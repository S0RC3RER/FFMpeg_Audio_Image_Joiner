import os
import time
# from queue import Queue
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QFileDialog, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, \
    QListWidget


class ImageAudioCombiner(QThread):
    """
    A subclass of QThread that defines a thread for combining an image and one or more audio files into MP4 video files.
    The thread takes an image file, a queue of audio files, and an output folder as inputs. The run method of the
    thread iteratively pops an audio file from the queue and combines it with the image file using FFmpeg. The progress
    of the thread is reported as an integer between 0 and 100 through the progress_signal signal. When the thread
    finishes, the finished_signal signal is emitted. If an error occurs during the process, the error_signal signal
    is emitted with a message describing the error.
    """
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, image_file, audio_files, output_folder, parent=None):
        """
        :param image_file: Path to image file
        :type image_file: basestring
        :param audio_files: Path to audio file
        :type audio_files: basestring
        :param output_folder: Path to output folder
        :type output_folder: basestring
        :param parent:
        """
        super().__init__(parent)
        self.image_file = image_file
        self.audio_files = audio_files
        self.output_folder = output_folder
        self.paused = False

    def pause(self):
        """
        Pause the combination
        :return:
        """
        self.paused = True

    def unpause(self):
        """
        Unpause the combination
        :return:
        """
        self.paused = False

    def run(self):
        """
        # TODO
        :return:
        """
        if not os.path.exists(self.output_folder):
            try:
                os.makedirs(self.output_folder)
            except OSError as e:
                self.error_signal.emit(f"Error occurred while creating the output folder: {e}")
                return

        total_files = self.audio_files.qsize()
        current_file = 1

        while not self.audio_files.empty():
            if self.cancel:  # Check the cancel flag
                self.finished_signal.emit()
                return  # Exit the loop

            if self.paused:
                time.sleep(0.5)
                continue

            audio_file = self.audio_files.get()
            output_file = os.path.join(self.output_folder, os.path.splitext(os.path.basename(audio_file))[0] + ".mp4")

            if not os.path.isfile(self.image_file):
                self.error_signal.emit("Invalid image file path.")
                return

            if not os.path.isfile(audio_file):
                self.error_signal.emit(f"Invalid audio file path: {audio_file}")
                return

            command = f'ffmpeg -loop 1 -i "{self.image_file}" -i "{audio_file}" -c:v libx264 -tune stillimage -c:a ' \
                      f'aac -b:a 192k -pix_fmt yuv420p -shortest "{output_file}"'
            os.system(command)

            if os.system(command) != 0:
                self.error_signal.emit(f"Error occurred while combining {audio_file}")
                return

            self.progress_signal.emit(int(current_file / total_files * 100))
            current_file += 1

        self.finished_signal.emit()


class MainWindow(QWidget):
    """
    A subclass of QWidget that defines the main window of the GUI application. The window contains several buttons and
    labels for selecting and displaying the image file, audio files, and output folder, as well as for starting,
    canceling, and monitoring the progress of the image and audio file combination process. The class also defines
    several methods for handling user interactions with the GUI components, such as selecting and removing files,
    updating the state of buttons, and launching and canceling the image and audio file combination thread.
    """
    def __init__(self):
        super().__init__()
        self.image_file = ""
        self.audio_files = []
        self.output_folder = ""
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Image selection button
        image_button = QPushButton("Select Image File")
        image_button.clicked.connect(self.select_image_file)
        layout.addWidget(image_button)

        # Image path label
        self.image_label = QLabel("No image file selected.")
        layout.addWidget(self.image_label)

        # Image remove button
        self.image_remove_button = QPushButton("Remove Image File")
        self.image_remove_button.clicked.connect(self.remove_image_file)
        self.image_remove_button.setEnabled(False)
        layout.addWidget(self.image_remove_button)

        # Audio selection button
        audio_button = QPushButton("Select Audio Files")
        audio_button.clicked.connect(self.select_audio_files)
        layout.addWidget(audio_button)

        # Audio files list
        audio_label = QLabel("Audio files:")
        layout.addWidget(audio_label)
        self.audio_list = QListWidget()
        self.audio_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.audio_list.itemSelectionChanged.connect(self.update_audio_remove_button)
        layout.addWidget(self.audio_list)

        # Audio remove button
        self.audio_remove_button = QPushButton("Remove Selected Audio Files")
        self.audio_remove_button.clicked.connect(self.remove_selected_audio_files)
        self.audio_remove_button.setEnabled(False)
        layout.addWidget(self.audio_remove_button)

        # Output selection button
        output_button = QPushButton("Select Output Folder")
        output_button.clicked.connect(self.select_output_folder)
        layout.addWidget(output_button)

        # Combine button
        combine_button = QPushButton("Combine")
        combine_button.clicked.connect(self.combine)
        layout.addWidget(combine_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel)
        cancel_button.setEnabled(False)
        layout.addWidget(cancel_button)
        self.cancel_button = cancel_button

        self.progress_label = QLabel("Progress: 0%")
        layout.addWidget(self.progress_label)

        self.setLayout(layout)
        self.setWindowTitle("Image Audio Combiner")
        self.show()

    def update_audio_remove_button(self):
        """
        A method of the MainWindow class that updates the state of the "Remove Selected Audio Files" button based on
        whether any audio files are currently selected in the audio file list.
        :return: None
        """
        selected_items = self.audio_list.selectedItems()
        if selected_items:
            self.audio_remove_button.setEnabled(True)
        else:
            self.audio_remove_button.setEnabled(False)

    def remove_image_file(self):
        """
        A method of the MainWindow class that removes the currently selected image file and updates the corresponding
        label and button state accordingly.
        :return: None
        """
        self.image_file = ""
        self.image_label.setText("No image file selected.")
        self.image_remove_button.setEnabled(False)

    def remove_selected_audio_files(self):
        """
        A method of the MainWindow class that removes the currently selected audio files from the audio file list and
        updates the corresponding button state accordingly.
        :return:
        """
        selected_items = self.audio_list.selectedItems()
        for item in selected_items:
            self.audio_files.remove(item.text())
            self.audio_list.takeItem(self.audio_list.row(item))
        self.update_audio_remove_button()

    def select_image_file(self):
        """
        A method of the MainWindow class that opens a file dialog for selecting an image file and updates the
        corresponding label and button state accordingly.
        :return:
        """
        image_file, _ = QFileDialog.getOpenFileName(self, "Select Image File", "",
                                                    "Image Files (*.jpg *.jpeg *.png *.bmp)")
        if image_file:
            if not os.path.isfile(image_file):
                QMessageBox.critical(self, "Error", "Invalid image file path.")
                return
            self.image_file = image_file
            self.image_label.setText(image_file)
            self.image_remove_button.setEnabled(True)

    def select_audio_files(self):
        """
        A method of the MainWindow class that opens a file dialog for selecting one or more audio files and updates the
        corresponding list and button state accordingly.
        :return:
        """
        audio_files, _ = QFileDialog.getOpenFileNames(self, "Select Audio Files", "", "Audio Files (*.mp3 *.wav *.ogg)")
        if audio_files:
            self.audio_files.extend(audio_files)
            for audio_file in audio_files:
                self.audio_list.addItem(audio_file)

    def select_output_folder(self):
        """
        A method of the MainWindow class that opens a file dialog for selecting an output folder for the combined video
        files and updates the corresponding label and button state accordingly.
        :return:
        """
        output_folder, _ = QFileDialog.getExistingDirectory(self, "Save Output Folder", "")
        if output_folder:
            self.output_folder = output_folder

    def combine(self):
        """
        A method of the MainWindow class that creates an instance of the ImageAudioCombiner thread with the selected
        image file, audio files, and output folder as inputs, connects its signals to the corresponding GUI components,
        and starts the thread.
        :return:
        """
        if not self.image_file:
            self.image_label.setText("No image file selected.")
            return
        if not self.audio_files:
            self.audio_list.addItem("No audio files selected.")
            return
        if not self.output_folder:
            return
        self.combine_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.cancel_button.setEnabled(True)  # Enable the cancel button

        self.image_label.setEnabled(False)
        self.image_remove_button.setEnabled(False)
        self.audio_list.setEnabled(False)
        self.audio_remove_button.setEnabled(False)
        self.output_folder.setEnabled(False)

        self.progress_label.setText("Progress: 0%")

        self.thread = ImageAudioCombiner(self.image_file, self.audio_files, self.output_folder,
                                         cancel=False)  # Set cancel flag to False
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.finished_signal.connect(self.finished)
        self.thread.error_signal.connect(self.handle_error)
        self.thread.start()

    def cancel(self):
        """
        A method of the MainWindow class that sets a flag to cancel the currently running ImageAudioCombiner thread,
        disables the "Combine" button, and enables the "Cancel" button.
        :return: None
        """
        self.cancel_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.combine_button.setEnabled(True)
        self.image_label.setEnabled(True)
        self.image_remove_button.setEnabled(True)
        self.audio_list.setEnabled(True)
        self.audio_remove_button.setEnabled(True)
        self.output_folder.setEnabled(True)
        self.progress_label.setText("Cancelled.")
        self.thread.pause()

    def update_progress_label(self, progress):
        """
        :param progress: progress percentage
        :type progress: int
        :return: None
        """
        self.progress_label.setText(f"Progress: {progress}%")

    def pause(self):
        """
        :return:None
        """
        if not self.combiner_thread:
            return

        if self.pause_button.text() == "Pause":
            self.combiner_thread.pause()
            self.pause_button.setText("Resume")
        else:
            self.combiner_thread.unpause()
            self.pause_button.setText("Pause")

    def combine_finished(self):
        """
        :return:
        """
        self.combine_button.setEnabled(True)
        self.pause_button.setEnabled(False)

        self.image_label.setEnabled(True)
        self.image_remove_button.setEnabled(True)
        self.audio_list.setEnabled(True)
        self.audio_remove_button.setEnabled(True)
        self.output_folder.setEnabled(True)

        self.progress_label.setText("Progress: 100%")

    def handle_error(self, message):
        """
        :param message: error message
        :type message: basestring
        :return:
        """
        QMessageBox.warning(self, "Error", message)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec()

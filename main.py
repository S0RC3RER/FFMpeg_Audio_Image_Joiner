import os
import time
# from queue import Queue
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QFileDialog, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QListWidget


class ImageAudioCombiner(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, image_file, audio_files, output_folder, parent=None):
        super().__init__(parent)
        self.image_file = image_file
        self.audio_files = audio_files
        self.output_folder = output_folder
        self.paused = False

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def run(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        total_files = self.audio_files.qsize()
        current_file = 1

        while not self.audio_files.empty():
            if self.paused:
                time.sleep(0.5)
                continue

            audio_file = self.audio_files.get()
            output_file = os.path.join(self.output_folder, os.path.splitext(os.path.basename(audio_file))[0] + ".mp4")

            command = f'ffmpeg -loop 1 -i "{self.image_file}" -i "{audio_file}" -c:v libx264 -tune stillimage -c:a ' \
                      f'aac -b:a 192k -pix_fmt yuv420p -shortest "{output_file}"'
            os.system(command)

            self.progress_signal.emit(int(current_file / total_files * 100))
            current_file += 1

        self.finished_signal.emit()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.image_file = ""
        self.audio_files = []
        self.output_file = ""
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
        output_button = QPushButton("Select Output File")
        output_button.clicked.connect(self.select_output_file)
        layout.addWidget(output_button)

        # Combine button
        combine_button = QPushButton("Combine")
        combine_button.clicked.connect(self.combine)
        layout.addWidget(combine_button)

        self.progress_label = QLabel("Progress: 0%")
        layout.addWidget(self.progress_label)

        self.setLayout(layout)
        self.setWindowTitle("Image Audio Combiner")
        self.show()

    def update_audio_remove_button(self):
        selected_items = self.audio_list.selectedItems()
        if selected_items:
            self.audio_remove_button.setEnabled(True)
        else:
            self.audio_remove_button.setEnabled(False)

    def remove_image_file(self):
        self.image_file = ""
        self.image_label.setText("No image file selected.")
        self.image_remove_button.setEnabled(False)

    def remove_selected_audio_files(self):
        selected_items = self.audio_list.selectedItems()
        for item in selected_items:
            self.audio_files.remove(item.text())
            self.audio_list.takeItem(self.audio_list.row(item))
        self.update_audio_remove_button()

    def select_image_file(self):
        image_file, _ = QFileDialog.getOpenFileName(self, "Select Image File", "",
                                                    "Image Files (*.jpg *.jpeg *.png *.bmp)")
        if image_file:
            self.image_file = image_file
            self.image_label.setText(image_file)
            self.image_remove_button.setEnabled(True)

    def select_audio_files(self):
        audio_files, _ = QFileDialog.getOpenFileNames(self, "Select Audio Files", "", "Audio Files (*.mp3 *.wav *.ogg)")
        if audio_files:
            self.audio_files.extend(audio_files)
            for audio_file in audio_files:
                self.audio_list.addItem(audio_file)

    def select_output_file(self):
        output_file, _ = QFileDialog.getSaveFileName(self, "Save Output File", "", "Video Files (*.mp4)")
        if output_file:
            self.output_file = output_file

    def combine(self):
        if not self.image_file:
            self.image_label.setText("No image file selected.")
            return
        if not self.audio_files:
            self.audio_list.addItem("No audio files selected.")
            return
        if not self.output_file:
            return
        self.combine_button.setEnabled(False)
        self.pause_button.setEnabled(True)

        self.image_label.setEnabled(False)
        self.image_remove_button.setEnabled(False)
        self.audio_list.setEnabled(False)
        self.audio_remove_button.setEnabled(False)
        self.output_folder.setEnabled(False)

        self.progress_label.setText("Progress: 0%")

        self.combiner_thread = ImageAudioCombiner(self.image_file, self.audio_files, self.output_folder)
        self.combiner_thread.progress_signal.connect(self.update_progress_label)
        self.combiner_thread.finished_signal.connect(self.combine_finished)
        self.combiner_thread.start()

    def update_progress_label(self, progress):
        self.progress_label.setText(f"Progress: {progress}%")

    def pause(self):
        if not self.combiner_thread:
            return

        if self.pause_button.text() == "Pause":
            self.combiner_thread.pause()
            self.pause_button.setText("Resume")
        else:
            self.combiner_thread.unpause()
            self.pause_button.setText("Pause")

    def combine_finished(self):
        self.combine_button.setEnabled(True)
        self.pause_button.setEnabled(False)

        self.image_label.setEnabled(True)
        self.image_remove_button.setEnabled(True)
        self.audio_list.setEnabled(True)
        self.audio_remove_button.setEnabled(True)
        self.output_folder.setEnabled(True)

        self.progress_label.setText("Progress: 100%")


def combine_audio_and_image(image_file, audio_files, output_file):
    audio_str = ""
    for audio_file in audio_files:
        audio_str += f"-i {audio_file} "
    cmd = f"ffmpeg -loop 1 -i {image_file} {audio_str} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt " \
          f"yuvj420p -shortest {output_file}"
    os.system(cmd)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec()

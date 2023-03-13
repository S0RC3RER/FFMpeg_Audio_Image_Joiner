import os
from PyQt6.QtWidgets import QApplication, QFileDialog, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QListWidget


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

        # Audio selection button
        audio_button = QPushButton("Select Audio Files")
        audio_button.clicked.connect(self.select_audio_files)
        layout.addWidget(audio_button)

        # Output selection button
        output_button = QPushButton("Select Output File")
        output_button.clicked.connect(self.select_output_file)
        layout.addWidget(output_button)

        # Image path label
        self.image_label = QLabel("No image file selected.")
        layout.addWidget(self.image_label)

        # Audio files list
        audio_label = QLabel("Audio files:")
        layout.addWidget(audio_label)
        self.audio_list = QListWidget()
        layout.addWidget(self.audio_list)

        # Combine button
        combine_button = QPushButton("Combine")
        combine_button.clicked.connect(self.combine)
        layout.addWidget(combine_button)

        self.setLayout(layout)
        self.show()

    def select_image_file(self):
        image_file, _ = QFileDialog.getOpenFileName(self, "Select Image File", "",
                                                    "Image Files (*.jpg *.jpeg *.png *.bmp)")
        if image_file:
            self.image_file = image_file
            self.image_label.setText(image_file)

    def select_audio_files(self):
        audio_files, _ = QFileDialog.getOpenFileNames(self, "Select Audio Files", "", "Audio Files (*.mp3 *.wav *.ogg)")
        if audio_files:
            self.audio_files = audio_files
            self.audio_list.clear()
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
        combine_audio_and_image(self.image_file, self.audio_files, self.output_file)


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

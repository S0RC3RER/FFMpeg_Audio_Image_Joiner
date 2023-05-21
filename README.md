# FFMpeg_Audio_Image_Joiner

This Python program allows you to combine an image file with one or more audio files and create MP4 video files. The program provides a graphical user interface (GUI) built using PyQt6.

## Features

- Select an image file to be combined with the audio files.
- Select one or more audio files to be combined with the image file.
- Choose an output folder where the combined video files will be saved.
- Start the combination process.
- Monitor the progress of the combination process.
- Handle errors during the combination process.

## Dependencies

The program requires the following dependencies:

- PyQt6: The Python binding for the Qt framework.
- PIL: The Python Imaging Library for image manipulation.
- FFMpeg: The command-line tool for video and audio processing.

## How to Use

1. Install the dependencies by running the following command:
   ```
   pip install PyQt6 pillow
   ```
   Make sure FFMpeg is installed and added to the system's PATH.

2. Run the program using Python:
   ```
   python program.py
   ```

3. The program will open a GUI window with several buttons and labels.

4. Click on the "Select Image File" button to choose an image file.

5. Click on the "Select Audio Files" button to select one or more audio files.

6. Click on the "Select Output Folder" button to choose the folder where the combined video files will be saved.

7. Click on the "Combine" button to start the combination process.

8. The progress of the combination process will be displayed in the progress label.

9. Once the combination is complete, a message will be shown indicating the success.

10. The output folder will open automatically, and you can find the combined video files there.

## Notes

- Supported image file formats: JPEG, PNG, BMP.
- Supported audio file formats: MP3, WAV, OGG.
- The combined video files will be saved in MP4 format.
- Make sure the image file, audio files, and output folder paths are valid.
- If any errors occur during the combination process, an error message will be shown.

Feel free to explore and modify the program according to your needs.

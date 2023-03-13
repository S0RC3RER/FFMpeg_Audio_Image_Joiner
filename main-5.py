import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import ffmpeg
import os
import threading
import multiprocessing


# def combine_audio_and_image_broken(image_file, audio_file, output_file):
#     ffmpeg_command = ffmpeg.input(image_file, loop=1)
#     ffmpeg_command = ffmpeg_command.input(audio_file)
#     ffmpeg_command = ffmpeg_command.output(output_file,
#                                            c='libx264',
#                                            tune='stillimage',
#                                            a='aac',
#                                            b='192k',
#                                            pix_fmt='yuvj420p',
#                                            shortest=True)
#     ffmpeg_command.run()


def combine_audio_and_image(image_file, audio_file, output_file):
    cmd = f"ffmpeg -loop 1 -i {image_file} -i {audio_file} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt " \
          f"yuvj420p -shortest {output_file}"
    os.system(cmd)


# def combine_audio_image(image_file, audio_file, output_file):
#     (
#         ffmpeg
#         .input(image_file, loop=1)
#         .input(audio_file)
#         .output(output_file, c='libx264', tune='stillimage', a='aac', b='192k', pix_fmt='yuvj420p', shortest=True)
#         .run()
#     )


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.select_image = tk.Button(self)
        self.select_image["text"] = "Select Image"
        self.select_image["command"] = self.select_image_command
        self.select_image.pack()

        self.select_audio = tk.Button(self)
        self.select_audio["text"] = "Select Audio"
        self.select_audio["command"] = self.select_audio_command
        self.select_audio.pack()

        self.combine = tk.Button(self)
        self.combine["text"] = "Combine"
        self.combine["command"] = self.combine_command
        self.combine.pack()

        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="indeterminate")
        self.progress.pack()

    def select_image_command(self):
        # self.image_file = filedialog.askopenfilename(initialdir=".", title="Select Image",
        #                                              filetypes=(("JPEG Files", "*.jpg"), ("PNG Files", "*.png")))
        self.image_file = "C:/Users/lower/Pictures/CCI01232023_even_dimensions.jpg"
        print(f"Image Selected: {self.image_file}")

    def select_audio_command(self):
        # self.audio_file = filedialog.askopenfilename(initialdir=".", title="Select Audio",
        #                                              filetypes=(("WAV Files", "*.wav"), ("MP3 Files", "*.mp3")))
        self.audio_file = "C:/Users/lower/Downloads/wnDjLhRaUhpA_160_(enhanced).wav"
        print(f"Audio Selected: {self.audio_file}")

    def combine_command(self):
        self.progress.start()
        # self.output_file = filedialog.asksaveasfilename(initialdir=".", title="Save Video",
        #                                                 filetypes=(("MP4 Files", "*.mp4"), ("AVI Files", "*.avi")))
        self.output_file = "C:/Users/lower/Videos/test.mp4"
        # combine_audio_image(self.image_file, self.audio_file, self.output_file)
        combine_audio_and_image(self.image_file, self.audio_file, self.output_file)
        self.progress.stop()
        print(f"Video Created: {self.output_file}")


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

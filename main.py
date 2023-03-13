import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import ffmpeg
from PIL import Image, ImageTk


# TODO - Modify this function to use new implementation
def combine_audio_image(image_file, audio_files, output_file):
    audio_inputs = [ffmpeg.input(f) for f in audio_files]
    (
        ffmpeg
        .concat(*audio_inputs, v=1, a=1)
        .input(image_file, loop=1)
        .output(output_file, **{'c:v':'libx264'}, tune='stillimage', **{'c:a': 'aac'}, b='192k', pix_fmt='yuv420p', shortest=True)
        .global_args('-loglevel', 'error')
        .global_args('-report')
        .run()
    )


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

        self.image_frame = tk.Frame(self)
        self.image_frame.pack()
        self.image_path = tk.Label(self.image_frame)
        self.image_path.pack(side="left")
        self.remove_image = tk.Button(self.image_frame)
        self.remove_image["text"] = "Remove"
        self.remove_image["command"] = self.remove_image_command
        self.remove_image.pack(side="right")

        self.image_preview = tk.Label(self)
        self.image_preview.pack()

        self.select_audio = tk.Button(self)
        self.select_audio["text"] = "Select Audio"
        self.select_audio["command"] = self.select_audio_command
        self.select_audio.pack()

        self.audio_list = tk.Listbox(self)
        self.audio_list.pack(fill="both", expand=True)
        self.audio_list.bind("<Double-Button-1>", self.remove_audio_command)

        self.remove_audio = tk.Button(self)
        self.remove_audio["text"] = "Remove Audio"
        self.remove_audio["command"] = self.remove_audio_command
        self.remove_audio.pack()

        self.combine = tk.Button(self)
        self.combine["text"] = "Combine"
        self.combine["command"] = self.combine_command
        self.combine.pack()

        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="indeterminate")
        self.progress.pack()

    def select_image_command(self):
        self.image_file = filedialog.askopenfilename(initialdir=".", title="Select Image", filetypes=(
            ("Image files", "*.jpg;*.png;*.jpeg"), ("All files", "*.*")))
        if self.image_file:
            self.image_path["text"] = self.image_file
            image = Image.open(self.image_file)
            image = image.resize((300, 300), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)
            self.image_preview["image"] = image
            self.image_preview.photo = image

    def remove_image_command(self):
        self.image_file = None
        self.image_path["text"] = ""
        self.image_preview["image"] = ""

    def select_audio_command(self):
        audio_file = filedialog.askopenfilename(initialdir=".", title="Select Audio", multiple=True, filetypes=(
            ("Audio files", "*.wav;*.mp3;*.aac"), ("All files", "*.*")))
        if audio_file:
            for file in audio_file:
                self.audio_list.insert("end", file)

    def remove_audio_command(self, event=None):
        selected = self.audio_list.curselection()
        for index in selected:
            self.audio_list.delete(index)

    def combine_command(self):
        if not self.image_file:
            messagebox.showerror("Error", "Please select an image.")
            return
        if self.audio_list.size() == 0:
            messagebox.showerror("Error", "Please select audio files.")
            return
        audio_files = [self.audio_list.get(i) for i in range(self.audio_list.size())]
        output_file = filedialog.asksaveasfilename(initialdir=".", title="Save Video",
                                                   filetypes=(("Video files", "*.mp4"), ("All files", "*.*")),
                                                   defaultextension=".mp4")
        if not output_file:
            return
        self.progress.start()
        combine_audio_image(self.image_file, audio_files, output_file)
        self.progress.stop()
        messagebox.showinfo("Info", "Video created successfully.")


if __name__ == "__main__":
    app = Application()
    app.mainloop()

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import ffmpeg
import concurrent.futures


class Application(tk.Tk):
    """
    The main GUI class for the application
    """

    def __init__(self):
        """
        Initialize the tkinter window and create widgets
        """
        super().__init__()
        self.title("Audio to Video Combiner")
        self.geometry("600x450")
        self.create_widgets()

    def create_widgets(self):
        """
        Creates three buttons: 'Select Image', 'Select Audio', 'Combine'
        A label to display the selected image file path and name
        A preview of the selected image
        A scrollable list to display the selected audio files
        A progress bar to display the progress of the video creation process
        """
        # Select Image Button
        select_image = tk.Button(self, text="Select Image", command=self.select_image_command)
        select_image.pack()

        # Label to display the selected image file path and name
        self.image_path = tk.Label(self, text="", anchor="w")
        self.image_path.pack()

        # Preview of the selected image
        self.image_preview = tk.Label(self, width=300, height=300)
        self.image_preview.pack()

        # Remove Image Button
        remove_image = tk.Button(self, text="Remove Image", command=self.remove_image_command)
        remove_image.pack()

        # Select Audio Button
        select_audio = tk.Button(self, text="Select Audio", command=self.select_audio_command)
        select_audio.pack()

        # Scrollable list to display the selected audio files
        self.audio_list = tk.Listbox(self, selectmode="multiple")
        self.audio_list.pack(fill="both", expand=True)

        # Remove Audio Button
        remove_audio = tk.Button(self, text="Remove Audio", command=self.remove_audio_command)
        remove_audio.pack()

        # Combine Button
        combine = tk.Button(self, text="Combine", command=self.combine_command)
        combine.pack()

        # Progress bar to display the progress of the video creation process
        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="indeterminate")
        self.progress.pack()

    def select_image_command(self):
        """
        Opens a file dialog to select an image
        Displays the file path and name of the selected image
        Displays a preview of the selected image
        """
        self.image_file = filedialog.askopenfilename(initialdir=".", title="Select Image", filetypes=(
            ("Image files", "*.jpg;*.png;*.jpeg"), ("All files", "*.*")))
        if self.image_file:
            self.image_path["text"] = self.image_file

            # Display a preview of the selected image
            image = Image.open(self.image_file)
            image = image.resize((300, 300), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)
            self.image_preview["image"] = image

    def remove_image_command(self):
        """
        Removes the selected image
        """
        self.image_file = None
        self.image_path["text"] = ""
        self.image_preview["image"] = ""

    def select_audio_command(self):
        """
        Opens a file dialog to select one or more audio files
        Adds the selected audio files to the scrollable list
        """
        audio_files = filedialog.askopenfilenames(initialdir=".", title="Select Audio", filetypes=(
            ("Audio files", "*.wav;*.mp3;*.aac"), ("All files", "*.*")))
        if audio_files:
            for audio_file in audio_files:
                self.audio_list.insert("end", audio_file)

    def remove_audio_command(self):
        """
        Removes the selected audio files from the scrollable list
        """
        selected_items = self.audio_list.curselection()
        for item in selected_items:
            self.audio_list.delete(item)

    def combine_command(self):
        """
        Combines multiple audios and image asynchronously using ffmpeg-python library
        Output videos keep the same name as the input audio
        Displays a message box indicating if the process was successful or not
        """
        if not self.image_file:
            messagebox.showerror("Error", "Please select an image")
            return
        if not self.audio_list.get(0, "end"):
            messagebox.showerror("Error", "Please select at least one audio file")
            return

        self.progress.start()
        try:
            futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for audio in self.audio_list.get(0, "end"):
                    inputs = [
                        ffmpeg.input(self.image_file, loop=1),
                        ffmpeg.input(audio),
                    ]
                    audio_name = audio.split("/")[-1].split(".")[0]
                    output_file = "{}.mp4".format(audio_name)
                    future = executor.submit(ffmpeg.output, inputs, output_file, c="libx264", tune="stillimage",
                                             a="aac", b="192k", pix_fmt="yuv420p", short="shortest").run
                    futures.append(future)
                    for future in concurrent.futures.as_completed(futures):
                        future.result()
                    messagebox.showinfo("Success", "Videos have been created successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.progress.stop()


app = Application()
app.mainloop()

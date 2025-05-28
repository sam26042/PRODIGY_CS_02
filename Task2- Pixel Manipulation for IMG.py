import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class ImageEncryptorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Simple Image Encryption tool")
        self.master.geometry("900x600")
        self.master.configure(bg="#222")

        # Encryption key for XOR operation (0-255)
        self.key = 123

        self.original_img = None
        self.processed_img = None  # encrypted or decrypted image
        self.tk_original_img = None
        self.tk_processed_img = None

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self.master, text="Simple Image Encryption Tool", font=("Arial", 30), fg="#ff4081", bg="#222")
        title.pack(pady=10)

        # Frame for buttons
        button_frame = tk.Frame(self.master, bg="#222")
        button_frame.pack(pady=10)

        load_btn = tk.Button(button_frame, text="Load Image", font=("Arial", 16), bg="#ff4081", fg="white", command=self.load_image)
        load_btn.grid(row=0, column=0, padx=5)

        encrypt_btn = tk.Button(button_frame, text="Encrypt", font=("Arial", 16), bg="#4caf50", fg="white", command=self.encrypt_image)
        encrypt_btn.grid(row=0, column=1, padx=5)

        decrypt_btn = tk.Button(button_frame, text="Decrypt", font=("Arial", 16), bg="#f44336", fg="white", command=self.decrypt_image)
        decrypt_btn.grid(row=0, column=2, padx=5)

        save_btn = tk.Button(button_frame, text="Save Image", font=("Arial", 16), bg="#2196f3", fg="white", command=self.save_image)
        save_btn.grid(row=0, column=3, padx=5)

        # Frame for images
        images_frame = tk.Frame(self.master, bg="#222")
        images_frame.pack(pady=10)

        # Original Image
        orig_label = tk.Label(images_frame, text="Original Image", font=("Arial", 20), fg="#ff4081", bg="#222")
        orig_label.grid(row=0, column=0, padx=20)
        self.orig_canvas = tk.Canvas(images_frame, width=400, height=400, bg="black", highlightthickness=0)
        self.orig_canvas.grid(row=1, column=0, padx=20)

        # Processed Image (encrypted/decrypted)
        proc_label = tk.Label(images_frame, text="Encrypted / Decrypted Image", font=("Arial", 20), fg="#ff4081", bg="#222")
        proc_label.grid(row=0, column=1, padx=20)
        self.proc_canvas = tk.Canvas(images_frame, width=400, height=400, bg="black", highlightthickness=0)
        self.proc_canvas.grid(row=1, column=1, padx=20)

        # Key input
        key_frame = tk.Frame(self.master, bg="#222")
        key_frame.pack(pady=10)

        key_label = tk.Label(key_frame, text="Encryption Key (0-255):", font=("Arial", 16), fg="white", bg="#222")
        key_label.pack(side=tk.LEFT, padx=5)

        self.key_entry = tk.Entry(key_frame, font=("Arial", 16), width=5, bg="#333", fg="white")
        self.key_entry.insert(0, "123")  # Default key
        self.key_entry.pack(side=tk.LEFT, padx=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if not file_path:
            return
        try:
            img = Image.open(file_path).convert("RGB")
            self.original_img = img
            self.processed_img = None
            self.display_image(img, self.orig_canvas, "orig")
            self.proc_canvas.delete("all")
            messagebox.showinfo("Success", "Image loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def display_image(self, pil_img, canvas, image_type):
        # Resize image to fit canvas while keeping aspect ratio
        w, h = pil_img.size
        max_w, max_h = 400, 400
        ratio = min(max_w / w, max_h / h)
        new_size = (int(w * ratio), int(h * ratio))
        resized_img = pil_img.resize(new_size, Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(resized_img)
        canvas.delete("all")
        canvas.create_image(max_w // 2, max_h // 2, image=tk_img, anchor="center")
        # Keep reference to avoid garbage collection
        if image_type == "orig":
            self.tk_original_img = tk_img
        else:
            self.tk_processed_img = tk_img

    def encrypt_image(self):
        if self.original_img is None:
            messagebox.showwarning("Warning", "Please load an image first.")
            return
        try:
            self.key = int(self.key_entry.get())
            if not (0 <= self.key <= 255):
                raise ValueError("Key must be between 0 and 255.")
        except ValueError:
            messagebox.showwarning("Warning", "Invalid key. Please enter a number between 0 and 255.")
            return

        img_array = np.array(self.original_img)
        encrypted_array = self.simple_encrypt(img_array)
        self.processed_img = Image.fromarray(encrypted_array)
        self.display_image(self.processed_img, self.proc_canvas, "proc")
        messagebox.showinfo("Encryption", "Image encrypted successfully.")

    def decrypt_image(self):
        if self.processed_img is None:
            messagebox.showwarning("Warning", "Please encrypt an image first.")
            return
        img_array = np.array(self.processed_img)
        decrypted_array = self.simple_decrypt(img_array)
        decrypted_img = Image.fromarray(decrypted_array)
        self.processed_img = decrypted_img
        self.display_image(decrypted_img, self.proc_canvas, "proc")
        messagebox.showinfo("Decryption", "Image decrypted successfully.")

    def save_image(self):
        if self.processed_img is None:
            messagebox.showwarning("Warning", "No encrypted or decrypted image to save.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
        if save_path:
            try:
                self.processed_img.save(save_path)
                messagebox.showinfo("Success", "Image saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{e}")

    def simple_encrypt(self, img_array):
        # Swap pixels horizontally pairwise and XOR each channel with key
        encrypted = img_array.copy()
        h, w, c = encrypted.shape

        # Swap pixels pairwise in each row for width-1 pixels
        for row in range(h):
            for col in range(0, w - 1, 2):
                # Swap pixel at col with pixel at col+1 for all channels
                encrypted[row, col], encrypted[row, col + 1] = encrypted[row, col + 1].copy(), encrypted[row, col].copy()

        # XOR each pixel channel with the key
        encrypted = np.bitwise_xor(encrypted, self.key)

        return encrypted

    def simple_decrypt(self, img_array):
        # Reverse XOR and swap pixels back
        decrypted = img_array.copy()

        # XOR again with key (XOR is its own inverse)
        decrypted = np.bitwise_xor(decrypted, self.key)

        h, w, c = decrypted.shape

        # Swap pixels pairwise in each row back to original
        for row in range(h):
            for col in range(0, w - 1, 2):
                decrypted[row, col], decrypted[row, col + 1] = decrypted[row, col + 1].copy(), decrypted[row, col].copy()

        return decrypted

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEncryptorApp(root)
    root.mainloop()

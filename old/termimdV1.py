import os
import cv2
from tkinter import filedialog
from PIL import Image
from colorama import Fore, Style
import time

def load_images(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    return [os.path.join(folder_path, image) for image in sorted(image_files)]

def decrypt_video(video_path, output_folder):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img.save(os.path.join(output_folder, f"frame_{i:06d}.png"))

    cap.release()

    return fps

def display_image(image_path):
    with Image.open(image_path) as img:
        img = img.convert("L")
        img = img.resize((100, 40))  # Adjust size as needed
        pixels = list(img.getdata())
        width, height = img.size
        imgtxt = ''
        for i in range(0, len(pixels), width):
            row = pixels[i:i+width]
            row_chars_list = [get_char(value) for value in row]
            row_chars = ''
            for c in row_chars_list:
                row_chars += c
            imgtxt += row_chars + '\n'
        print('\033[2J' + imgtxt)

def get_char(pixel_value):
    chars = "@%#*+=-:. "
    index = min(pixel_value // (256 // len(chars)), len(chars) - 1)
    return chars[index]

def remove_temp_images(folder_path):
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            os.remove(os.path.join(folder_path, file))

if __name__ == "__main__":
    video_path = filedialog.askopenfilename()
    output_folder = ".tmp_images"

    if not os.path.exists(video_path):
        print(f"The specified video path '{video_path}' does not exist.")
    else:
        print('Proccessing images now')
        fps = decrypt_video(video_path, output_folder)
        image_paths = load_images(output_folder)

        for image_path in image_paths:
            display_image(image_path)
            time.sleep(1 / fps)
            
        remove_temp_images(output_folder)
        print('\033[2JDone, Thanks for watching')


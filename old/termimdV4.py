#4 sec buffer at end
import os
import cv2
from tkinter import filedialog
from PIL import Image
import time
import threading
from moviepy.editor import VideoFileClip

def load_images(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    return [os.path.join(folder_path, image) for image in sorted(image_files)]

def decrypt_video(video_path, image_list):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image_list.append(img)

    cap.release()

    return fps

def display_image(img):
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
        if file.lower().endswith('.png'):
            os.remove(os.path.join(folder_path, file))

def play_audio(video_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.preview()
    video_clip.close()   

if __name__ == "__main__":
    video_path = filedialog.askopenfilename()
    output_images = []

    if not os.path.exists(video_path):
        print(f"The specified video path '{video_path}' does not exist.")
    else:
        print('Processing video now')
        fps = decrypt_video(video_path, output_images)
        print(f'Fps: {fps}\nLoading images now')
        print('Images loaded\nLoading audio')
        audio_thread = threading.Thread(target=play_audio, args=(video_path,))
        print('START')
        time.sleep(1)
        audio_thread.start()

        threads = []
        for img in output_images:
            thread = threading.Thread(target=display_image, args=(img,))
            threads.append(thread)
            thread.start()
            time.sleep(1 / fps)
            
        for thread in threads:
            thread.join()
        audio_thread.join()
        
        print('\033[2JDone, Thanks for watching')


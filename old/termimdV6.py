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
    
def decrypt_video_opt(video_path, image_list, col, lin):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = img.convert("L")
        img = img.resize((col-3, lin-3))
        pixels = list(img.getdata())
        width, height = img.size
        imgtxt = ''
        for i in range(0, len(pixels), width):
            row = pixels[i:i+width]
            row_chars_list = [get_char(value) for value in row]
            row_chars = '  '
            for c in row_chars_list:
                row_chars += c
            imgtxt += row_chars + '\n'
        image_list.append(imgtxt)
    cap.release()
    return fps

def display_image_in_thread_opt(img, fps, start_time):
    print('\033[2J' + img)
    elapsed_time = time.perf_counter() - start_time
    sleep_duration = max(0, 1 / fps - elapsed_time)
    time.sleep(sleep_duration)

def display_image_in_thread(img, fps, start_time):
    display_image(img)
    elapsed_time = time.perf_counter() - start_time
    sleep_duration = max(0, 1 / fps - elapsed_time)
    time.sleep(sleep_duration)
    
def display_image(img):
    img = img.convert("L")
    terminal_size = os.get_terminal_size()
    
    
    img = img.resize((terminal_size.columns-3, terminal_size.lines-3))
    pixels = list(img.getdata())
    width, height = img.size
    imgtxt = ''
    for i in range(0, len(pixels), width):
        row = pixels[i:i+width]
        row_chars_list = [get_char(value) for value in row]
        row_chars = '  '
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
    cpuOpt1 = input('Would you like to use resource optimized? Dynamic terminal sizing will no longer be available. (y/n): ')
    cpuOpt = cpuOpt1 == 'y' or cpuOpt1 == 'Y'
    video_path = filedialog.askopenfilename()
    output_images = []

    terminal_size = os.get_terminal_size()
    print("Terminal size: {} columns x {} rows".format(terminal_size.columns, terminal_size.lines))

    if not os.path.exists(video_path):
        print(f"The specified video path '{video_path}' does not exist.")
    elif(cpuOpt):
        print('Processing video now')
        fps = decrypt_video_opt(video_path, output_images, terminal_size.columns, terminal_size.lines)
        print(f'Fps: {fps}\nImages loaded\nLoading audio')
        #audio_thread = threading.Thread(target=play_audio, args=(video_path,))
        print('START')
        time.sleep(1)
        #audio_thread.start()

        threads = []
        start_time = time.perf_counter()

        for img in output_images:
            thread = threading.Thread(target=display_image_in_thread_opt, args=(img, fps, start_time))
            threads.append(thread)
            thread.start()

            expected_start_time = start_time + 1 / fps
            time_to_sleep = max(0, expected_start_time - time.perf_counter())
            time.sleep(time_to_sleep)

            start_time = expected_start_time
            
        for thread in threads:
            thread.join()
        #audio_thread.join()
        
        print('\033[2JDone, Thanks for watching')
    else:
        print('Processing video now')
        fps = decrypt_video(video_path, output_images)
        print(f'Fps: {fps}\nLoading images now')
        print('Images loaded\nLoading audio')
        #audio_thread = threading.Thread(target=play_audio, args=(video_path,))
        print('START')
        time.sleep(1)
        #audio_thread.start()

        threads = []
        start_time = time.perf_counter()

        for img in output_images:
            thread = threading.Thread(target=display_image_in_thread, args=(img, fps, start_time))
            threads.append(thread)
            thread.start()

            expected_start_time = start_time + 1 / fps
            time_to_sleep = max(0, expected_start_time - time.perf_counter())
            time.sleep(time_to_sleep)

            start_time = expected_start_time
            
        for thread in threads:
            thread.join()
        #audio_thread.join()
        
        print('\033[2JDone, Thanks for watching')


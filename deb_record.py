import cv2
import tkinter as tk
from PIL import Image, ImageTk
import datetime
import threading
import queue

cam_inds = [0, 1] #Update the indices here

num_cameras = len(cam_inds)

# Global variables
recorders = []
is_recording = [False] * num_cameras
global_recording = False
root = None
streams = []
frame_queues = []

def camera_feed(camera_index):
    # Create a VideoCapture object for the camera
    cap = cv2.VideoCapture(cam_inds[camera_index])
    streams.append(cap)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame to desired dimensions
        frame = cv2.resize(frame, (640, 480))
        
        # Put the frame in the queue
        if not frame_queues[camera_index].full():
            frame_queues[camera_index].put(frame)

    cap.release()

def update_camera_feed(camera_index, video_label):
    def get_frame():
        if not frame_queues[camera_index].empty():
            frame = frame_queues[camera_index].get()
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)

            # Display the image in the label
            video_label.imgtk = imgtk  # Keep a reference
            video_label.configure(image=imgtk)

            if is_recording[camera_index]:
                recorders[camera_index].write(frame)

        # Schedule the next frame update
        video_label.after(10, get_frame)  # Update every 10 ms

    get_frame()  # Start the frame update loop

def toggle_recording(camera_index, button):
    global is_recording
    if not is_recording[camera_index]:
        start_recording(camera_index)
        button.configure(bg="red", text=f"Stop Camera {camera_index + 1}")
    else:
        stop_recording(camera_index)
        button.configure(bg="green", text=f"Start Camera {camera_index + 1}")
    is_recording[camera_index] = not is_recording[camera_index]

def start_recording(camera_index):
    global recorders
    # Ensure we only have one recorder per camera
    if len(recorders) <= camera_index:
        recorders.append(None)  # Initialize with None if not already present

    # Release the previous recorder if it exists
    if recorders[camera_index] is not None:
        recorders[camera_index].release()

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"camera_{camera_index + 1}_{start_time}.mp4"
    
    # Specify the frame size as (width, height)
    frame_size = (640, 480)  # Ensure this matches the resized dimensions
    recorder = cv2.VideoWriter(output_filename, fourcc=fourcc, fps=20.0, frameSize=frame_size)  # Initialize the recorder

    if not recorder.isOpened():
        print(f"Error: Could not open video writer for camera {camera_index + 1}")
        return
    
    recorders[camera_index] = recorder  # Save the recorder to the list

def stop_recording(camera_index):
    global recorders
    if recorders[camera_index] is not None:
        recorders[camera_index].release()
        recorders[camera_index] = None  # Reset to None after releasing
        print(f"Recording stopped for camera {camera_index + 1}")

def toggle_all_recordings():
    global global_recording
    if not global_recording:
        start_all_recordings()
        global_start_stop_button.configure(bg="red", text="Stop All Cameras")
    else:
        stop_all_recordings()
        global_start_stop_button.configure(bg="green", text="Start All Cameras")
    global_recording = not global_recording

def start_all_recordings():
    for i in range(num_cameras):
        if not is_recording[i]:
            start_recording(i)
            buttons[i].configure(bg="red", text=f"Stop Camera {i + 1}")
            is_recording[i] = True

def stop_all_recordings():
    for i in range(num_cameras):
        if is_recording[i]:
            stop_recording(i)
            buttons[i].configure(bg="green", text=f"Start Camera {i + 1}")
            is_recording[i] = False

def create_gui():
    global buttons, global_start_stop_button, root
    root = tk.Tk()
    root.title("Multi-Camera Recorder")
    root.geometry("1280x720")  # Set the window size larger for full-screen use

    buttons = []
    video_labels = []

    for i in range(num_cameras):
        video_label = tk.Label(root)
        video_label.grid(row=0, column=i, padx=10, pady=10)
        video_labels.append(video_label)

        button = tk.Button(root, text=f"Start Camera {i + 1}", bg="green",
                           command=lambda idx=i: toggle_recording(idx, buttons[idx]))
        button.grid(row=1, column=i, padx=10, pady=5)
        buttons.append(button)

        # Start the camera feed thread
        thread = threading.Thread(target=camera_feed, args=(i,))
        thread.daemon = True  # Allow thread to exit when main program exits
        thread.start()

        # Start updating the camera feed
        update_camera_feed(i, video_label)

    global_start_stop_button = tk.Button(root, text="Start All Cameras", bg="green", command=toggle_all_recordings)
    global_start_stop_button.grid(row=2, column=0, columnspan=num_cameras, pady=10)

    close_button = tk.Button(root, text="Close", bg="grey", command=close_application)
    close_button.grid(row=3, column=0, columnspan=num_cameras, pady=10)

    root.protocol("WM_DELETE_WINDOW", close_application)
    root.mainloop()

def close_application():
    stop_all_recordings()
    for cap in streams:
        cap.release()  # Stop the OpenCV streams
    cv2.destroyAllWindows()
    root.quit()

if __name__ == "__main__":
    # Create a queue for each camera to hold frames
    frame_queues = [queue.Queue(maxsize=10) for _ in range(num_cameras)]
    create_gui()

import cv2
import tkinter as tk
import datetime
import threading


num_cameras = 2  # Adjust this number based on the cameras you have

# Global variables
recorders = []
is_recording = [False] * num_cameras
global_recording = False
streams = []
root = None
camera_threads = []
exit_event = threading.Event()  # Event to signal threads to exit

def camera_feed(camera_index):
    # Create a VideoCapture object for the camera
    cap = cv2.VideoCapture(camera_index)
    streams.append(cap)

    while not exit_event.is_set():  # Check for exit signal
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame to desired dimensions
        frame = cv2.resize(frame, (640, 480))

        # Show the frame in an OpenCV window
        cv2.imshow(f"Camera {camera_index + 1}", frame)

        # Write to video file if recording
        if is_recording[camera_index]:
            recorders[camera_index].write(frame)

        # Check for 'q' key to break the loop (optional)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow(f"Camera {camera_index + 1}")

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
    
    buttons = []

    for i in range(num_cameras):
        button = tk.Button(root, text=f"Start Camera {i + 1}", bg="green",
                           command=lambda idx=i: toggle_recording(idx, buttons[idx]))
        button.grid(row=0, column=i, padx=10, pady=5)
        buttons.append(button)

        # Start the camera feed thread
        thread = threading.Thread(target=camera_feed, args=(i,))
        thread.daemon = True  # Allow thread to exit when main program exits
        camera_threads.append(thread)  # Store the thread in a list
        thread.start()

    global_start_stop_button = tk.Button(root, text="Start All Cameras", bg="green", command=toggle_all_recordings)
    global_start_stop_button.grid(row=1, column=0, columnspan=num_cameras, pady=10)

    close_button = tk.Button(root, text="Close", bg="grey", command=close_application)
    close_button.grid(row=2, column=0, columnspan=num_cameras, pady=10)

    root.protocol("WM_DELETE_WINDOW", close_application)
    root.mainloop()

def close_application():
    global exit_event
    exit_event.set()  # Signal all threads to exit
    stop_all_recordings()
    for cap in streams:
        cap.release()  # Stop the OpenCV streams
    cv2.destroyAllWindows()  # Close all OpenCV windows
    for thread in camera_threads:
        thread.join(timeout=1)  # Wait for threads to finish
    root.quit()

if __name__ == "__main__":
    create_gui()

# Installation and running the script (Windows)
- First clone this repository using `git clone https://github.com/nikhsub/magtestcamSW.git` and cd into it
- Install OpenCV and numpy using `pip install pip install opencv-python numpy Pillow`
- Open `record.py` and change the `num_cameras` to the number of cameras connected, save and exit
- Run `python3 record.py` and wait till all the cameras load in the GUI (This could take a minute depending on how many cameras are connected)
- Once the GUI has loaded, click on the buttons to start and stop recording as necessary: files are saved with the camera numbers and the start and stop timestamp
- Once completed, use the close button to terminate the program

For a version of the script that loads up quicker but has the different cameras in separate windows, use `record_lite.py`. Same installation and running steps apply

# Debian
- The same installation instructions apply but we will be running slightly different scripts
- First we check the indices of the cameras that we are interested in recording - run `ls /dev/video*`. This should display all the usb video devices that are available
- Optionally, we can also check each one individually to ensure that it is indeed the device we are interested in. Run `sudo apt install ffmpeg` and then `ffplay /dev/videoN` where N is the index of the device. If all goes well, this should open up a window that displays the output of the device - make a note of the values of N
- Open `deb_record.py` or `deb_record_lite.py` and change the `cam_inds` variable based on the values of N
- Run `python3 deb_record.py` or `python3 deb_record_lite.py`
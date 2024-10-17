# Installation and running the script
- First clone this repository using `git clone https://github.com/nikhsub/magtestcamSW.git` and cd into it
- Install OpenCV and numpy using `pip install pip install opencv-python numpy`
- Open `record.py` and change the `num_cameras` to the number of cameras connected, save and exit
- Run `python3 record.py` and wait till all the cameras load in the GUI (This could take a minute depending on how many cameras are connected)
- Once the GUI has loaded, click on the buttons to start and stop recording as necessary: files are saved with the camera numbers and the start and stop timestamp
- Once completed, use the close button to terminate the program

For a version of the script that loads up quicker but has the different cameras in separate windows, use `record_lite.py`. Same installation and running steps apply
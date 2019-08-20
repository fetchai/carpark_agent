# Fetch.AI Car Park Agent
This is a project to get a Fetch.AI agent running on a Rasperry Pi which utilises the camera to report on free parking spaces. This data is made available on the Fetch network and can be purchased by other agents. 

This project primarily targets the Raspberry Pi 4. It can be made to run on the Raspberry Pi 3, but it struggles a little. Currently there are only instructions for the Raspberry Pi 4, but I will add instructions for the 3 later.

This document will take you through:
1. Physically building the Camera/Raspberry PI module
2. Preparing the Raspberry Pi 
3. Installing the Fetch.AI carpark_agent software on the Rasperry Pi
4. Installing the client software on a Mac (windows will be done later)


## 1. Physically building the car park agent
### Prerequisits
Things you will need - I've added links to the specific things I bought:
* Raspberry Pi 4 [link](https://thepihut.com/products/raspberry-pi-4-model-b?gclid=EAIaIQobChMImcuwvcfh4wIVirHtCh3szg2EEAAYASAAEgJQ_fD_BwE)
* Raspberry PI Camera [link](https://thepihut.com/products/raspberry-pi-camera-module?variant=758603005)
* Case to put Raspbery Pi and Camera in [link](https://uk.rs-online.com/web/p/products/1270210/?grossPrice=Y&cm_mmc=UK-PLA-DS3A-_-google-_-CSS_UK_EN_CatchAll-_-Catch+All-_-PRODUCT_GROUP&matchtype=&pla-381930223918&gclsrc=aw.ds&&gclid=EAIaIQobChMIqoC2hsjh4wIVxbHtCh0w5whsEAQYASABEgKsJfD_BwE)
* Clamp and Arm [link](https://www.amazon.co.uk/dp/B011769YUM/ref=pe_3187911_189395841_TE_dp_1)
* (optional) Adafruit GPS unit [link](https://www.amazon.co.uk/dp/B01H1R8BK0?ref_=pe_3187911_264767211_E_301_dt_1)
* An HDMI monitor and USB moue and keyboard to plug into your Raspberry Pi
* A PC or Mac 
* A network which the PC/Mac and Raspberry pi can connect to

I use a wireless network because, once your Raspberry Pi is set up, you want as few wires going to it as possible 
The GPS unit is optional and initially these instructions will focus on building the agent without the GPS Unit. I may do an additional set of instructions on how to update it to use a GPS unit.
As mentioned in the introduction, this will also work on a Raspberry Pi 3 - however, some additional steps are needed to make this work, so I'll put some notes about this at the end.

### Building 
The case I got has excellent instructions on how to put it together and mount the Raspberry PI and Camera inside it. However, this case is desgined for the Raspberry Pi 3 rather than 4 and so the side with the holes for the HDMI output will not fit on when the board is inside. I just left this side off, but you could probably enlarge the holes with a file.
https://thepihut.com/blogs/raspberry-pi-tutorials/nwazet-pi-zero-camera-box-assembly-instructions

I will attach the clamp and arm to the box later, 

Plug in the monitor, keyboard and mouse.

## 2. Preparing the Raspberry Pi
If you have got a brand-new Raspberry Pi, you can simply insert the SD card, connect the power and boot up. 

If you do not have a new Rasperry Pi SD card, you will need to make one. To do this follow the NOOBS insructions below. 

### NOOBS
NOOBS is a way to get an SD card like it was when you got your Raspberry Pi new from the shop. Go to here and follow the instructions (I used the "Offline and network install" option): 
https://www.raspberrypi.org/downloads/noobs/
 
Once you have set up your SD card, plug it into your Raspberry Pi, connect the power and watch it boot up. When prompted select the Raspbian operating system and click on Install. 


### Booting up and updating the OS
When you first boot your Raspberry Pi, you will be prompted to enter a password for the Raspberry PI and your wifi password so the Raspberry Pi has access to the internet. When it has finished you will be prompted to restart.

You will need to have your OS completely up to date to avoid problens with these instructions. Open a Terminal window and type:

    sudo apt update -y
    sudo apt-get update
    sudo apt-get dist-upgrade

### Configuring the Raspberry Pi
Click on the Raspberry symbol in the top left of the screen. Select Preferences -> Raspberry Pi Configuration.
Select the Interfaces tab.
Enable the following:
* Camera
* SSH
* VNC

Close the window.

VNC lets us control the Raspberry Pi's desktop even when the monitor, keyboard and mouse have been disconnected. 

Find out the ip address of your raspberry pi. Open a Terminal and type:

    ifconfig

There should be a some lines saying something like:

    ...
    wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.11.9  netmask 255.255.255.0  broadcast 192.168.11.255
    ... 

The numbers after inet is my Raspberry Pi's ip address. In this case 192.168.11.9. Write these down.

Let's test that VNC is working by going to our Mac or PC and downloading and installing VNC viewer:
https://www.realvnc.com/en/connect/download/viewer/

When you run it, you there should be a bar at the top where you can type in an IP address. Type in the IP address of your Raspberry Pi. You will be prompted for your Raspberry Pi password. You should then see your Raspberry Pi's desktop in a window on your Mac or PC.

Now we need to test it without the monitor plugged in:
* Shut down your Raspberry Pi using the Raspberry icon at the top left of the screen
* Unplug your monitor
* Unplug the power from the mains, leave it for 10 seconds then plug it back in
* On your Mac or PC, Use your VNC Viewer to view the desktop of the Raspberry Pi

The reason for testing that this works is that while I never had any problems doing this on the Raspberry Pi 3, the Raspberry Pi 4 had an issue where the screen would revert to a very low resolution and 4:3 aspect ratio when using VNC after rebooting without the monitor plugged in. The car park agent is very difficult to use if this happens, and so I recommend fixing this issue.

### Fixing the low screen-resolution issue on Raspberry Pi 4
Open a terminal and type:

    sudo nano /boot/config.txt
 
 Use the Nano editor to scroll down until you see the following lines:
 
    [pi4]
    # Enable DRM VC4 V3D driver on top of the dispmanx display stack
    dtoverlay=vc4-fkms-v3d
    max_framebuffers=2
 
 Comment out the latter two lines so it now says:
 
    [pi4]
    # Enable DRM VC4 V3D driver on top of the dispmanx display stack
    # dtoverlay=vc4-fkms-v3d
    # max_framebuffers=2
 
Save this file and exit the editor. Now reboot. You can do this by typing into the terminal:
 
    reboot
    
As you reboot, your VNC Viewer on your Mac or PC will no longer be able to see your screen. However it will come back to life once your Raspberry Pi has booted up.
You may find that once you have rebooted, your screen resolution is still small (perhaps even smaller than it was). This is expected. so fix this problem. Open a terminal and type:
 
    sudo raspi-config
    
Use the up/down arrow keys, select Advanced options and press Enter
* Go down the Resolution and press Enter
* Go all the way to the bottom to the 1920X1080 option and press Enter
* Confirm the change
* Use the right arrow to select <Finish>, press Enter
* You will be prompted to restart - do so

Now when the Pi restarts, the VNC Viewer should show a nice large resolution. If this is what happens, you can shut it down, reconnect your monitor and restart it 

## 3. Installing the Fetch.AI carpark_agent software on the Rasperry Pi
I would now work directly on the Raspbery Pi as the VNC connection can be quite laggy sometimes.

We will be getting the code from github.com. At the moment, the code is  in a private repository, so you will need a Fetch github account to get access to it. When the code is public, you will not need to log into github to get the code, but it is still useful to log in and have the page open in a browser on the Raspberry Pi so you can copy and past text into the terminal fromn these instructions.

### Adding a key to your git hub account
While the code is in a private repository, you will not be able to get the code without creating a public/private key pair on the Raspberry Pi and adding it to your github account. Only Fetch employees will be able to do this. 

The first step is to make a public/private key pair. On your Raspberry PI, open a terminal and type (replacing the last bit with your own email address):

    ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
    
When you are presented with options just press Enter to accept the defaults until you are informed a key has been generated.

Now we need to get the public key into the clipboard

    cd ~/.ssh
    cat id_rsa.pub 
    
Now use your mouse to select the text. It should start from the "ssh-rsa......" and finish witth your email address. Try not to select any addiitonal lines or spaces at the beginning and end.
Now right click in the selected text and select Copy

Open up a browser and type this into the address bar (don't copy and past this in as you will lose the key stored in your clipboard):
 
    www.github.com
    
You will be asked to sign in - since you are en employee, you should have an account associated with Fetch.AI already. To add the new private key, do the following:
* In the top right corner, click on the icon representing you. 
* Select settings
* On the left hand side select SSH and GPG keys
* in the top right press, new SSH key
* In the title, write something like "Raspberry Pi"
* Right click in the Key text box and select Paste - you should see a long string of numbers and letters pasted in starting with ssh-rsa and finishing with your email address 
* Click Add SSH Key
    
Now you will be able to download the code from github as if it were a public repository



### Getting the code
In your browser on your Raspberry Pi, type this into the address bar:

    https://github.com/fetchai/carpark_agent

This takes you to the webpage with these instructions. Having it available on the Raspberry Pi is useful for copying and pasting text into the terminal
 
Open a terminal and type:

    cd ~/Desktop
    git clone git@github.com:fetchai/carpark_agent.git
    cd carpark_agent
    
In order to run the machine learning algorithms we need to download a large datafile. In the terminal, type:

    ./car_detection/weights/download_weights.sh
    
There are a number of things that need to be installed on the Raspberry Pi before we can install the agent code itself. Paste this line into the terminal (careful its a long one tha goes off the page, so make sure you select it all before doing copy/paste)

    sudo apt-get install gcc htop vim mc python3-dev ffmpeg virtualenv libatlas-base-dev libsm6 libxext6 clang libblas3 liblapack3 liblapack-dev libblas-dev cython gfortran build-essential libgdal-dev libopenblas-dev liblapack3 liblapacke liblapacke-dev liblcms2-utils liblcms2-2 libwebpdemux2 python3-scipy python3-numpy python3-matplotlib libjasper-dev libqtgui4 libqt4-test protobuf-compiler python3-opencv gpsd gpsd-clients

Now type this:

    pip3 install virtualenv     

Create the virtual environment and activate it

    ./run_scripts/create_venv.sh
    source venv/bin/activate
    
Install the software in develop mode
    
    python setup.py develop
    
When install python software you can either pass `install` or `develop` into the setup.py script.  "install" copies all the code into the python environment so it can be run - this means that there are then two copies of the code and if you change one of the python files, it will not necessarily have any effect unless you reinstall it. This can be quite confusing if you are intending to muck around with the code. Therefore, I recommend that you use "develop" as this will create a link to the code and so any changes you make will take immediate effect when you run the code.  

### Ensure it runs correctly
Try running it
    
    ./run_scripts/run_carpark_agent.sh
    
You should now see the agent running.

If you go back to your Mac or PC and go to the git hub repository for this project and look under resources/images there is an image of a car-park. Print this out and tape it to a wall and point the raspberry pi camera at it. Every few minutes, it will capture in email and perform vehicle detection on the image (detections showing up in blue or green) It should detect the cars in your picture (you might have to wait a few minutes to know that it has worked)

If this all seems to work, power down your Raspberry pi, disconnect the power, keyboard, mouse and keyboard.

Attach the Clamp and Arm and set the camera up pointing to your parking spaces, reconnect the power and let it boot up.


### Configuring the car-park agent
Now go back to your Mac or PC and start up VNC viewer and connect to the Raspberry Pi. 

The agent will not be running. So, open a terminal and type:

    cd Desktop/carpark_agent
    ./run_scripts/run_carpark_agent.sh

When it starts up and you see the output from the camera, you can move your camera around so it is looking at the area you are interested in.

There are likely to be cars in many parts of your image and by default your agent is set up to detect cars everywhere. To restrict detections to the area you are interested in:
* Press Edit Detection Area button
* Press Capture Ref Image button - this will capture in image from the camera and it should be tinted blue - indicating that it will detect everywhere
* Press the red Fill All button - This will turn it all red - showing it will now detect nowhere
* Press Draw detectable button and then draw an outline around the area you are interested in. Ensure you make a completely closed shape
* Press the blue Flood Fill button and then click inside the shape you have drawn. This should fill it blue

Note that this UI can be a bit laggy when running over VNC and while detections are going on, so just do it slowly and be patient.

Count the number of parking spaces in the area of interest you marked out. If it is hard to see, press Live Detect to see things more clearly. When you have counted them press Edit Detection area again to go into edit mode.
Use the arrows either side of "Max Capacity" to set the correct number of parking spaces that the agent can report on.

When you are done press the Live Detect button. 

Close down the agent by pressing the Quit button. If you watch the terminal window that you launched it from, you may find that it takes a while to fully shut down - this is because if it is in the middle of a detection it needs to finish what it is doing before quitting. This can take a minute or so.  

We now need to edit the script file which launches the agent. In the terminal window make sure your current directory is ~/Desktop/carpark_agent and type:

    nano run_scripts/run_carpark_agent.sh

Look for the line that says

    python run_carparkagent.py -ps 120 -fn set_friendly_name -fet 2000 -lat 40.780343 -lon -73.967491
    
Replace the set_friendly_name with something that is unique to you. E.g. I might set it as diarmid_carpark_agent. 

You also need to set the latitude and longitude of your locations. An easy way to find out what this is, is to go open a browser and go to Google Maps and find your current location. Then right click at your location and select "What's here?". A small window will pop up which will let you copy the latitude and longitude of that location. Paste these values into the script command line - be careful not to leave any commas in.
 
My new line would read

    python run_carparkagent.py -ps 120 -fn diarmid_carpark_agent -fet 2000 -lat 52.235063 -lon 0.154021

The -fet argument is how much nano-FET we wish to charge other agents for information about parking. Note that a nano-FET is 0.0000000001 FET, so the default value here is 0.0000002 FET.

Save the edited file and close the editor.

### Make the agent start on boot up

The final thing we need to do is to make the script run whenever we start the Raspberry Pi up. In a terminal type:
    
    crontab -e
    
You may be asked to specify which editor you wish to use.

This editor will then open a text file - scroll down to the bottom and add the following line right the bottom:

    @reboot /home/pi/Desktop/carpark_agent/run_scripts/run_carpark_agent.sh
  
Save the file exit the editor. Reboot your Raspberry Pi.

The carpark agent should now start up after it has booted. Wait for a detection to happen. Look at the stats in the panel on the right hand side of the images. You should see the total number of parking spaces, the number of vehicles detected, the number of free spaces and the latitude and longitude. Check this is all correct. If you click your mouse on any of the smaller images on the right, they will be enlarged in the main panel.

## 4. Installing the client software on a Mac
### Setting up the Mac
Now that the car park agent is running, we will set up a client agent on your Mac or PC. This will query the Fetch.AI network for parking space data.
 
These instructions have only been done for Mac so far.


If you do not have Homebrew already installed, open a terminal:

    xcode-select --install
    
Go through the various dialog boxes agreeing to everything and wait till all the X-code tools install. Now go back to the terminal:

    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    
You need to press ENTER to confirm and will be prompted to give your password.

Now we need to install some software to support the agent. Paste these lines into a Terminal window:
    
    brew install wget python3 opencv3
    pip3 install virtualenv
     
### Getting and installing the code
Since this code it not currently public, you will need to set up a private key and add it to your github profile. Follow the same instructions you did for the Raspberry Pi above in the section titled "Adding a key to your git hub account".
 
This should now let you get the code from github as if it were a public repository
  
Open a Terminal

    cd ~/Desktop
    git clone git@github.com:fetchai/carpark_agent.git
    cd carpark_agent
    
If you want to try running that actual carpark agent on a mac, you can do this. You will need to get the object detection datafile:
    
    ./car_detection/weights/download_weights.sh
    
Create and activate the virtual environment and install the python packages
    
    ./run_scripts/create_venv.sh
    source venv/bin/activate
    python setup.py develop
        
### Running the client
Configure the client agent. Open the file run_scripts/run_client_agent.sh in a text editor. You can do this using a terminal by typing

    nano run_scripts/run_client_agent.sh
    
then find the line that says:

    python run_client_ui.py -fn set_friendly_name -ma 3600 -mf 4000

Change the set_friendly_name to something personal. E.g. I would called it dc_client_agent. So my line would look like:

    python run_client_ui.py -fn dc_client_agent -ma 3600 -mf 4000


The other options on this command line are:
* -ma: The maximum age of any detection data we consider worth having. Default is 3600 seconds (1 hour) 
* -mf: The maximum price this client would be prepared to pay for car parking data. This is specified in nano-FET. I.e. 0.0000000001 FET. SO, default is 0.0000004 FET 

Save the file and exit the editor.

Now you can run the agent
    
    ./run_scripts/run_client_agent.sh
    
You are presented with a screen with a number of buttons. 
* Press Search. This will look for agents on the Fetch.AI network which can supply car parking information. Their public keys will be listed here.
* Press CFP. This sends a "Call for Proposal" to all the gents listed. They will send back a friendly name that you can identify them with, the age of thier last detection, how many spaces they can report about and the total FET they charge. The UI will display whether their data fits your acceptance criteria (new enough and cheap enough)
* When you first start this, you will not be able to request any data because you do not have any FET to spend. Press Generate FET to create some (this will freeze the UI for about 30 seconds while it does this)
* Press Request data. All of the agents that satisfy the acceptance criteria will be asked to send their data. The final column of the table will be filled in showing how many car parking spaces that agent is aware of.  In return this client agent will send the appropriate amount of FET to the car park agent

Note there is a transaction fee of 1 nano-FET when you send FET from one agent to another. So the client agent's FET will go down by a bit more than the cost of the data on its own.

### Running the car-park agent on a Mac
Since you have all the code installed on the Mac, you can also run the car-park agent itself. It will use the Mac's built in camera and so will most likely be looking at you rather than at a car-parking space. However, I have found that the Mac is a much easier environment to develop the code in before then transferring it to the Raspberry Pi. If you hold up a photo of a car-park you can test that the detection algorithms are working correctly.

To configure and run the agent on the mac, simply follow the instructions for the Raspberry Pi above entitled "Configuring the car-park agent" (ignoring the first line about opening up VNC Viewer and connecting to the Raspberry Pi)


## Installing under Windows
The client agent (which can request data) can also be run on Windows. However, you cannot at present run the car park agent (which detects cars in a camera image) on Windows. This is due to some difficulties I have had getting the TensorFlow libraries running. These instructions have been tested on Windows 10.

### Git hub
You will need to clone the repository from git hub as well as execute various linux type Bash scripts. In order to do this, I recommend following these instructions to get Git-Bash installed. Follow these instructions up to and including Step 3 of "Configuring and connecting to a remote repository" - this steps starts with the words "After entering the above command..."'  
https://www.computerhope.com/issues/ch001927.htm

You can now used Git-Bash to execute any of the Linux style bash scripts. 

### Installing Python and Open CV
Download and run this installer:
https://www.python.org/ftp/python/3.7.4/python-3.7.4.exe
On the first page of the installation program there is check box "Add Python 3.7 to PATH" tick this. 

Open Git-Bash and type:

    $ python --version
    
This should print something like:
    
    Python 3.7.3
    
However, if it shows an earlier version e.g.:
    
    Python 2.7.15

Then if means you still have Python 2 in your system PATH and it needs to be removed. To do this on Windows 10:
*   Go to the search bar in the bottom left of the screen and type Environment
*   Click on "Edit the System Environment Variables" option
*   Click on the "Environment variables..." button
*   In the bottom section entitled "System Variables" double click on the Path entry
*   Find the entry with the location of the earlier version of Python e.g. "C:\Python27" select it and press the delete button
*   There may be more than one such entry delete all of them (though keep any which refer to Python37 as this is the new one we just installed)
*   When finished click OK

You will need to close down Git-Bash and restart it.

Now you can open Git-Bash and type:

    $ python --version

Check that is displays the correct version.

Now install virtualenv. Type:
    
    pip install virtualenv

To install OpenCV, Go to this website:
[https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv](https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv)

pip install "c:\Users\dishm\Downloads\opencv_python-4.1.1-cp37-cp37m-win32.whl"

    
### Getting the car-park agent code
Using the Git-Bash terminal you can now get the code from git-hub.  

As before, since this code it not currently public, you will need to set up a private key and add it to your github profile. Follow the same instructions you did for the Raspberry Pi above in the section titled "Adding a key to your git hub account".
 
This should now let you get the code from github as if it were a public repository
  
In the Git-Bash terminal type:

    cd ~/Desktop
    git clone git@github.com:fetchai/carpark_agent.git
    cd carpark_agent
    
 Create and activate the virtual environment and install the python packages (not that the script name to create the virutal envrionment is a bespoke windows version)
    
    ./run_scripts/create_venv_win.sh
    source venv/bin/activate
    python setup.py develop


Use gitapp
./car_detection/weights/download_weights_win.sh

./run_scripts/create_venv.sh
source venv/bin/activate
python setup.py develop

### Cleared and uncleared FET
Both the client and carpark agent UI show the current FET levels at the top left corner of the UI. As soon as the data is sent and the client has initiated the FET transfer, the FET values update. However, this is "uncleared" FET. It takes a while for the transaction to work its way through the network and you can see the cleared and uncleared FET in the detailed status panel at the bottom left of the UI.

Something else to watch out for in this status panel is any errors shown on the Ledger or OEF. If there is an error, the agent may need restarting, or it could be a problem at the server side.

## Known issues
### Searchable but non CFP-able agents
Sometimes the car park agents get in a state where they are still searchable for, but do not receive any notification when CFP is sent. This is an issue at the Fetch.AI end of things and we are working a solution. The only work-around for agent developers at present is to restart their agents when this happens.
### To dos:
* Add illustrative screenshots to these instructions
* Do instructions for Raspberry Pi Version 3
* Do instructions for running the windows client agent
* Do instructions for using the GPS module (instead of entering GPS coordinates manually) 







https://pysource.com/2019/03/15/how-to-install-python-3-and-opencv-4-on-windows/

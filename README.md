# Fetch Car Park Agent
This is a project to get a Fetch.AI agent running on a Rasperry Pi which utilises the camera to report on free parking spaces. This data is made available on the Fetch network and can be purchased by other agents. 

This project primarily targets the Raspbery Pi 4. It can be made to run on the Raspberry Pi 3, but it striggles a little. I include instructions for both versions.

This document will take you through:
1. Physically building the Camera/Raspberry PI module
2. Preparing the Raspberry Pi 
3. Installing the Fetch carpark_agent software on the Rasperry Pi
4. Using the software to report on car parking spaces
5. Installing the client software on a desktop machine (mac only at the moment)


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

I use a wireless network as once your Raspberry Pi is set up, you want as few wires going to it as possible 
The GPS unit is optional and initially these instructions will focus on building the agent without the GPS Unit. I may do an additional set of instructions on how to update it to use a GPS unit.
As mentioned in the introduction, this will also work on a Raspberry Pi 3 (4) - however, some additional sets are needed to make this work, so I'll put some notes about this at the end.

### Building 
The case I got has excellent instructions on how to put it together and mount the Raspberry PI and Camera inside it. However, this case is desgined for the Raspberry Pi 3 rather than 4 and so the side with the holes for the HDMI output will not fit on when the board is inside. I just left this side off, but you could probably just enlarge the holes.
https://thepihut.com/blogs/raspberry-pi-tutorials/nwazet-pi-zero-camera-box-assembly-instructions

I then removed the metal plate from the camera-case wall-mount and attached it to the clamp + arm and then reassembled it all.

Plug in the monitor, keyboard and mouse.

## 2. Preparing the Raspberry Pi
If you have got a brand-new Raspberry Pi, then you will need to first install the Raspbian operating system. If you do not have a new Rasperry pi, I recommend updating your operating system to the latest version.

With your new Raspberry Pi, you should have received an SD card with NOOBS installed on it. If you do not have an SD card like this, then you can turn an existing SD card into one, using the NOOBS instructions below:

###NOOBS
NOOBS is a way to get an SD card like it was when you got your Raspberry Pi new from the shop - I used the "Offline and network install" option and am using version 3.2.0:
Go to here and follow the instructions: https://www.raspberrypi.org/downloads/noobs/

###Installing and updating Raspbian
Once you have set up your SD card, plug it into your Raspberry Pi, connect the power and watch it boot up. When prompted select the Raspbian operating system and click on Install. You may be prompted to enter a password for the Raspberry PI and your wifi password so the Raspberry Pi has access to the internet. When it has finished you will be prompted to restart.

It is wise to ensure your operating system is completely up to date. Open a Terminal window and type:

    sudo apt-get update
    sudo apt-get dist-upgrade

### Configuring the Raspberry Pi

Find out the ip address of your raspberry pi. Open a Terminal and type:

    ifconfig

There should be a some lines saying something like:

    ...
    wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.11.9  netmask 255.255.255.0  broadcast 192.168.11.255
        ... 

The numbers after inet is my Raspberry Pi's ip address. In this case 192.168.11.9 Write these down.


Click on the Raspberry symbol in the top left of the screen. Select Preferences -> Raspberry Pi Configuration.
Select the Interfaces tab.
Enable the following:
* Camera
* SSH
* VNC

VNC lets us control the Raspberry Pi's desktop even when the monitor, keyboard and mouse have been disconnected. 

Let's test that VNC is working by going to our Mac or PC and downloading and installing VNC viewer:
https://www.realvnc.com/en/connect/download/viewer/

When you run it, you there should be a bar at the top where you can type in an IP address. Type in the IP address of your Raspberry Pi. You will be prompted for your Raspberry Pi password. You should then see your Raspberry Pi's desktop in a window on your Mac or PC.

Now we should test it without the monitor plugged in:
Unplug your monitor
Using your VNC viewing, restart your Raspberry pi by going to the Raspberry icon on the rop left of the screen.
You will lose your connecting with the Raspberry pi while it reboots, but when it has rebooted, you should see the desktop again on your Mac or Pc.

The reason for testing that this works is that while I never had any problems doign this on the Raspberry Pi 3, the Raspberry Pi 4 had an issue where the screen solution would revert to a very low resolutoin 4:3 aspect ratio when using VNC after rebooting without the mintor plugged in. If this happens to you, you will need to do the following:

### Fixing the low screen-resolution issue on Raspberry Pi 4
[To do]

## 3. Installing the Fetch carpark_agent software on the Rasperry Pi

I would reconnect the monitor and continue working directly on the Raspbery Pi if possible as the VNC connection can be quite laggy sometimes.

We will be getting the code from github.com

### 
Since the repository is not public, you will need a github account in order to donload the code. You will also need to generate 
In order to install the software you will need a github account. If you odn't have one you will need to create one when you first go to github

Since the repository is not

    sudo apt-get install xclip
Then type:

    cd ~/.ssh  
    cat id_rsa.pub | xclip -i
    
You then need to paste this into your github settings

### Getting the code
Open a terminal

    cd ~/Desktop
    git clone git@github.com:fetchai/carpark_agent.git
    cd carpark_agent
    
Now we need to download the ..:

    ./car_detection/weights/download_weights.sh
    
Now install various things
Past this line into the terminal

    sudo apt-get install gcc htop vim mc python3-dev ffmpeg virtualenv libatlas-base-dev libsm6 libxext6 clang libblas3 liblapack3 liblapack-dev libblas-dev cython gfortran build-essential libgdal-dev libopenblas-dev liblapack3 liblapacke liblapacke-dev liblcms2-utils liblcms2-2 libwebpdemux2 python3-scipy python3-numpy python3-matplotlib libjasper-dev libqtgui4 libqt4-test protobuf-compiler python3-opencv gpsd gpsd-clients
    pip3 install virtualenv     

Create the virtual environment and activate it

    ./run_scripts/create_venv.sh
    source venv/bin/activate
    
Install the software in develop mode
    
    python3 setup.py develop
    
Try running it
    
    ./run_scripts/run_carpark_agent.sh
    

    
 
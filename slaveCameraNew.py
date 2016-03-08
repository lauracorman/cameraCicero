# -*- coding: utf-8 -*-
"""
Created on Thu Aug 06 10:02:52 2015

@author: maintenancelab
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jan 23 14:38:04 2015

:Author: Laura Corman

:Version: 2015-01-29

This file is the main controller for the cameras running with Cicero.
If you want to add / remove a camera type, for the moment, modify the CameraFind function.
Default parameters are in the configCamera.cfg file which should be in the same folder.
This file can be edited manually.

You need to install the PyPNG python module: https://github.com/drj11/pypng 
Its documentation is here: http://pythonhosted.org/pypng/
Pictures are stored as greyscale 16-bits png.
You can change this by modifying the savePicture function

"""


from PyQt4 import QtCore, QtGui#, Qt
from CameraUI import Ui_MainWindow
import time
import socket
import sys
import os
import threading
from CamerasClass import PrincetonCam#, LumeneraCam, PCOCam
#from Lumenera_interface import LucamEnumCameras
from Princeton_wrapper import PrincetonEnumCamera
import tifffile as tiff
import ConfigParser
import numpy as np
from matplotlib import pyplot as plt

class slaveCamera():
    """

    GUI control

    """
    
#==============================================================================
#     Initialization
#==============================================================================
    
    def __init__(self):
        """

        Creates main window and connects camera

        """
        
#        Load config file
        self.config = ConfigParser.RawConfigParser()
        if not os.path.isfile('Z:\PythonPrograms\CameraControllerMain\configCamerasSlave.cfg'):      
            writeConfigFileDefault()
        self.config.read('Z:\PythonPrograms\CameraControllerMain\configCamerasSlave.cfg')
        
#        Booleans describing state of camera and program
        self.is_server_connected = False
        self.are_camera_initialized = False
        self.abortThread = False
        self.takePictureWithCicero = True


#        Thread part and connections
        self.sock = None
        self.threadConnectServer = None
        self.threadListenCicero = None
        self.conn = None
        self.currentPicture = None
        self.server_connect() 
        print 'Server started'
        
#        Fields related to camera handling
        self.cameras = [] # List of cameras
        self.camerasHandles = [] # List of cameras handles
        self.camerasFind()
        self.currentCamera = None
        self.currentPicture = None
        try:
            self.threadListenCicero = threading.Thread(target =self.listenToCicero)
            self.threadListenCicero.start()
            print 'Start Listening to Cicero'
        except:
            print 'Could not start Listening to Cicero'
        
    
    def closeEvent(self,event):
        """

        Closes the camera and the sockets when closing the main window

        """
        print 'Closing the Camera program'
        
        try:
            self.conn.close()
            print 'Connection closed'
        except:
            print 'problem in closing connection'
        try:
            self.sock.close()
            print 'Socket closed'
        except:
            print 'Socket already closed'
        
        try:
            if self.are_camera_initialized:
                self.camerasCloseAll()
        except:
            print 'Camera closing problem'
        return
            
#==============================================================================
#     Non-callback function
#==============================================================================
    
    
    def camerasFind(self):
        """

        Finds all cameras, type by type, and fills the self.cameras and self.camerasHandle objects
        The cameras are not initialized yet : they can be used by a third party program for instance

        """
        numberLumeneraCamera = 0
        numberPrincetonCamera = 0
#        useLumenera = self.config.getint('General Parameters','useLumenera')
#        usePixelfly = self.config.getint('General Parameters','usePixelfly')
        usePrinceton = self.config.getint('General Parameters','usePrinceton')
#        if useLumenera == 1:
#            try:
#                numberLumeneraCamera = len(LucamEnumCameras())
#                for i in range(numberLumeneraCamera):
#                    name = 'Lumenera camera ' + str(i+1)
#                    cam = LumeneraCam(i,name)
#                    self.cameras.append(cam)
#                    self.camerasHandles.append(i)
#            except:
#                print 'No camera of type Lumenera'
        if usePrinceton == 1:
            try:
                numberPrincetonCamera = PrincetonEnumCamera()
                for i in range(numberPrincetonCamera):
                    name = 'Princeton camera ' + str(i+1)
                    cam = PrincetonCam(i+numberLumeneraCamera,name)
                    self.cameras.append(cam)
                    self.camerasHandles.append(i)
            except:
                print 'No camera of type Princeton'
                self.ui.InformationCamera.append('No camera of type Princeton' )
#        if usePixelfly == 1:
#            try:
#    #            Only one PixelFly
#                i = numberPrincetonCamera+numberLumeneraCamera
#                name = 'Pixelfly camera ' + str(1)
#                cam = PCOCam(name,i+numberLumeneraCamera)
#                self.cameras.append(cam)
#                self.camerasHandles.append(0)
#            except:
#                print 'No camera of type Pixelfly'
        for i in range(len(self.cameras)):
            cam = self.cameras[i]
        return
    
    def camerasInitAll(self):
        """

        Initializes all the cameras that have been found - they are now unavailable for other imaging programs.
        Picture taking functionalities become available.
        Exposure time and gain are taken from the config file.

        """
        for i in range(len(self.cameras)):
            cam = self.cameras[i]
#            try:
            cam.openCamera(self.camerasHandles[i])
#            except:
#                cam.name = -1
            if self.config.has_section(cam.name):
                cam.exposureTime = self.config.getfloat(cam.name,'exposureTime')
                print cam.name,' has exposure time ',cam.exposureTime,' ms'
                cam.gain = self.config.getfloat(cam.name,'gain')
        self.are_camera_initialized = True
        return
    
    def camerasCloseAll(self):
        """

        Closes all the cameras safely by freeing the handles.

        """
        for i in range(len(self.cameras)):
            cam = self.cameras[i]
            cam.closeCamera()
            try:
                print 'camera ' + cam.name + ' closed'
            except:
                print 'closing did not work for camera ' + str(i)  
        self.are_camera_initialized = False
        return
        
    def savePicture(self,data,filename):
        """

        Saves a picture in png 16 bits, greyscale.

        """
        print 'shape of picture : ',data.shape
        tiff.imsave(filename,data)
        return
        
 
    def get_day_folder(self):
        """

        Gets current day folder in config file

        """
        
        day_folder = time.strftime(self.config.get('General Parameters','Picture storing path')) 
        
        if not os.path.exists(day_folder):
            os.makedirs(day_folder)
            
        return day_folder
        
        
    def server_connect(self):
        """

        Start server connection
        Open socket on PORT and start listenning thread

        """
        print 'in server connect'
        
        HOST = socket.gethostname()
        PORT = self.config.getint('General Parameters','master port')
        server_address = ((HOST, PORT))
        print 'open socket'
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind(server_address)
        print 'starting up on %s port %s' % server_address
        self.sock.listen(1)
        self.is_server_connected = True
        return
            
        
    def listenToCicero(self):
        """

        Receives the stream of data from Cicero (reopens the connection each time it closes)
        and starts the taking picture thread

        """
        try:
            self.camerasInitAll()
            self.cameraSelect()
            TrigCamDelay = 7.#self.config.getfloat('General Parameters','waitToTrig')
            print 'wait for connection'
            conn, addr = self.sock.accept()
            self.conn = conn
            time.sleep(1)
    #        Max size of Cicero message
            BUFFER_SIZE = 1024 
    #        We want to be always listenning, hence the while True
            while True:
                print 'number of active thread ' + str(threading.active_count())
                try:
                    data = self.conn.recv(BUFFER_SIZE)
                except:
                    print 'lost connection - wait for connection'
                    conn, addr = self.sock.accept()
                    self.conn = conn
                    time.sleep(1)
                    data = self.conn.recv(BUFFER_SIZE)
                print 'data received: ',data
                time.sleep(0.25)
                if data == 'Closing':
                    print 'closing - reset connection'
                    self.sock.listen(1)
                    conn, addr = self.sock.accept() # Restart the connection that cicero has closed
                    self.conn = conn
                elif data == 'Abort':
                    print 'aborting - reset connection'
                    self.abortTakingPicture()
                else:
                    print 'message : start taking picture with Cicero if enabled'
                    print 'on est ici'
                    #if self.takePictureWithCicero: # Boolean whise value is controlled via GUI interaction
                    #if True: # Boolean whise value is controlled via GUI interaction
                    print 'on est là'
                    print 'Taking picture with Cicero'
                    shot_name = data.split("@", 1)[0]
                    durationSequence = float(data.split("@")[1])
                    if TrigCamDelay>=3:
                        time.sleep(max([0,durationSequence-TrigCamDelay]))
                    self.abortThread = False
                    self.shot_name = shot_name
                    print 'Go!'
                    self.takeCiceroPicture()
                    print 'Done'
                print 'End of True'
                
        except KeyboardInterrupt:
            print 'Keyboard interrupt - closing and exiting'
            self.closeEvent()
        return

        
    def abortTakingPicture(self):
        """

        Resets the camera if needed if the sequence has been interrupted between 
        the moment when the camera has been told to wait for a trigger and the trigger itself

        """
        print 'Try to abort picture taking...'
        self.abortThread = True
        self.currentCamera.abortTakeTriggedPicture()
        print '...Done'
        return

        
    def computeAbsorptionPicture(self, im):
        """

        Computes the OD to be displayed in the matplotlib widget

        """
        withatoms = 1.*im[0]
        withoutatoms = 1.*im[1]
        background = 1.*im[2]
#        absorption = numpy.log((withatoms - background)/(withoutatoms - background))
        absorption = np.nan_to_num(np.log((withoutatoms - background)/(withatoms - background)))
        absorption[absorption<0] = 0
        absorption[absorption>10] = 0
        maxOD = np.max(absorption*(withoutatoms>(0.5*np.max(withoutatoms))))
        return maxOD, absorption
        
        
    def takeCiceroPicture(self):
        """

        Start taking a trigged picture and when it is done, start a thread for 
        saving the picture and a thread for displaying it

        """
        
        im = self.currentCamera.takeTriggedPicture()
        self.saveCiceroPicture(im)
        im = None
        self.currentCamera._getCameraInfo()

        return
    
    def saveCiceroPicture(self,im):
        """

        Save a picture taken by Cicero (3 pictures to save). 
        One can enable the saving as numpy array.
        Skips if the number of pictures is not the right one.

        """
        shot_name = self.shot_name
        FORMAT = '.tif'
        nameCam = self.currentCamera.name
        nameCam = nameCam.replace(" ","")
        pic = ['_With','_NoAt', '_Bgd', '_Bgd2']
        dayFolder = self.get_day_folder()
        if len(im) < 3:
            print 'Problem in size of im: ' + str(len(im))
        else:
            for i in range(len(im)):
                if not self.abortThread:
#                    Save as png
                    name = dayFolder + '\\' + shot_name + '_' + nameCam + pic[i] + FORMAT
                    self.savePicture(im[i], name)
#                    print 'saving im[',i,'] as ',name
##                    Save as numpy array
#                    name2 = dayFolder + '\\' + shot_name + '_' + nameCam + pic[i] + '.npy'
#                    numpy.save(name2,im[i])
                else:
                    print 'sequence aborted'
                    return
            self.conn.sendall('Images saved in' + dayFolder + '\\' + shot_name)
#            print shot_name + '  images saved ' + str(self.index)
#            self.index = self.index + 1
        return
        
#==============================================================================
#     Callback functions
#==============================================================================
    

            
          
    def cameraSelect(self,currentIndex = 0):
        """

        If button clicked selects the camera in the drop menu as the current one, and update the text field the current parameters.

        """
        
        try:
            
            cam = self.cameras[currentIndex]
            if cam.name == -1:
                print 'This camera cannot be selected (could not be opened)'
            else:
                self.currentCamera = self.cameras[currentIndex]
                print 'current camera is '+ self.cameras[currentIndex].name
                print 'exposure time = ' + str(self.currentCamera.exposureTime) + ' ms'
                print 'gain = ' + str(self.currentCamera.gain)
        except:
            print 'problem with current camera'
            return
        return
            
            
            


def writeConfigFileDefault():
    """

    Writes a first config file in case it does not already exist

    """
    config = ConfigParser.RawConfigParser()
    
    config.add_section('General Parameters')
    config.set('General Parameters','cicero port','12121')
    config.set('General Parameters','master port','12122')
    config.set('General Parameters','Picture storing path','Z:\%Y\%b%Y\%d%b%Y\Pictures\RAW')
    config.set('General Parameters','useLumenera','0')
    config.set('General Parameters','usePixelfly','0')
    config.set('General Parameters','usePrinceton','1')
    config.set('General Parameters','waitToTrig','3')
    
    config.add_section('Default camera')
    config.set('Default camera','exposureTime','1')
    config.set('Default camera','gain','1')
    
    config.add_section('Lumenera camera 1')
    config.set('Lumenera camera 1','exposureTime','0.312')
    config.set('Lumenera camera 1','gain','1')
    
    config.add_section('Lumenera camera 2')
    config.set('Lumenera camera 2','exposureTime','0.312')
    config.set('Lumenera camera 2','gain','1')
    
    config.add_section('Lumenera camera 3')
    config.set('Lumenera camera 2','exposureTime','0.312')
    config.set('Lumenera camera 2','gain','1')
    
    config.add_section('Pixelfly camera 1')
    config.set('Pixelfly camera 1','exposureTime','0.2')
    config.set('Pixelfly camera 1','gain','1')
    
    config.add_section('Princeton camera 1')
    config.set('Princeton camera 1','exposureTime','0.04')
    config.set('Princeton camera 1','gain','1')
    
    with open('configCamerasSlave.cfg','w') as configfile:
        config.write(configfile)
    return
    

try:
    slave = slaveCamera()
except KeyboardInterrupt:
    print 'Keyboard interrupt - closing and exiting'
    slave.closeEvent()


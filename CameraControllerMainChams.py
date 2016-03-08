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
from CameraUIMain import Ui_MainWindow
import time
import socket
import sys
import os
import threading
from CamerasClass import PrincetonCam, LumeneraCam, PCOCam
from CamerasClass_JL2 import ChameleonCam
from Lumenera_interface import LucamEnumCameras
from Princeton_wrapper import PrincetonEnumCamera
import tifffile as tiff
import ConfigParser
import numpy as np
from matplotlib import pyplot as plt
import cv

class MainWindow(QtGui.QMainWindow):
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
#        Setup Main window
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.index = 0
        
#        Load config file
        self.config = ConfigParser.RawConfigParser()
        if not os.path.isfile('configCamerasMain.cfg'):      
            writeConfigFileDefault()
        self.config.read('configCamerasMain.cfg')

        self.saveFromSlave = False
        self.slaveIP = self.config.get('General Parameters','slave IP')
        self.slavePort = self.config.getint('General Parameters','slave port')
        
#        Booleans describing state of camera and program
        self.is_server_connected = False
        self.is_slaveserver_connected = False
        self.is_preview_on = False
        self.cicero_is_running = False
        self.are_camera_initialized = False
        self.exitFromProgram = False
        self.abortThread = False
        self.takePictureWithCicero = False
        self.lastCheckServer = False

#        Timer to check if server is alive 
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_server_connection)
        self.timer.start(1500)

#        Thread part and connections
        self.sock = None
        self.threadConnectServer = None
        self.threadListenCicero = None
        self.conn = None
        self.currentPicture = None
        self.sockSlave = None
        try:
            self.server_connect() 
            print 'Server started'
        except:
            print 'Could not connnect to server'
#        try:
        self.serverSlave_connect() 
        print 'Slave server started'
#        except:
#            print 'Could not connnect to slave server'
        
#        Fields related to camera handling
        self.cameras = [] # List of cameras
        self.camerasHandles = [] # List of cameras handles
        self.camerasFind()
        self.currentCamera = None
        self.currentPicture = None
        self.setCameraOnlyParam(self.are_camera_initialized)
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
        self.ui.InformationCamera.append('Closing')
        self.exitFromProgram = True
        self.cicero_is_running = False
        
        try:
            self.conn.close()
            print 'Connection closed'
            self.ui.CiceroCommunication.append('Connection closed')
        except:
            print 'Unable to close connection'
            self.ui.CiceroCommunication.append('Unable to close connection')
            
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
    

    def check_server_connection(self):
        """

        If server is connected check that Cicero did not stop every
        QtCore.QTimer cycle (preset 1.5 sec)

        """
        
#        if self.is_server_connected:
#            if not self.threadConnectServer.isAlive():
#                if self.lastCheckServer:
#                    print 'Server not connected ?'
#                    self.lastCheckServer = False
#            elif not self.lastCheckServer:
#                self.lastCheckServer = True
        return
    
    def camerasFind(self):
        """

        Finds all cameras, type by type, and fills the self.cameras and self.camerasHandle objects
        The cameras are not initialized yet : they can be used by a third party program for instance

        """
        numberLumeneraCamera = 0
        numberPrincetonCamera = 0
        useLumenera = self.config.getint('General Parameters','useLumenera')
        usePixelfly = self.config.getint('General Parameters','usePixelfly')
        usePrinceton = self.config.getint('General Parameters','usePrinceton')
        if useLumenera == 1:
            try:
                numberLumeneraCamera = len(LucamEnumCameras())
                for i in range(numberLumeneraCamera):
                    name = 'Lumenera camera ' + str(i+1)
                    cam = LumeneraCam(i,name)
                    self.cameras.append(cam)
                    self.camerasHandles.append(i)
            except:
                print 'No camera of type Lumenera'
                self.ui.InformationCamera.append('No camera of type Lumenera' )
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
        if usePixelfly == 1:
            try:
    #            Only one PixelFly
                i = numberPrincetonCamera+numberLumeneraCamera
                name = 'Pixelfly camera ' + str(1)
                cam = PCOCam(name,i+numberLumeneraCamera)
                self.cameras.append(cam)
                self.camerasHandles.append(0)
            except:
                print 'No camera of type Pixelfly'
                self.ui.InformationCamera.append('No camera of type Pixelfly' )
        for i in range(len(self.cameras)):
            cam = self.cameras[i]
            self.ui.cameraSelectComboBox.insertItem(i,cam.name)
        return
    
    def camerasInitAll(self):
        """

        Initializes all the cameras that have been found - they are now unavailable for other imaging programs.
        Picture taking functionalities become available.
        Exposure time and gain are taken from the config file.

        """
        for i in range(len(self.cameras)):
            cam = self.cameras[i]
            try:
                cam.openCamera(self.camerasHandles[i])
            except:
                cam.name = -1
            if self.config.has_section(cam.name):
                cam.exposureTime = self.config.getfloat(cam.name,'exposureTime')
                cam.gain = self.config.getfloat(cam.name,'gain')
        if (not self.is_server_connected) :
            self.setCameraOnlyParam(True)
        elif not self.takePictureWithCicero:
            self.setCameraOnlyParam(True)
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
                self.ui.InformationCamera.append('camera ' + cam.name + ' closed')
            except:
                print 'closing did not work for camera ' + str(i)  
                self.ui.InformationCamera.append('closing did not work for camera ' + str(i) )
        self.setCameraOnlyParam(False)
        self.are_camera_initialized = False
        return
        
    def savePicture(self,data,filename):
        """

        Saves a picture in png 16 bits, greyscale.

        """
        print 'shape of picture : ',data.shape
        tiff.imsave(filename,data)
        return
        
    def saveCurrentPicture(self):
        """

        If the field self.currentImage is none empty, displays a prompt to enter a filename and saves it.

        """
        if not type(self.currentPicture) == type(None):
            filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', "test", "Images (*.png)")
            data = self.currentPicture
            self.savePicture(data,filename)
        return
 
    def get_day_folder(self):
        """

        Gets current day folder in config file

        """
        
        day_folder = time.strftime(self.config.get('General Parameters','Picture storing path')) 
        
        if not os.path.exists(day_folder):
            os.makedirs(day_folder)
            dayFolderCham1 = day_folder[:-3] + 'CHAMDMD'
            dayFolderCham2 = day_folder[:-3] + 'CHAMAcc'
            os.makedirs(dayFolderCham1)
            os.makedirs(dayFolderCham2)
            
        return day_folder
        
    def setCameraOnlyParam(self,boolean):
        """

        Enables/disables the right buttons if the cameras are initialized or not.

        """
        self.ui.takeSnapshotButton.setEnabled(boolean)
        self.ui.previewButton.setEnabled(boolean)
        self.ui.cameraUpdateButton.setEnabled(boolean)
        self.ui.cameraSelectButton.setEnabled(boolean)
        self.ui.cameraRestoreButton.setEnabled(boolean)
        self.ui.saveSnapshotButton.setEnabled(boolean)
        return
        
    def setPreviewModeParam(self,boolean):
        """

        Enables/disables the right buttons if the preview mode of the current camera is started.

        """
        self.ui.takeSnapshotButton.setEnabled(not boolean)
        self.ui.cameraUpdateButton.setEnabled(not boolean)
        self.ui.cameraSelectButton.setEnabled(not boolean)
        self.ui.cameraRestoreButton.setEnabled(not boolean)
        self.ui.saveSnapshotButton.setEnabled(not boolean)
        self.ui.ciceroStartButton.setEnabled(not boolean)
        return
        
    def setCiceroModeParam(self,boolean):
        """

        Enables/disables the right buttons if the pictures are being taken when Cicero says it.

        """
        self.ui.takeSnapshotButton.setEnabled(not boolean)
        self.ui.previewButton.setEnabled(not boolean)
        self.ui.cameraUpdateButton.setEnabled(not boolean)
        self.ui.cameraSelectButton.setEnabled(not boolean)
        self.ui.cameraRestoreButton.setEnabled(not boolean)
        self.ui.saveSnapshotButton.setEnabled(not boolean)
        return
        
    def server_connect(self):
        """

        Start server connection
        Open socket on PORT and start listenning thread

        """
        try:
            print 'in server connect'
            HOST = socket.gethostname()
            PORT = self.config.getint('General Parameters','Cicero port')  
            server_address = ((HOST, PORT))
            print 'open socket'
            self.sock = socket.socket()
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(server_address)
            print 'starting up on %s port %s' % server_address
            self.ui.CiceroCommunication.append(
                'starting up on %s port %s' % server_address) 
            self.sock.listen(1)
            self.is_server_connected = True
        except:
            print 'Could not connect to server'
        return
        
    def serverSlave_connect(self):
        """

        Start server connection
        Open socket on PORT and start listenning thread

        """
        try:
            print 'Connecting to slave server'
            self.slaveIP = self.config.get('General Parameters','slave IP')
            self.slavePort = self.config.getint('General Parameters','slave port')
            HOST = self.slaveIP
            PORT = self.slavePort
            server_address = ((HOST, PORT))
            print 'open socket'
            print server_address
            self.sockSlave = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #        try:
            self.sockSlave.connect(server_address)
    #        except:
    #            self.sockSlave = None
    #            print 'Could not open slave socket'
    #            return
            print 'starting slave on %s port %s' % server_address
            self.ui.CiceroCommunication.append(
                'starting slave on %s port %s' % server_address) 
            self.is_slaveserver_connected = True
        except:
            print 'Could not connect to slave server'
        return
            
        
    def listenToCicero(self):
        """

        Receives the stream of data from Cicero (reopens the connection each time it closes)
        and starts the taking picture thread

        """
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
            self.ui.CiceroCommunication.append(data)
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
                if self.takePictureWithCicero: # Boolean whise value is controlled via GUI interaction
                    print 'Taking picture with Cicero'                    
                    if self.saveFromSlave:
                        self.ui.CiceroCommunication.append('on remote server')
                        print 'on remote server'
                        if type(self.sockSlave) == type(None):
                            try:
                                self.sockSlave.close()
                                print 'Slave server closed'
                            except:
                                print 'Could not close slave server'
                                continue
                            try:
                                self.serverSlave_connect() 
                                print 'Slave server started'
                            except:
                                print 'Could not (re)connnect to slave server'
                                continue
                        try:
                            self.sockSlave.send(data)
                        except:
                            try:
                                self.sockSlave.close()
                                print 'Slave server closed'
                            except:
                                print 'Could not close slave server'
                                continue
                            self.serverSlave_connect() 
                            print 'Slave server started'
                            
                    else:
                        print 'on local server'
                        shot_name = data.split("@", 1)[0]
    #                    durationSequence = float(data.split("@")[1])
    #                    time.sleep(durationSequence-2.)
    #                    Timeout not implemented
    #                    sequence_time = float(data.split('@', 2)[1].replace(",", "."))
    #                    self.currentCamera.timeout = int(2*(sequence_time + 10) * 1000)
                        self.abortThread = False
                        self.shot_name = shot_name
                        
                        #Chameleon images si pas en Princeton
                        print 'Go Chameleon Cam DMD!'
                        cam = self.cameras[2] #ou 2 3? -> car on a 2 chameleon, mais revient au meme, les changer dans 'context'
                        cvimage = cam.takeSinglePicture()
                        shot_name = self.shot_name
                        FORMAT = '.png'
                        nameCam = self.currentCamera.name
                        dayFolder = self.get_day_folder()
                        print dayFolder
                        dayFolderCham = dayFolder[:-3] + 'CHAMDMD'
                        print dayFolderCham
                        name = dayFolderCham + '\\' + shot_name + '_' + nameCam + FORMAT                   
                        #self.savePicture(im, name)
                        cv.SaveImage(name, cvimage)
                        
                        print 'Go Chameleon Cam Acc!'
                        cam = self.cameras[2] #ou 2 3? -> car on a 2 chameleon, mais revient au meme, les changer dans 'context'
                        cvimage = cam.takeSinglePictureAcc()
                        shot_name = self.shot_name
                        FORMAT = '.png'
                        nameCam = self.currentCamera.name
                        dayFolder = self.get_day_folder()
                        dayFolderCham = dayFolder[:-3] + 'CHAMAcc'
                        name = dayFolderCham + '\\' + shot_name + '_' + nameCam + FORMAT                   
                        #self.savePicture(im, name)
                        cv.SaveImage(name, cvimage)   
                        
                        print 'Go Normal Cam!'
                        self.takeCiceroPicture()
                        print 'Done'
            print 'End of True'
        return

        
    def abortTakingPicture(self):
        """

        Resets the camera if needed if the sequence has been interrupted between 
        the moment when the camera has been told to wait for a trigger and the trigger itself

        """
        try:
            self.ui.CiceroCommunication.append('Try to abort picture taking...')
            print 'Try to abort picture taking...'
            self.abortThread = True
            self.currentCamera.abortTakeTriggedPicture()
            self.ui.CiceroCommunication.append('...Done')
            print '...Done'
        except:
            print 'problem but probably ok'
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
#        saveThread = threading.Thread(target = self.saveCiceroPicture, args=(im,))
#        saveThread.start()
#        showThread = threading.Thread(target = self.showCiceroPicture, args=(im,))
#        showThread.start()
        self.saveCiceroPicture(im)
#        self.showCiceroPicture(im)
        im = None
        return
    
    def saveCiceroPicture(self,im):
        """

        Save a picture taken by Cicero (3 pictures to save). 
        One can enable the saving as numpy array.
        Skips if the number of pictures is not the right one.

        """
#        im = self.currentCamera
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
                    self.ui.CiceroCommunication.append('sequence aborted')
                    return
            try:
                self.conn.sendall('Images saved in' + dayFolder + '\\' + shot_name)
            except:
                print "Could not send acknowledgement"
            self.ui.CiceroCommunication.append(shot_name + '  images saved')
            print shot_name + '  images saved ' + str(self.index)
            self.index = self.index + 1
        return
            
    def showCiceroPicture(self,im):
        """

        Displays the computed OD in the matplotlib widget

        """
        if len(im) == 3:
            maxOD, absorption = self.computeAbsorptionPicture(im)
            self.ui.matplotlibGadget.plotDataPoints(absorption,CLim = maxOD)
        return
        
#==============================================================================
#     Callback functions
#==============================================================================
    

    @QtCore.pyqtSignature("")
    def on_ciceroStartButton_clicked(self):
        """

        Inverts the value of the takePictureWithCicero boolean and enables/disables thee right buttons.

        """
        self.takePictureWithCicero = not self.takePictureWithCicero
        if self.takePictureWithCicero:
            self.setCameraOnlyParam(False)
            self.setCiceroModeParam(True)
            self.ui.ciceroStartButton.setText('Stop Cicero Server')
        else:
            self.setCiceroModeParam(False)
            self.setCameraOnlyParam(True)
            self.ui.ciceroStartButton.setText('Start Cicero Server')
        return
            

    @QtCore.pyqtSignature("")            
    def on_takeSnapshotButton_clicked(self):
        """

        If button clicked takes snapshot and displays it. Skips if a current camera is not selected.

        """
        if type(self.currentCamera) == type(None):
            return
        try:
            self.currentCamera.abortTakeTriggedPicture()
        except:
            print 'abort take picture not working'
        im = self.currentCamera.takeSinglePicture()
        self.ui.matplotlibGadget.plotDataPoints(im,CLim = np.max(im))
        self.currentPicture = im
        return

    @QtCore.pyqtSignature("")            
    def on_saveSnapshotButton_clicked(self):
        """

        If button clicked saves the current picture. Skips if a current camera is not selected.

        """
        if type(self.currentCamera) == type(None):
            return
        self.saveCurrentPicture()
        return
            

    @QtCore.pyqtSignature("")            
    def on_cameraEnableButton_clicked(self):
        """

        If button clicked initializes all the camera.

        """
        if not self.are_camera_initialized:
            self.camerasInitAll()
            self.ui.cameraEnableButton.setText('Disable all camera')
        else:
            self.camerasCloseAll()
            self.ui.cameraEnableButton.setText('Enable all camera')
        return
            

    @QtCore.pyqtSignature("")            
    def on_cameraSelectButton_clicked(self):
        """

        If button clicked selects the camera in the drop menu as the current one, and update the text field the current parameters.

        """
        
        try:
            
            currentIndex = self.ui.cameraSelectComboBox.currentIndex()
            cam = self.cameras[currentIndex]
            if cam.name == -1:
                print 'This camera cannot be selected (could not be opened)'
                self.ui.InformationCamera.append('This camera cannot be selected (could not be opened)')
            else:
                self.currentCamera = self.cameras[currentIndex]
                print 'current camera is '+ self.cameras[currentIndex].name
                self.ui.InformationCamera.append('current camera is '+ self.cameras[currentIndex].name)
                self.ui.exposureEdit.setText(str(self.currentCamera.exposureTime))
                self.ui.gainEdit.setText(str(self.currentCamera.gain))
        except:
            print 'problem with current camera'
            return
        return
            
            

    @QtCore.pyqtSignature("")            
    def on_cameraUpdateButton_clicked(self):
        """

        If button clicked sets the exposure time and gain to the values written in the text fields.

        """
        try:
            self.currentCamera.exposureTime = float(self.ui.exposureEdit.text())
        except:
            print 'problem updating exposure time'
        try:
            self.currentCamera.gain = float(self.ui.gainEdit.text())
        except:
            print 'problem updating gain'
        return
            
            
    @QtCore.pyqtSignature("")            
    def on_cameraRestoreButton_clicked(self):
        """

        If button clicked restores the exposure time and gain to the values of the config file.

        """
        if self.config.has_section(self.currentCamera.name):
            self.currentCamera.exposureTime = self.config.getfloat(self.currentCamera.name,'exposureTime')
            self.currentCamera.gain = self.config.getfloat(self.currentCamera.name,'gain')
        else:
            self.currentCamera.exposureTime = self.config.getfloat('Default camera','exposureTime')
            self.currentCamera.gain = self.config.getfloat('Default camera','gain')
        self.ui.exposureEdit.setText(str(self.currentCamera.exposureTime))
        self.ui.gainEdit.setText(str(self.currentCamera.gain))
        return
            

    @QtCore.pyqtSignature("")
    def on_previewButton_clicked(self):
        """

        Preview window

        """
        if not self.is_preview_on:
            self.currentCamera.startPreview() 
            self.is_preview_on = True
            self.setPreviewModeParam(True)
            self.ui.previewButton.setText('Stop Preview')
        else:
            self.ui.previewButton.setText('Start Preview')
            self.currentCamera.stopPreview() 
            self.is_preview_on = False
            self.setPreviewModeParam(False)
        return
        
    @QtCore.pyqtSignature("")
    def on_radioButton_clicked(self):
        """

        Preview window

        """
        self.saveFromSlave = not self.saveFromSlave


def writeConfigFileDefault():
    """

    Writes a first config file in case it does not already exist

    """
    config = ConfigParser.RawConfigParser()
    
    config.add_section('General Parameters')
    config.set('General Parameters','Cicero port','12121')
    config.set('General Parameters','Picture storing path','Z:\%Y\%b%Y\%d%b%Y\Pictures\RAW')
    config.set('General Parameters','slave IP','172.16.2.17')
    config.set('General Parameters','slave port','12122')
    config.set('General Parameters','useLumenera','1')
    config.set('General Parameters','usePixelfly','1')
    config.set('General Parameters','usePrinceton','0')
    
    config.add_section('Default camera')
    config.set('Default camera','exposureTime','1')
    config.set('Default camera','gain','1')
    
    config.add_section('Lumenera camera 1')
    config.set('Lumenera camera 1','exposureTime','0.312')
    config.set('Lumenera camera 1','gain','1')
    
    config.add_section('Lumenera camera 2')
    config.set('Lumenera camera 2','exposureTime','0.312')
    config.set('Lumenera camera 2','gain','1')
    
    config.add_section('Princeton camera 1')
    config.set('Princeton camera 1','exposureTime','0.1')
    config.set('Princeton camera 1','gain','1')
    
    with open('configCamerasMain.cfg','w') as configfile:
        config.write(configfile)
    return
    

    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())


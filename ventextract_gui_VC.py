# -*- coding: utf-8 -*-
"""
VentExtract_gui_VC.py
"""
import numpy as np
import scipy
from scipy import signal
from scipy.signal import find_peaks
from matplotlib import pyplot as plt
from matplotlib.pyplot import ion
ion()
import os
import sys
from Tkinter import *
import tkFileDialog as filedialog

def dump(final_divisions):  #Saving Function
    final_divisions = np.sort(final_divisions)
    print(final_divisions)
    print("Number of Levels: " + str(len(final_divisions)-1))
            
    run = np.genfromtxt(RAW_DATA, dtype=str, deletechars="b'")
    run = np.transpose(run)
            
    for i, segment in enumerate(final_divisions[0:-1]):
        run_sample = np.hstack((np.transpose([run[:,0]]), run[:,segment:final_divisions[i+1]-250]))
        run_sample = np.vstack((run_sample[0:2,:], run_sample[3:5,:], run_sample[14,:], run_sample[17,:]))
            
        np.savetxt((OUT_PATH + "/" + "VC" + str(i+6) + '.ASC'), np.transpose(run_sample), fmt='%s', delimiter = '\t')

def browse():
    global OUT_PATH
    OUT_PATH = filedialog.askdirectory(initialdir = "/", title = "Select Output Folder")
    filename = filedialog.askopenfilename(initialdir = "/", 
                                          title = "Select ASC File", 
                                          filetypes = (("ASC files", 
                                                        "*.ASC*"), 
                                                       ("all files", 
                                                        "*.*"))) 
    global RAW_DATA
    RAW_DATA = filename
    
    x_extract = np.genfromtxt(RAW_DATA, dtype=str, deletechars="b'")
    x = np.transpose(x_extract)
    x = x[:,1:]
    x = x.astype(float)

    #Airway Pressure Analysis
    xx = x[3,:]
    peaks1, properties1 = find_peaks(xx, prominence=1)
    dary1 = xx[peaks1]
    dary1 -= np.average(dary1)
    step1 = np.hstack((1*np.ones(4), -1*np.ones(4)))
    dary_step1 = np.convolve(dary1, step1, mode='full')
    peaks21 = signal.find_peaks(dary_step1[3:-4], prominence=0.7, distance=10)[0]

    plt.figure()
    plt.plot(xx)
    plt.scatter(peaks1[peaks21],xx[peaks1[peaks21]], c="red")
    plt.show()

    #Flow Analysis
    xx = x[1,:]
    peaks2, properties2 = find_peaks(xx, prominence=0.05)
    dary2 = xx[peaks2]
    dary2 -= np.average(dary2)
    step2 = np.hstack((1*np.ones(4), -1*np.ones(4)))
    dary_step2 = np.convolve(dary2, step2, mode='full')
    peaks22 = signal.find_peaks(dary_step2[3:-4]*100, prominence=0.01, distance=10)[0]

    plt.figure()
    plt.plot(xx)
    plt.scatter(peaks2[peaks22],xx[peaks2[peaks22]], c="red")
    plt.show()

    #User Manually Chooses Airway Pressure or Flow Based Analysis
    mode = input("Please enter mode 1(Pmo) or 2(Flow): ")
    mode = int(mode)

    if mode == 1:
        print("Using mode 1")
        xx = x[3,:]
        peaks = peaks1
        peaks2 = peaks21
    elif mode == 2:
        print("Using mode 2")
        xx = x[1,:]
        peaks = peaks2
        peaks2 = peaks22

    #Proceed With Selected Analysis Mode
    fig = plt.figure()

    global final_divisions
    final_divisions = peaks[peaks2]

    plt.plot(xx)

    plt.scatter(final_divisions,xx[final_divisions], c="red")

    coords = []
    
    def onclick(event): #Interactive Plot To Allow Manual Fine-Tuning
        ix = event.xdata

        if ix < 5:
            fig.canvas.mpl_disconnect(cid)
            dump(final_divisions)
        
        else:
            coords.append(ix)

            global final_divisions
            deleting_mode = False
            for i, division in enumerate (final_divisions):
                if abs(ix-division) < 250:
                    final_divisions = np.delete(final_divisions, i)
                    deleting_mode = True
            if not(deleting_mode):
                final_divisions = np.append(final_divisions, ix)
                final_divisions = final_divisions.astype(int)

            print(final_divisions)

            plt.clf()

            plt.plot(xx)

            plt.scatter(final_divisions,xx[final_divisions], c="red")

        return coords
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
                                                                                                          
#GUI For File Loading, Path Selection
window = Tk() 
   
window.title('NVR') 
   
window.geometry("500x250") 
   
window.config(background = "white") 
   
title = Label(window,  
                            text = "ZAM Breath Extraction Program", 
                            width = 50, height = 4,  
                            fg = "blue") 
   
       
button_start = Button(window,  
                        text = "Start", 
                        command = browse)  
   
button_exit = Button(window,  
                     text = "Exit", 
                     command = exit)  
   
title.grid(column = 1, row = 1) 
   
button_start.grid(column = 1, row = 2) 
   
button_exit.grid(column = 1,row = 3) 
   
window.mainloop() 

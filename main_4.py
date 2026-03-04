import preprocess as pp
import word_detection as wd
#import word_classification as wc
import google_ocr as go
import create_prescription as cp
import spell
import json
import argparse
import glob
import os
import numpy as np
import cv2
import sys
import time
import tkinter as tk
from tkinter.filedialog import askopenfilename
import shutil
import os
import sys
from PIL import Image, ImageTk
import fastwer
fileName=""
window = tk.Tk()
window.title("Medicine Name Extraction from Doctor's Prescription and Medicine Strips")
window.geometry("600x600")
# Set background image
background_image = tk.PhotoImage(file="C:/Users/nehat/Desktop/m66.png")
background_label = tk.Label(window, image=background_image)
background_label.place(relwidth=1, relheight=1)
title = tk.Label(window, text="Click below to upload the Doctors Prescription and Strips", background="white", fg="Black", font=("Small Fonts", 17))
title.place(relx=0.5, rely=0.05, anchor=tk.CENTER)

#Running instructions - python main_2.py --google-ocr
parser = argparse.ArgumentParser()
parser.add_argument('--google-ocr', action="store_true",dest='google_ocr',default=False)
parser.add_argument('--file', action="store", dest="filename", type=str)

if __name__ == "__main__":
	dictionary = {}
	start_time = time.time()
	print("Opening the file")
	fire=open("diction.txt","r")
	print("Reading from file")
	test_string=fire.read()
	print("Converting to dictionary")
	res = json.loads(test_string)
	print("Converted")
	dictionary=res
	fire.close()
	import pandas as pd
	xl_workbook = pd.ExcelFile("Medicine1.xlsx")  # Load the excel workbook
	df = xl_workbook.parse("Medicine")  # Parse the sheet into a dataframe
	o_name = df['Medicine'].tolist()
	desc= df['Description'].tolist()
	run_time = time.time() - start_time
	print('%.2f seconds to run' % run_time)
	def analysis():
                import pyttsx3
                def play_text(text1,text2):
                        engine=pyttsx3.init()
                        engine.say(text1)
                        engine.runAndWait()
                        engine=pyttsx3.init()
                        engine.say(text2)
                        engine.runAndWait()
                global fileName
                #Load image and change channels
                print("file:",fileName)
                image = cv2.cvtColor(cv2.imread(fileName), cv2.COLOR_BGR2RGB)
                #Pre-processing = Cropping + Binarization
                #print(
                imageEdges = pp.edgesDet(image, 200, 250)
                closedEdges = cv2.morphologyEx(imageEdges, cv2.MORPH_CLOSE, np.ones((5, 11)))
                pageContour = pp.findPageContours(closedEdges, pp.resize(image))
                pageContour = pageContour.dot(pp.ratio(image))
                newImage = pp.perspImageTransform(image, pageContour)
                #Saving image to show status in the app
                save_filename = fileName[:-4]+"_1"+fileName[-4:]
                text_file=fileName[:-4]
                cv2.imwrite(save_filename, cv2.cvtColor(newImage, cv2.COLOR_BGR2RGB))
                ##Detect words using google-ocr
                if (parser.parse_args().google_ocr):
                        entities,bBoxes = go.convert(save_filename)
                        detected_filename = "input.txt"
                        with open(detected_filename, 'w') as outfile:
                                for i in entities:
                                        outfile.write(i)
                                        outfile.write("\n")
                        spell.spellcheck(dictionary, "./input.txt")
                        entities = []
                        with open("input.txt") as file:
                                entities = file.readlines()
                        entities = [x.strip() for x in entities]
                        save_filename = fileName[:-4]+"_2"+fileName[-4:]
                        

                else:
                        blurred = cv2.GaussianBlur(newImage, (5, 5), 18)
                        edgeImg = wd.edgeDetect(blurred)
                        ret, edgeImg = cv2.threshold(edgeImg, 50, 255, cv2.THRESH_BINARY)
                        bwImage = cv2.morphologyEx(edgeImg, cv2.MORPH_CLOSE, np.ones((20,20), np.uint8))

                        #bBoxes1 = wd.textDetect(bwImage, newImage)
                        wbBoxes = wd.textDetectWatershed(bwImage, newImage)
                #sug={"cormaffin":["abc1","abc2","abc3"],"Dolo":["abc1","abc2","abc3"]}
                file=open("input.txt","r")
                Lines = file.read().splitlines()
                file.close()
                file=open("input.txt","r")
                text_gen=str(file.read())
                #Lines = file.read().splitlines()
                rem1=""
                e = tk.Entry(relief=tk.GROOVE)
                e.grid(row=8, column=0, sticky=tk.NSEW)
                e.insert(tk.END, 'Prescribed medicine')
                window.columnconfigure(e,weight=1, uniform='third')
                e = tk.Entry(relief=tk.GROOVE)
                e.grid(row=8, column=1, sticky=tk.NSEW)
                e.insert(tk.END, 'Description')
                window.columnconfigure(e,weight=1, uniform='third')
                r=9
                meds=[]
                c=0
                for line in Lines:
                        if line in o_name:
                                if c==0:
                                        c=1
                                        meds.append(line)
                                else:
                                        if line in meds:
                                                continue
                                meds.append(line)
                                print(line)
                                index=o_name.index(line)
                                ds=desc[index]
                                ds=str(ds)
                                e = tk.Entry(relief=tk.GROOVE)
                                e.grid(row=r, column=0, sticky=tk.NSEW)
                                e.insert(tk.END,line)
                                window.columnconfigure(e,weight=1, uniform='third')
                                text_widget = tk.Text(window, wrap="word", relief=tk.GROOVE, width=20, height=1)
                                text_widget.grid(row=r, column=1, sticky=tk.NSEW)
                                text_widget.insert("1.0", ds)
                                window.columnconfigure(text_widget,weight=1, uniform='third')
                                play_button = tk.Button(window, text="Play",height = 2, width = 2, command=lambda t1=line,t2=ds: play_text(t1,t2))
                                play_button.grid(row=r, column=2, sticky=tk.NSEW)
                                window.columnconfigure(play_button, weight=1, uniform='third')
                                r+=1
                                
                        else:
                                pass
                if r<=9:
                        rem1="No medicines found(database referance)"
                        remedies1=tk.Label(text=rem1, background="pink",fg="Black", font=("", 12))
                        remedies1.grid(column=0, row=9, padx=10, pady=10)
                        

                        

                remedies2=tk.Label(text="Please visit doctor before having the medicine", background="pink",fg="Black", font=("", 12))
                remedies2.grid(column=0, row=r, padx=10, pady=10)
                button1 = tk.Button(text="Upload Photo", command = openphoto)
                button1.grid(column=0, row=r+1, padx=10, pady = 10)
                
	def openphoto():
            global fileName
            dirPath = "testpicture"
            fileList = os.listdir(dirPath)
            for fileName in fileList:
                os.remove(dirPath + "/" + fileName)
            # C:/Users/sagpa/Downloads/images is the location of the image which you want to test..... you can change it according to the image location you have  
            fileName = askopenfilename(initialdir=r'./', title='Select image for analysis ',
                                   filetypes=[('image files', '.jpg .jpeg')])
            dst = r"./testpicture"
            load = Image.open(fileName)
            load=load.resize((600, 400))
            render = ImageTk.PhotoImage(load)
            img = tk.Label(image=render, height="300", width="500")
            img.image = render
            img.place(x=0, y=0)
            img.grid(column=0, row=1, padx=10, pady = 10)
            title.destroy()
            button1.destroy()
            button2 = tk.Button(text="Convert", command=analysis)
            button2.grid(column=0, row=2)
	button1 = tk.Button(text="Get Photo", command = openphoto)
	button1.grid(column=0, row=1, padx=250, pady = 130)
	window.mainloop()





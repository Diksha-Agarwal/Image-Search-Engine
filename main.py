from flask import Flask, render_template, redirect, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
import re
import pyautogui
import fitz
from pathlib import Path
import os
import spacy
import en_core_web_lg
from PIL import Image
from pytesseract import pytesseract
import cv2
from collections import Counter
import numpy as np 
from werkzeug.utils import secure_filename


app = Flask(__name__)
# UPLOAD_FOLDER = r'./static/'
UPLOAD_FOLDER = 'D:\\WS\\majorProject\\main\\static'



app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
	return render_template('home.html')


@app.route('/view1', methods=['POST', 'GET'])
def view1():
	global branch, sem, y_n
	branch = request.form.get('branch-dropdown')  # takes 'name'
	sem = request.form.get('sem-dropdown')
	y_n = request.form.get('text')

	if (y_n.lower() == 'yes'): # ALREADY DOWNLOADED
		return render_template('view5.html')		 

	elif (y_n.lower() == 'no'): # AUTOMATIC DOWNLOAD
		# options = Options()
		# options.headless = True
		# driver = webdriver.Chrome('D:\\chromedriver_win32\\chromedriver_win32\\chromedriver.exe', options=options)
		driver = webdriver.Chrome('D:\\chromedriver_win32\\chromedriver_win32\\chromedriver.exe')
		driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
		  "source": """
		    Object.defineProperty(navigator, 'webdriver', {
		      get: () => undefined
		    })
		  """
		})

		# if branch == 'CSE':
		if sem == '1' or sem=='2':
			# link = 'https://www.osmaniaonline.com/#1y'
			driver.get('https://www.osmaniaonline.com/#1y')
			driver.maximize_window()
			bs = BeautifulSoup(driver.page_source, 'html.parser')
			actions = ActionChains(driver)
			driver.implicitly_wait(2)
			links = bs.find_all('a')
			l = list()
			names = list()
			

			# GETTING ALL LINKS
			for link in links:
				l.append(link.get('href'))

			for link in links:
				names.append(link.text)

			# print(len(names), '\n\n', names)
			# print(len(l), '\n\n', l)

			for i in range(43):
				names.pop(0)
				l.pop(0)

			for i in range(19):
				names.pop(-1)
				l.pop(-1)

			for j in l:
				driver.get(j)
				# DOWNLOAD LINK
				driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/h2/a').click()
				driver.implicitly_wait(3)
				pyautogui.hotkey('ctrl', 's')
				pyautogui.press('enter')

			i = len(l)-1
			while(i >= 0):
				driver.get(l[i])
				driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/h2/a').click()
				driver.implicitly_wait(3)
				pyautogui.hotkey('ctrl', 's')
				pyautogui.press('enter')
				i -= 1

		else:
			link = 'https://www.osmaniaonline.com/be-'+branch.lower()+'-question-papers.html#'+str(sem)+'s'

			driver.get(link)
			driver.maximize_window()
			bs = BeautifulSoup(driver.page_source, 'html.parser')
			actions = ActionChains(driver)
			driver.implicitly_wait(2)

			links = bs.find_all('a')
			l = list()
			names = list()
			global main_names_list
			main_names_list = list()
			main_list = list()

			# GETTING ALL LINKS
			for link in links:
				l.append(link.get('href'))
				

			for link in links:
				names.append(link.text)

			# LINKS FOR SPECIFIC SEMESTER
			for j in l:
				if re.search('https://www.osmaniaonline.com/papers/be-'+branch.lower()+'-'+str(sem)+'-sem', j):
					main_list.append(j)

			for k in names:
				if re.search('BE-'+branch+'-'+str(sem)+'-SEM', k):
					main_names_list.append(k)

			# DOWNLOADING FIRST HALF PAPERS
			for j in main_list:
				driver.get(j)
				# DOWNLOAD LINK
				try:
					driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/h2/a').click()
				except:
					continue
				driver.implicitly_wait(3)
				pyautogui.hotkey('ctrl', 's')
				pyautogui.press('enter')


			# DOWNLOADING OTHER HALF PAPERS
			i = len(main_list) - 1
			while(i >= 0):
				driver.get(main_list[i])
				driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/h2/a').click()
				driver.implicitly_wait(3)
				pyautogui.hotkey('ctrl', 's')
				pyautogui.press('enter')
				i -= 1

			

		return render_template('view5.html')


	else :
		return '<h1> ENTER CORRECT VALUE </h1>'


# ONLY FILE PATH.
@app.route('/view4', methods=['POST', 'GET'])
def view4():
	global pathh
	pathh = request.form.get('filepath')  

	return render_template('view5.html')


@app.route('/process', methods=['GET', 'POST'])
def process():
	img = request.files['query_img']  # displaying input image
	filename = secure_filename(img.filename)
	img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

	path_to_tesseract = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
	# Providing the tesseract executable
	# location to pytesseract library
	pytesseract.tesseract_cmd = path_to_tesseract
	NER = en_core_web_lg.load()

	img1 = Image.open('D:\\WS\\majorProject\\main\\static\\'+filename)
	text = pytesseract.image_to_string(img1)
	input_text = text.split('\n') # list of question(s) in input image

	# inp_image_array = np.asarray(r'./static/'+filename)
	inp_image_array = np.asarray(img1)
	flat_array1 = inp_image_array.flatten()
	RH1 = Counter(flat_array1)
	h1 = []

	for i in range(256):
		if i in RH1.keys():
			h1.append(i)
		else:
			h1.append(0)

	# Separating images

	directory = r'D:\\WS\\majorProject\\papers\\train\\'+branch+'\\'+str(sem)+'\\jpgs'
	file_list = [] # list of all the images after first classification
	for fname in os.listdir(directory):
		os.chdir(directory)
		# print('\n', directory+'\\'+fname, '\n')
		image = cv2.imread(directory+'\\'+fname)
		copy = Image.fromarray(image)
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		blur = cv2.GaussianBlur(gray, (7,7), 0)
		thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9)) #(3,13)
		dilate = cv2.dilate(thresh, kernel, iterations=2)
		cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if len(cnts) == 2 else cnts[1]
		cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0])

		score_list = []
		for c in cnts:
			x,y,w,h = cv2.boundingRect(c)
			roi = image[y:y+h, x:x+w]
			imgggg = Image.fromarray(roi) # taking the partitioned image

			test_array = np.asarray(imgggg)

			flat_array2 = test_array.flatten()

			RH2 = Counter(flat_array2)

			h2 = []
			for i in range(256):
				if i in RH2.keys():
					h2.append(i)
				else:
					h2.append(0)

			distance = 0
			for i in range(len(h1)):
				distance += np.square(h1[i] - h2[i])

			if (np.sqrt(distance) <= 220):
				text2 = pytesseract.image_to_string(imgggg)
				text2 = text2.split('\n')
				for i in input_text:
					if i != '':
						t1 = NER(i)
						for j in text2:
							if j != '':
								t2 = NER(j)
								z = t1.similarity(t2)
								if z >= 0.846:
									score_list.append(z)


			cv2.rectangle(image, (x,y), (x+w, y+h), (36,255,12), 2)


		if len(score_list) != 0:
			file_list.append(fname)
			copy.save(os.path.join('D:\\WS\\majorProject\\main\\static', fname))


	return render_template('inp_img.html', filename=filename, file_list=file_list)


if (__name__ == '__main__'):
	app.run(debug=True)

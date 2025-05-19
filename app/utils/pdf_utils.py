import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from scipy import ndimage
import numpy as np
import cv2
import math
import sys
import os
import easyocr
import torch
import matplotlib.pyplot as plt
from flask import current_app

# UPLOAD_FOLDER = os.path.join(app.config['UPLOAD_FOLDER'], '../uploads')
UPLOAD_FOLDER = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
PROCESSED_FOLDER = os.path.join(UPLOAD_FOLDER, "images")


def check_exiting_poppler():
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    poppler_path = (
        r"C:\Users\ProBook\Documents\PFA\Release-24.08.0-0\poppler-24.08.0\Library\bin"
    )

    if os.path.isdir(poppler_path):
        print("Poppler path exists!")
        return poppler_path
    else:
        print("Poppler path does not exist!")


def check_GPU():
    if torch.cuda.is_available():
        print(f"GPU available: {torch.cuda.device_count()} devices")
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    else:
        print("GPU is not available.")


def convert_pdf_to_images(pdf_path, poppler_path):
    """
    Part #1 : Converting PDF to images
    """
    if not os.path.exists(pdf_path):
        print("File does not exist!")
    else:
        print("File exists and ready for processing.")

    # Store all the pages of the PDF in a variable
    pages = convert_from_path(pdf_path, 350, poppler_path=poppler_path)

    # Counter to store images of each page of PDF to image
    image_counter = 1

    # Iterate through all the pages stored above
    for page in pages:
        # Declaring filename for each page of PDF as JPG
        # For each page, filename will be:
        # PDF page 1 -> page_1.jpg
        # PDF page 2 -> page_2.jpg
        # PDF page n -> page_n.jpg
        filename = PROCESSED_FOLDER + "/page_" + str(image_counter) + ".jpg"

        # Save image of the page in system
        page.save(filename, "JPEG")

        # Increase counter to update filename
        image_counter = image_counter + 1
    return image_counter


def recognising_text_from_images(image_counter, language, outfile_path):
    # Variable to get count of total number of pages
    filelimit = image_counter - 1

    # Create a text file to write the output
    # outfile = "../outputs/output_text.txt"

    # Open the file in append mode so that contents of all images are added to the same file
    f = open(outfile_path, "a", encoding="utf-8")

    # Iterate from 1 to the total number of pages
    for i in range(1, filelimit + 1):

        # Set filename to recognize text from
        # page_1.jpg
        # page_2.jpg
        # page_n.jpg
        filename = PROCESSED_FOLDER + "/page_" + str(i) + ".jpg"

        # # Load image and preprocess
        # img = cv2.imread(filename)
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]  # binarization
        # gray = cv2.medianBlur(gray, 3)

        # Optional: Save to verify output
        # cv2.imwrite(PROCESSED_FOLDER + "/cleaned_"+str(i)+".jpg", gray)

        # Load image and preprocess
        image = cv2.imread(filename)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)  # Noise reduction
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Save cleaned image (optional)
        cv2.imwrite(PROCESSED_FOLDER + "/cleaned_" + str(i) + ".jpg", gray)

        if language != "ar":
            text = get_text_by_tesseract(thresh, language)
        else:
            text = get_text_by_easyocr(filename, language)

        # Write the processed text to the file
        f.write(text)

    # Close the file after writing all the text
    f.close()
    return thresh


def get_text_by_tesseract(thresh, language):
    # Recognise the text as string in image using pytesserct
    # text = str(((pytesseract.image_to_string(Image.open(filename), lang="ara"))))  # or 'fra', 'ara', etc
    # custom_config = r'--oem 3 --psm 3 -l ara'
    custom_config = r"--oem 3 --psm 3 -l " + language
    # text = pytesseract.image_to_string(thresh, config=custom_config)

    # The recognized text is stored in variable text
    # Any string processing may be applied on text
    # Basic formatting has been performed
    # In many PDFs, if a word can't be written fully at line ending, a 'hyphen' is added
    # The rest of the word is written in the next line
    # Replace every '-\n' to '' to remove such hyphens
    # text = text.replace('-\n', '')
    return str(
        ((pytesseract.image_to_string(thresh, config=custom_config, lang=language)))
    )  # or 'fra', 'ara', etc


def get_text_by_easyocr(image_path, language="ar"):
    # reader = easyocr.Reader(['fr'])
    reader = easyocr.Reader([language])  # Arabic
    # results = reader.readtext('../uploads/images/page_1.jpg', paragraph=True, detail=0)
    # print("\n".join(results))
    return reader.readtext(image_path, paragraph=True, detail=0)


def mark_region(image_path):

    image = cv2.imread(image_path)

    # define threshold of regions to ignore
    THRESHOLD_REGION_IGNORE = 40

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 30
    )

    # Dilate to combine adjacent text contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    dilate = cv2.dilate(thresh, kernel, iterations=4)

    # Find contours, highlight text areas, and extract ROIs
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    line_items_coordinates = []
    for c in cnts:
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)

        if w < THRESHOLD_REGION_IGNORE or h < THRESHOLD_REGION_IGNORE:
            continue

        image = cv2.rectangle(
            image, (x, y), (x + w, y + h), color=(255, 0, 255), thickness=3
        )
        line_items_coordinates.append([(x, y), (x + w, y + h)])

    return image, line_items_coordinates

from django.shortcuts import render, HttpResponse
import os
import re
# import exceptions
# from docx import Document
from docx import Document
from PyPDF2 import *
from io import BytesIO
import json
# from pdfminer.high_level import extract_text
# Create your views here.
def home(request):
    # Function to extract text from a PDF document
    def extract_text_from_pdf(file_path):
        text = ""
        with open(file_path, "rb") as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()     # text += page.extract_text()
        return text

    # Function to extract text from a Word document
    def extract_text_from_word(file_path):
        doc = Document(file_path)
        return " ".join([para.text for para in doc.paragraphs])    


    if request.method == 'POST':
        # email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        email_pattern = re.compile(r'[\w.]+@\w+\.\w+')
        # phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}')
        phone_pattern = re.compile(r'\b(?:\+\d{1,2}\s*)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
        # name_pattern = re.compile(r'\b[A-Z][a-z]+[A-Z][a-z]+\b')
        # name_pattern = re.compile(r'[\w\s]+')
        name_pattern = re.compile(r'[^,\r\n]+')
        def extract_data_from_text(text):
            emails = email_pattern.findall(text)
            phones = phone_pattern.findall(text)
            names = name_pattern.findall(text)
            return {
                "emails": list(set(emails)),  # Remove duplicates
                "phones": list(set(phones)),
                "names": list(set(names)),
            }
        # Function to parse files in a directory
        def parse_files_in_directory(file_path):
            results = []
            if file_path.endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            if file_path.endswith(".docx"):
                text = extract_text_from_word(file_path)
            # elif file_path.endswith(".pdf"):
            #     text = extract_text_from_pdf(file_path)
            
            data = extract_data_from_text(text)
            results = [data["emails"], data["phones"], data["names"]]
            os.remove(file_path)
            return results

        uploaded_file = request.FILES.getlist('fileInput')
        data = []
        for file in uploaded_file:
            if file.name.endswith(".pdf"):
                print(file)
                with open('uploaded_file.pdf', 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                data.append(parse_files_in_directory('uploaded_file.pdf'))

            elif file.name.endswith(".docx"):
                print(file)
                with open('uploaded_file.docx', 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                data.append(parse_files_in_directory('uploaded_file.docx'))

        parsed_results = {
            "data": data
        }
        return HttpResponse(json.dumps(parsed_results))
        
    return render(request, 'app/base.html')
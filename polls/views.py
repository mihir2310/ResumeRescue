import os
import cv2
import pytesseract
import openai
import PyPDF2
from django.shortcuts import render
from django.http import HttpResponse
from .forms import uploadCVandJobDesc
from django.core.files.storage import FileSystemStorage
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
openai.api_key = os.getenv("OPEN_AI_TOKEN")

# Function to extract text from image using OpenCV and Tesseract
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

# Function to extract text from PDF using PyPDF2
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

# Function to get recommendations using OpenAI API
def get_recommendations(job_desc_text, resume_text):
    messages = [
        {"role": "user", "content": f"Given the following job description: {job_desc_text} and the following resume: {resume_text}, generate a recommendation paragraph that matches the resume to the job description."}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Updated model
        messages=messages,
        max_tokens=200
    )

    return response.choices[0]['message']['content'].strip()

# Home page view
def home_page(request):
    return render(request, 'base.html')

# View for file upload form
def upload_form(request):
    if request.method == 'POST':
        form = uploadCVandJobDesc(request.POST, request.FILES)
        if form.is_valid():
            # Save uploaded files
            job_desc_file = request.FILES['job_description']  # Image (Job Description)
            resume_file = request.FILES['resume_cv']  # PDF (Resume)

            # Use FileSystemStorage to handle files
            fs = FileSystemStorage()
            job_desc_filename = fs.save(job_desc_file.name, job_desc_file)
            resume_filename = fs.save(resume_file.name, resume_file)

            job_desc_filepath = fs.path(job_desc_filename)
            resume_filepath = fs.path(resume_filename)

            # Extract text based on file type
            if job_desc_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                job_desc_text = extract_text_from_image(job_desc_filepath)
            else:
                job_desc_text = "Invalid job description file format."

            if resume_filename.lower().endswith('.pdf'):
                resume_text = extract_text_from_pdf(resume_filepath)
            else:
                resume_text = "Invalid resume file format."

            # Generate recommendations
            recommendation = get_recommendations(job_desc_text, resume_text)

            # Clean up files (optional)
            fs.delete(job_desc_filename)
            fs.delete(resume_filename)

            # Pass the recommendation to a new page
            return render(request, 'recommendations.html', {
                'recommendation': recommendation
            })
        else:
            print(form.errors)  # For debugging, print the form errors
            return HttpResponse('Form is not valid! Please check your inputs.')
    else:
        form = uploadCVandJobDesc()
    return render(request, 'final.html', {'form': form})

def final_page(request):
    return render(request, 'final.html')

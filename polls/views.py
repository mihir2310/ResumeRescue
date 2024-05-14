# views.py

from django.shortcuts import render
from django.http import HttpResponse

def home_page(request):
    return render(request, 'base.html')  

def process_files(request):
    if request.method == 'POST' and 'file1' in request.FILES and 'file2' in request.FILES:
        file1 = request.FILES['file1']
        file2 = request.FILES['file2']
        print("hello World")
        
        # Read content of file1
        file1_content = file1.read().decode('utf-8')
        
        # Read content of file2
        file2_content = file2.read().decode('utf-8')
        
        # Process file1 with OpenAI API
        response1 = openai.Completion.create(
            engine="text-davinci-003",
            prompt=file1_content,
        )
        
        # Process file2 with OpenAI API
        response2 = openai.Completion.create(
            engine="text-davinci-003",
            prompt=file2_content,
        )
        
        # Perform your processing with the OpenAI API responses
        
        return render(request, 'final/')  
    
    else:
        return HttpResponse('File upload failed! Make sure you upload both files.')
    

def parse_job_description(request):
    pass

def parse_resume(request):
    pass




from django.shortcuts import render
from django.http import HttpResponse
from .utils import (
    extract_text_from_image,
    extract_key_requirements,
    analyze_resume_match,
    generate_recommendations
)
import PyPDF2
import io

def home(request):
    return render(request, 'base.html')

def upload(request):
    if request.method == 'POST':
        try:
            # Get the uploaded files
            job_description_file = request.FILES['job_description']
            resume_file = request.FILES['resume_cv']
            
            # Process job description image
            job_description_text = extract_text_from_image(job_description_file.read())
            job_requirements = extract_key_requirements(job_description_text)
            
            # Process resume PDF
            resume_text = ""
            if resume_file.name.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
            else:
                # Handle other file types if needed
                pass
            
            # Analyze the match
            analysis_results = analyze_resume_match(resume_text, job_requirements)
            
            # Generate recommendations
            recommendations = generate_recommendations(analysis_results)
            
            # Prepare context for template
            context = {
                'match_score': round(analysis_results['match_score']),
                'matching_skills': analysis_results['matching_skills'],
                'missing_skills': analysis_results['missing_skills'],
                'recommendations': recommendations
            }
            
            return render(request, 'final.html', context)
            
        except Exception as e:
            # Handle any errors during processing
            return render(request, 'final.html', {
                'form': {'errors': {'processing': str(e)}}
            })
    
    return HttpResponse("Method not allowed", status=405) 
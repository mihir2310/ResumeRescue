from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
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
            # Validate that both files are present
            if 'job_description' not in request.FILES or 'resume_cv' not in request.FILES:
                messages.error(request, 'Please upload both a job description and a resume.')
                return redirect('home')
            
            # Get the uploaded files
            job_description_file = request.FILES['job_description']
            resume_file = request.FILES['resume_cv']
            
            # Validate file types
            if not job_description_file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                messages.error(request, 'Job description must be a JPG or PNG image.')
                return redirect('home')
            
            if not resume_file.name.lower().endswith(('.pdf', '.doc', '.docx')):
                messages.error(request, 'Resume must be a PDF or Word document.')
                return redirect('home')
            
            # Process job description image
            job_description_text = extract_text_from_image(job_description_file.read())
            print("\n=== Extracted Job Description Text ===")
            print(job_description_text)
            print("\n=== End Job Description Text ===\n")
            
            job_requirements = extract_key_requirements(job_description_text)
            print("\n=== Extracted Requirements ===")
            print("\n".join(job_requirements))
            print("\n=== End Requirements ===\n")
            
            # Process resume
            resume_text = ""
            if resume_file.name.lower().endswith('.pdf'):
                try:
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                    for page in pdf_reader.pages:
                        resume_text += page.extract_text()
                    print("\n=== Extracted Resume Text ===")
                    print(resume_text)
                    print("\n=== End Resume Text ===\n")
                except Exception as e:
                    messages.error(request, 'Error reading PDF file. Please ensure it is not password protected.')
                    return redirect('home')
            else:
                # TODO: Add Word document processing
                messages.error(request, 'Word document processing not yet implemented. Please upload a PDF.')
                return redirect('home')
            
            if not resume_text.strip():
                messages.error(request, 'Could not extract text from the resume. Please try a different file.')
                return redirect('home')
            
            # Analyze the match
            analysis_results = analyze_resume_match(resume_text, job_requirements)
            print("\n=== Analysis Results ===")
            print(f"Match Score: {analysis_results['match_score']}%")
            print("\nMatching Skills:")
            print("\n".join(analysis_results['matching_skills']))
            print("\nMissing Skills:")
            print("\n".join(analysis_results['missing_skills']))
            print("\n=== End Analysis Results ===\n")
            
            # Generate recommendations
            recommendations = generate_recommendations(analysis_results)
            
            # Prepare context for template
            context = {
                'match_score': round(analysis_results['match_score']),
                'matching_skills': analysis_results['matching_skills'],
                'missing_skills': analysis_results['missing_skills'],
                'recommendations': recommendations,
                'job_description_text': job_description_text,  # Add this to see in template
                'resume_text': resume_text  # Add this to see in template
            }
            
            return render(request, 'final.html', context)
            
        except Exception as e:
            print(f"\nError during processing: {str(e)}\n")  # Debug print
            messages.error(request, f'An error occurred during processing: {str(e)}')
            return redirect('home')
    
    return HttpResponse("Method not allowed", status=405) 
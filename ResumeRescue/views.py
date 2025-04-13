from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .utils import (
    extract_text_from_image,
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
            print("\n=== Extracted Job Description Text ===")
            print(job_description_text)
            print("\n=== End Job Description Text ===\n")
            
            if not job_description_text.strip():
                messages.error(request, 'Could not extract text from the job description image. Please try a clearer image.')
                return redirect('home')
            
            # Process resume PDF
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
                messages.error(request, 'Please upload your resume in PDF format.')
                return redirect('home')
            
            if not resume_text.strip():
                messages.error(request, 'Could not extract text from the resume. Please try a different PDF.')
                return redirect('home')
            
            # Analyze the match using GPT (with fallback to basic analysis)
            analysis_results = analyze_resume_match(resume_text, job_description_text)
            
            print("\n=== Analysis Results ===")
            print(f"Match Score: {analysis_results['match_score']}%")
            print("\nMatching Skills:")
            print("\n".join(analysis_results['matching_skills']))
            print("\nMissing Skills:")
            print("\n".join(analysis_results['missing_skills']))
            if 'explanation' in analysis_results:
                print("\nExplanation:")
                print(analysis_results['explanation'])
            print("\n=== End Analysis Results ===\n")
            
            # Prepare context for template
            context = {
                'match_score': round(analysis_results['match_score']),
                'matching_skills': analysis_results['matching_skills'],
                'missing_skills': analysis_results['missing_skills'],
                'recommendations': analysis_results['recommendations'],
                'explanation': analysis_results.get('explanation', ''),
                'job_description_text': job_description_text,
                'resume_text': resume_text
            }
            
            return render(request, 'final.html', context)
            
        except Exception as e:
            print(f"\nError during processing: {str(e)}\n")
            messages.error(request, f'An error occurred during processing: {str(e)}')
            return redirect('home')
    
    return HttpResponse("Method not allowed", status=405) 
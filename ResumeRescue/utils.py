import cv2
import pytesseract
import numpy as np
from PIL import Image
import io

def preprocess_image(image_data):
    """Preprocess the image for better OCR results"""
    # Convert image data to numpy array
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Apply dilation to connect text components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    gray = cv2.dilate(gray, kernel, iterations=1)
    
    return gray

def extract_text_from_image(image_data):
    """Extract text from image using OCR"""
    # Preprocess the image
    processed_image = preprocess_image(image_data)
    
    # Perform OCR
    text = pytesseract.image_to_string(processed_image)
    
    return text.strip()

def extract_key_requirements(text):
    """Extract key requirements from the job description text"""
    # Common requirement keywords
    requirement_keywords = [
        'required', 'requirements', 'qualifications', 'skills', 'experience',
        'education', 'degree', 'certification', 'knowledge', 'ability',
        'proficiency', 'expertise', 'familiarity'
    ]
    
    # Split text into lines
    lines = text.split('\n')
    requirements = []
    
    # Find lines containing requirement keywords
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in requirement_keywords):
            # Clean up the line
            line = line.strip()
            if line and len(line) > 10:  # Filter out very short lines
                requirements.append(line)
    
    return requirements

def analyze_resume_match(resume_text, job_requirements):
    """Analyze how well the resume matches the job requirements"""
    matching_skills = []
    missing_skills = []
    
    # Convert both texts to lowercase for comparison
    resume_lower = resume_text.lower()
    
    for requirement in job_requirements:
        # Check if the requirement appears in the resume
        if any(word.lower() in resume_lower for word in requirement.split()):
            matching_skills.append(requirement)
        else:
            missing_skills.append(requirement)
    
    # Calculate match score
    total_requirements = len(job_requirements)
    if total_requirements > 0:
        match_score = (len(matching_skills) / total_requirements) * 100
    else:
        match_score = 0
    
    return {
        'match_score': match_score,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills
    }

def generate_recommendations(analysis_results):
    """Generate recommendations based on the analysis"""
    recommendations = []
    
    # Add recommendations for missing skills
    if analysis_results['missing_skills']:
        recommendations.append(
            "Consider adding the following requirements to your resume: " +
            ", ".join(analysis_results['missing_skills'][:3]) + 
            (" and more..." if len(analysis_results['missing_skills']) > 3 else "")
        )
    
    # Add general recommendations
    if analysis_results['match_score'] < 70:
        recommendations.append(
            "Your resume could be better aligned with the job requirements. " +
            "Consider highlighting more of the required skills and experience."
        )
    elif analysis_results['match_score'] >= 70 and analysis_results['match_score'] < 90:
        recommendations.append(
            "Your resume shows good alignment with the job requirements. " +
            "Consider adding a few more relevant skills to make it even stronger."
        )
    else:
        recommendations.append(
            "Great job! Your resume shows strong alignment with the job requirements."
        )
    
    return recommendations 
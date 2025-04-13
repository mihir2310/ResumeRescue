import cv2
import pytesseract
import numpy as np
from PIL import Image
import io
import re
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def preprocess_image(image_data):
    """Preprocess the image for better OCR results"""
    # Convert image data to numpy array
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(
        gray, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 
        2
    )
    
    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(binary)
    
    # Apply dilation to connect text components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,1))
    dilated = cv2.dilate(denoised, kernel, iterations=1)
    
    # Scale up the image (can help with OCR accuracy)
    scale_factor = 2
    scaled = cv2.resize(dilated, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    
    return scaled

def extract_text_from_image(image_data):
    """Extract text from image using OCR"""
    try:
        # Convert bytes to PIL Image first
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Preprocess the image
        processed_image = preprocess_image(cv2.imencode('.png', img_array)[1].tobytes())
        
        # Configure Tesseract parameters
        custom_config = r'--oem 3 --psm 6'
        
        # Perform OCR
        text = pytesseract.image_to_string(
            processed_image,
            config=custom_config,
            lang='eng'
        )
        
        # Clean up the text
        text = text.strip()
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        return text
    except Exception as e:
        print(f"Error in OCR processing: {str(e)}")
        return ""

def extract_key_requirements(text):
    """Extract key requirements from the job description text"""
    # Common section headers and requirement indicators
    section_headers = [
        'requirements', 'qualifications', 'skills', 'experience', 'education',
        'what you\'ll need', 'what we\'re looking for', 'your skills', 'your talents',
        'your objectives', 'responsibilities', 'about you', 'what you bring'
    ]
    
    # Split text into lines and clean them
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    requirements = []
    in_requirements_section = False
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Check if this line is a section header
        if any(header in line_lower for header in section_headers):
            in_requirements_section = True
            continue
            
        # If we're in a requirements section and the line is a bullet point or starts with a number
        if in_requirements_section and (
            line.startswith('•') or 
            line.startswith('-') or 
            line.startswith('*') or
            re.match(r'^\d+\.?\s', line) or
            len(line) > 20  # Also include longer lines that might be requirements
        ):
            # Clean up the requirement
            requirement = re.sub(r'^[•\-\*\d\.]+\s*', '', line).strip()
            if requirement and len(requirement) > 10:  # Filter out very short lines
                requirements.append(requirement)
                
        # If we hit another section header or a very short line, end the requirements section
        elif in_requirements_section and (len(line) < 20 or line.endswith(':')):
            in_requirements_section = False
    
    # If no requirements were found using section headers, try to extract any bullet points
    if not requirements:
        for line in lines:
            if (line.startswith('•') or 
                line.startswith('-') or 
                line.startswith('*') or
                re.match(r'^\d+\.?\s', line)):
                requirement = re.sub(r'^[•\-\*\d\.]+\s*', '', line).strip()
                if requirement and len(requirement) > 10:
                    requirements.append(requirement)
    
    return requirements

def analyze_with_gpt(job_description, resume_text):
    """Use GPT to analyze the match between resume and job description"""
    try:
        prompt = f"""
        You are an expert resume analyzer and career coach. Analyze how well the candidate's resume matches the job description.
        Focus on both technical skills and soft skills. Consider experience level, education, and specific achievements.
        
        Job Description:
        {job_description}

        Resume:
        {resume_text}

        Provide a detailed analysis in the following JSON format:
        {{
            "match_score": <number between 0-100>,
            "matching_skills": [<list of skills/qualifications that match>],
            "missing_skills": [<list of required skills/qualifications that are missing or need strengthening>],
            "recommendations": [<specific, actionable recommendations to improve the resume>],
            "explanation": "<brief explanation of the score and key factors>"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert resume analyzer focusing on tech roles."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )

        # Parse the response
        analysis = eval(response.choices[0].message.content)
        return analysis

    except Exception as e:
        print(f"Error in GPT analysis: {str(e)}")
        # Fall back to basic analysis if GPT fails
        return analyze_resume_match_basic(resume_text, extract_key_requirements(job_description))

def analyze_resume_match(resume_text, job_description):
    """Main analysis function that tries GPT first, falls back to basic analysis"""
    try:
        # Try GPT analysis first
        return analyze_with_gpt(job_description, resume_text)
    except Exception as e:
        print(f"Falling back to basic analysis due to error: {str(e)}")
        # Fall back to basic analysis
        return analyze_resume_match_basic(resume_text, extract_key_requirements(job_description))

def analyze_resume_match_basic(resume_text, job_requirements):
    """Basic analysis as fallback when GPT is unavailable"""
    matching_skills = []
    missing_skills = []
    
    # Convert resume text to lowercase and split into words
    resume_lower = resume_text.lower()
    resume_words = set(re.findall(r'\b\w+\b', resume_lower))
    
    for requirement in job_requirements:
        requirement_lower = requirement.lower()
        # Split requirement into key terms
        key_terms = re.findall(r'\b\w+\b', requirement_lower)
        
        # Calculate how many key terms from the requirement appear in the resume
        matching_terms = sum(1 for term in key_terms if term in resume_words)
        # Consider it a match if more than 50% of the key terms are found
        if matching_terms >= len(key_terms) * 0.5:
            matching_skills.append(requirement)
        else:
            missing_skills.append(requirement)
    
    # Calculate match score with more weight given to technical skills
    total_requirements = len(job_requirements)
    if total_requirements > 0:
        # Base score from matching requirements
        base_score = (len(matching_skills) / total_requirements) * 100
        
        # Bonus points for technical skills
        tech_keywords = {'python', 'java', 'javascript', 'c++', 'programming',
                        'software', 'development', 'engineering', 'computer science',
                        'database', 'api', 'cloud', 'aws', 'azure', 'machine learning'}
        tech_matches = sum(1 for word in resume_words if word in tech_keywords)
        tech_bonus = min(20, tech_matches * 2)  # Up to 20% bonus for technical skills
        
        match_score = min(100, base_score + tech_bonus)
    else:
        match_score = 0
    
    return {
        'match_score': match_score,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'recommendations': generate_recommendations({
            'match_score': match_score,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills
        }),
        'explanation': "Analysis performed using basic keyword matching."
    }

def generate_recommendations(analysis_results):
    """Generate recommendations based on the analysis"""
    recommendations = []
    
    # Add specific recommendations for missing skills
    if analysis_results['missing_skills']:
        recommendations.append(
            "Consider highlighting these key requirements in your resume: " +
            ", ".join(analysis_results['missing_skills'][:3]) + 
            (" and more..." if len(analysis_results['missing_skills']) > 3 else "")
        )
    
    # Add general recommendations based on score
    if analysis_results['match_score'] < 50:
        recommendations.append(
            "Your resume needs significant alignment with the job requirements. " +
            "Try to incorporate more relevant skills and experiences that match the position."
        )
    elif analysis_results['match_score'] < 70:
        recommendations.append(
            "Your resume shows moderate alignment with the job requirements. " +
            "Consider restructuring your resume to better highlight relevant experiences."
        )
    elif analysis_results['match_score'] < 90:
        recommendations.append(
            "Your resume shows good alignment with the job requirements. " +
            "Consider adding a few more specific examples of your relevant skills."
        )
    else:
        recommendations.append(
            "Excellent match! Your resume is well-aligned with the job requirements. " +
            "Make sure to prepare specific examples of your experiences for the interview."
        )
    
    return recommendations 
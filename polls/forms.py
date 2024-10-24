from django import forms
from .models import UploadedFiles

class uploadCVandJobDesc(forms.ModelForm):
    class Meta:
        model = UploadedFiles
        fields = ['job_description', 'resume_cv']
    
    def clean_job_description(self):
        job_desc_file = self.cleaned_data.get('job_description')
        if job_desc_file:
            # Check if the uploaded file is an image (PNG, JPG, etc.)
            if not job_desc_file.content_type.startswith('image/'):
                raise forms.ValidationError("Job description must be an image file (PNG, JPG, etc.)")
        return job_desc_file

    def clean_resume_cv(self):
        resume_file = self.cleaned_data.get('resume_cv')
        if resume_file:
            # Check if the uploaded file is a PDF
            if not resume_file.content_type == 'application/pdf':
                raise forms.ValidationError("Resume must be a PDF file")
        return resume_file

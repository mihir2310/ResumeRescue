from django.db import models

class UploadedFiles(models.Model):
    id = models.AutoField(primary_key=True)
    job_description = models.FileField(upload_to='uploads/')
    resume_cv = models.FileField(upload_to='uploads/')

    class Meta:
        app_label = 'ResumeRescue'

    def __str__(self):
        return f"Upload {self.id}: {self.job_description.name}, {self.resume_cv.name}"

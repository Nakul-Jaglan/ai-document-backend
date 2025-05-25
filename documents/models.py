from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file type. Only PDF, DOC, and DOCX files are allowed.')

class Document(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/', validators=[validate_file_extension])
    file_type = models.CharField(max_length=10)
    size = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-uploaded_at']

    def clean(self):
        if self.file:
            if self.file.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError('File size cannot exceed 10MB.')

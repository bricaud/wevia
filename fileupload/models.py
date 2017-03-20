from django.db import models
from django.utils import timezone 
from django.conf import settings
UPLOAD_PATH = settings.UPLOAD_PATH

class UploadFile(models.Model):
	file = models.FileField(upload_to=UPLOAD_PATH)
	created = models.DateTimeField(default=timezone.now)
	description = models.CharField(max_length=255, blank=True)
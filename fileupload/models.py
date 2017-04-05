from django.db import models
from django.utils import timezone 
from django.conf import settings
UPLOAD_PATH = settings.UPLOAD_PATH

class Document(models.Model):
	file = models.FileField(upload_to=UPLOAD_PATH)
	name = models.CharField(max_length=255, blank=True)
	created = models.DateTimeField(default=timezone.now)
	text_date = models.DateTimeField(null=True, blank=True)
	last_modified = models.DateTimeField(null=True, blank=True)
	description = models.CharField(max_length=255, blank=True)
	text = models.TextField(blank=True)
	path = models.CharField(max_length=255, blank=True)
	png_path = models.CharField(max_length=255, blank=True)
	txt_path = models.CharField(max_length=255, blank=True)
	extract_error = models.IntegerField(default=10)
	txt_error = models.IntegerField(default=10)
	nb_pages = models.IntegerField(default=0)
	cluster = models.ForeignKey(to='classif.Cluster', related_name="elements",
		null=True, blank=True, on_delete=models.SET_NULL, default=None)
	class Meta:
		ordering = ('name',)

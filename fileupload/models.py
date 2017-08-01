from django.db import models
from django.utils import timezone 
from django.conf import settings
import os,warnings


class Document(models.Model):
	file = models.FileField(upload_to=settings.UPLOAD_PATH)
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
	#is_classified = models.BooleanField(default=False)
	cluster = models.ForeignKey(to='classif.Cluster', related_name="elements",
		null=True, blank=True, on_delete=models.SET_NULL, default=None)
	is_in_graph = models.BooleanField(default=False)

	def get_cluster_id(self):
		try:
			cluster_id = self.cluster.number
		except:
			print('Warning: document {} does not belong to any cluster. Please run the classification.'
				.format(self.name))
			cluster_id = -1
		return cluster_id

	def get_url(self):
		if os.path.isfile(self.file.path):
			return self.file.url
		else:
			warnMessage = ('Cannot find file for database entry. Document: "{}".'.format(self.name) +
			' You may need to clean the database.')
			warnings.warn(warnMessage)
			return None

	class Meta:
		ordering = ('name',)

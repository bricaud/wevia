from django.db import models
from django.core import validators
from fileupload.models import Document
import json

class Cluster(models.Model):
	name = models.CharField(max_length=255, blank=True)
	confidence = models.IntegerField()
	sharedWords = models.CharField(validators=[validators.validate_comma_separated_integer_list], max_length=4096)

	def load_sharedWords(self,list_to_load):
		self.sharedWords = json.dumps(list_to_load)

	def get_sharedWords(self):
		return json.loads(self.sharedWords)

	class Meta:
		ordering = ('name',)
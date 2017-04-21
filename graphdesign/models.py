from django.db import models
from django.core import validators
from fileupload.models import Document
import json

class GraphNode(models.Model):
	# Each node of the graph of words (and expressions) is 
	# stored as a GraphNode object in the Django database
	name = models.CharField(max_length=255, blank=True)
	documents = models.ManyToManyField(Document, through='DocumentIndex')
	class Meta:
		ordering = ('name',)

class DocumentIndex(models.Model):
	# Connecting words and expressions with the documents they appear in. 
	document = models.ForeignKey(Document, on_delete=models.CASCADE)
	graphnode = models.ForeignKey(GraphNode, on_delete=models.CASCADE)
	positions_in_document = models.CharField(validators=[validators.validate_comma_separated_integer_list], max_length=2048)

	def load_list(self,list_to_load):
		self.positions_in_document = json.dumps(list_to_load)

	def get_list(self):
		return json.loads(self.positions_in_document)

	class Meta:
		ordering = ('positions_in_document',)

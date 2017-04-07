from django.shortcuts import render

import os
#from django.conf import settings
from classif.models import Cluster
from fileupload.models import Document
from graphdesign.models import GraphNode



def index(request):
	output = ''
	if(request.GET.get('check_db')):
		output = run_check_db()
	if(request.GET.get('clean_db')):
		output = run_clean_db()
	if(request.GET.get('erase_db')):
		output = run_erase_db()
	return render(request,'advancedSettings/advanced_settings.html',
		{'console_message' :output})

def run_check_db():
	try:
		clusters = Cluster.objects.all() # lazy implementation (not evaluated)
		nb_clusters = len(clusters) # needed to evaluate the line above
	except:
		print("Database corrupted (can't access 'Cluster' object). Please re-install.")
		return "Database corrupted (can't access 'Cluster' object). Please re-install."
	try:
		expressions = GraphNode.objects.all()
		nb_expressions = len(expressions)
	except:
		print("Database corrupted (can't access 'GraphNode' object). Please re-install.")
		return "Database corrupted (can't access 'GrpahNode' object). Please re-install."
	# Delete only documents that are not associated to a file:
	try: 
		document_set = Document.objects.all()
		nb_documents = len(document_set)
	except:
		print("Database corrupted (can't access 'Document' object). Please re-install.")
		return "Database corrupted (can't access 'Document' object). Please re-install."
	doc_no_file = 0
	docname_no_file = []
	for doc in document_set:
		if doc.file == '' or not os.path.isfile(doc.file.path):
			doc_no_file+=1
			docname_no_file.append(doc.name)
	return ("""{} documents, {} words and expressions, {} clusters in database."""
		.format(nb_documents,nb_expressions,nb_clusters)+
		' {} document(s) not associated to a file {}.'.format(doc_no_file,docname_no_file))


def run_clean_db():
	Cluster.objects.all().delete()
	GraphNode.objects.all().delete()
	# Delete only documents that are not associated to a file: 
	document_set = Document.objects.all()
	for doc in document_set:
		if doc.file == '' or not os.path.isfile(doc.file.path):
			doc.delete()
	return 'Database cleaned.'

def run_erase_db():
	Cluster.objects.all().delete()
	Document.objects.all().delete()
	GraphNode.objects.all().delete()
	return 'Database erased.'
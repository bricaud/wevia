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
	clusters = Cluster.objects.all()
	nb_clusters = len(clusters)
	expressions = GraphNode.objects.all()
	nb_expressions = len(expressions)
	# Delete only documents that are not associeted to a file: 
	document_set = Document.objects.all()
	nb_documents = len(document_set)
	doc_no_file = 0
	for doc in document_set:
		if not os.path.isfile(doc.file.path):
			doc_no_file+=1
	return ('{} documents, {} words and expressions, {} clusters in database.'.format(nb_documents,nb_expressions,nb_clusters)+
		' {} document(s) not associated to a file.'.format(doc_no_file))


def run_clean_db():
	Cluster.objects.all().delete()
	GraphNode.objects.all().delete()
	# Delete only documents that are not associeted to a file: 
	document_set = Document.objects.all()
	for doc in document_set:
		if not os.path.isfile(doc.file.path):
			doc.delete()
	return 'Database cleaned.'

def run_erase_db():
	Cluster.objects.all().delete()
	Document.objects.all().delete()
	GraphNode.objects.all().delete()
	return 'Database erased.'
from django.shortcuts import render

import os
#from django.conf import settings
from classif.models import Cluster
from fileupload.models import Document
from graphdesign.models import GraphNode

import grevia.wordgraph as wordgraph
import grevia.g_gremlin as graphdatabase



def index(request):
	output = ''
	if(request.GET.get('check_db')):
		output = run_check_db()
	if(request.GET.get('clean_db')):
		output = run_clean_db()
	if(request.GET.get('erase_db')):
		output = run_erase_db()
	if(request.GET.get('check_graphdb')):
		output = run_check_graphdb()
	if(request.GET.get('clean_graphdb')):
		output = run_clean_graphdb()
	if(request.GET.get('erase_graphdb')):
		output = run_erase_graphdb()
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
		return "Database corrupted (can't access 'GraphNode' object). Please re-install."
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
	return 'Database cleaned. (document objects with no associated file have been removed).'

def run_erase_db():
	Cluster.objects.all().delete()
	Document.objects.all().delete()
	GraphNode.objects.all().delete()
	return 'Database erased.'


#############################################
#### Graphe database

def run_check_graphdb():
	try:
		graph_object = graphdatabase.DiGraph() 
	except:
		message = "Cannot access the graph database. Please check the Gremlin server."
		print(message)
		return message	
	return ("""Graph with {} nodes and {} edges."""
		.format(graph_object.number_of_nodes(),graph_object.number_of_edges()))

def run_clean_graphdb():
	message = run_check_graphdb()
	if message.startswith('Cannot'):
		return message
	graph = graphdatabase.DiGraph()
	list_of_nodes = graph.list_of_nodes(data=False)
	removed_nodes = 0
	for node in list_of_nodes:
		if not graph.node_is_ok(node):
			graph.remove_node(node)
			removed_nodes +=1
	return 'Database cleaned. {} nodes removed.'.format(removed_nodes)

def run_erase_graphdb():
	try:
		graph_object = graphdatabase.DiGraph()
		graph_object.remove_all()
	except:
		message = "Cannot access the graph database. Please check the Gremlin server."
		print(message)
		return message	
	return 'Database erased.'
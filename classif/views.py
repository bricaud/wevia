from django.shortcuts import render
import commands.eviascripts as cevia
import sys
from contextlib import redirect_stdout 
import io 
import os
from django.conf import settings
from classif.models import Cluster
from fileupload.models import Document
import grevia

stdoutstream = io.StringIO()




def index(request):
	num_var = 0
	output = ''
	evia_paths = cevia.EviaPaths(settings.PDF_PATH)
	if(request.GET.get('run_classify')):
		output = run_classify(evia_paths)
	return render(request,'classify_template.html',
		{'console_message' :output, 'loading':'False'})

	
def run_classify(paths_objects):
	#global stdoutstream
	print('Running classification.')
	#with redirect_stdout(stdoutstream):
	#	output = cevia.run_classify_db(paths_objects)
	output = cevia.run_classify_db(paths_objects)
	return output

def classify_in_folders(paths_object):
	#global stdoutstream
	print('Classifying clusters into folders.')
	#with redirect_stdout(stdoutstream):
	#	output = cevia.csv2folders(paths_object)
	output = cevia.csv2folders(paths_object)
	return output

def request_output_page(request):
	global stdoutstream
	evia_paths = cevia.EviaPaths(settings.PDF_PATH)
	text = '{}'.format(stdoutstream.getvalue())
	text = text.split('\n')
	return render(request,'outputs_classify.html',{'output_messages' :text})
	#return HttpResponse("Hello, world. You're at the commands page.")

def request_display_classif(request):
	clusters = Cluster.objects.all()
	cluster_dic = {}
	clusters_info_dic = {}
	for cluster in clusters:
		doc_list = []
		cluster_dic[cluster.number] = {}
		clusters_info_dic[cluster.number] = {}
		c_documents = Document.objects.filter(cluster=cluster)
		cluster_dic[cluster.number]['confidence'] = '{}%'.format(cluster.confidence)#'{.0f}%'.format(cluster.confidence*100)
		clusters_info_dic[cluster.number]['shared_words'] = cluster.get_sharedWords()
		#print(clusters_info_dic[cluster.name]['shared_words'])
		#url = os.path.join(settings.MEDIA_ROOT,doc.file.url)
		#[doc_list.append((doc.name,'file://' + os.path.join(settings.MEDIA_ROOT,doc.file.url))) for doc in c_documents]
		[doc_list.append([doc.name,os.path.join('../../',doc.file.url)]) for doc in c_documents]
		cluster_dic[cluster.number]['doc_list'] = doc_list
	#return render(request,'results_classif.html',{'csv_table' : csv_table, 'console_message' : console_message})
	return render(request,'results_classif.html',{'csv_table' : sorted(cluster_dic.items()), 
		'clusters_info' : sorted(clusters_info_dic.items())})


def request_groups_of_files(request):
	clusters_list = Cluster.objects.all()
	cluster_id_list = [cluster.number for cluster in clusters_list]
	# First process unclassified docs if any
	unclassif_docs = Document.objects.filter(cluster=None)
	# load the graph
	try:
		docgraph = grevia.docgraph.Graph.load(settings.DOC_GRAPH_PATH)
	except:
		print('Document graph file "{}" not found, creating a new graph.'.format(settings.DOC_GRAPH_PATH))
		docgraph = grevia.docgraph.Graph()

	for uc_doc in unclassif_docs:
		clusters_list = Cluster.objects.all()
		cluster_id_list = [cluster.number for cluster in clusters_list]
		print(uc_doc.name)
		docgraph,cluster_score = add_to_classif(uc_doc,docgraph)
		new_cluster = compute_cluster_id(cluster_score,cluster_id_list)
		# Save the cluster info on the graph
		node = docgraph.get_node(int(uc_doc.id))
		node.cluster = new_cluster.number
		docgraph.save_node(node)

		cluster_keywords_form_doc = get_cluster_keywords(uc_doc,new_cluster.number,docgraph)
		cluster_keywords = new_cluster.get_sharedWords()
		cluster_keywords += cluster_keywords_form_doc
		new_cluster.load_sharedWords(cluster_keywords)
		new_cluster.save()
		uc_doc.cluster = new_cluster
		uc_doc.save()
	docgraph.save(settings.DOC_GRAPH_PATH)
	cluster_dic = {}
	clusters_info_dic = {}
	for cluster in clusters_list:
		doc_list = []
		cluster_dic[cluster.number] = {}
		clusters_info_dic[cluster.number] = {}
		c_documents = Document.objects.filter(cluster=cluster)
		cluster_dic[cluster.number]['confidence'] = '{}%'.format(cluster.confidence)#'{.0f}%'.format(cluster.confidence*100)
		cluster_dic[cluster.number]['color'] = cevia.set_cluster_color(cluster.number)
		[doc_list.append([doc.name,os.path.join('../../',doc.file.url)]) for doc in c_documents]
		cluster_dic[cluster.number]['doc_list'] = doc_list
	return render(request,'groups_of_files.html',{'csv_table' : sorted(cluster_dic.items()), 
		'clusters_info' : sorted(clusters_info_dic.items())})


def add_to_classif(document,docgraph):
	doc_node = grevia.docgraph.Node(document.id)
	docgraph.save_node(doc_node)
	# preprocess similarity
	similarity_data = document.get_similarity()
	doc_id = str(document.id)
	node_selfweight = similarity_data[doc_id]
	del similarity_data[doc_id]
	# create the edges and get cluster score
	cluster_score = {}
	for node_id,keywords in similarity_data.items():
		node_id = int(node_id)
		if not docgraph.has_node(node_id):
			n_node = grevia.docgraph.Node(node_id)
			docgraph.save_node(n_node)
		edge_weight = len(keywords)/node_selfweight
		edge = grevia.docgraph.Edge(document.id,node_id,edge_weight,keywords)
		docgraph.save_edge(edge)
		node = docgraph.get_node(int(node_id))
		if not node.cluster in cluster_score:
			cluster_score[node.cluster] = 0
		cluster_score[node.cluster] += edge_weight
	return docgraph,cluster_score
	


def compute_cluster_id(cluster_score,cluster_id_list):
	if cluster_score:
		best_cluster_number_list = sorted(cluster_score, key=(lambda k: cluster_score[k]),reverse=True)
		best_cluster_number = best_cluster_number_list[0]
		if best_cluster_number==-1 and len(best_cluster_number_list)>1:
			best_cluster_number = best_cluster_number_list[1]
		# in case the score is too low, create a new cluster
		threshold = 0.2
		print(cluster_score[best_cluster_number])
		if cluster_score[best_cluster_number]>threshold and best_cluster_number!=-1:
			best_cluster = Cluster.objects.get(number=best_cluster_number)
			return best_cluster
		s_c_list = sorted(cluster_id_list)
		new_cluster_id = s_c_list[-1]+1
		return Cluster(name='Cluster_'+str(new_cluster_id), number=int(new_cluster_id), confidence=100)
	else:
		if cluster_id_list:
			s_c_list = sorted(cluster_id_list)
			new_cluster_id = s_c_list[-1]+1
		else:
			new_cluster_id = 1
		return Cluster(name='Cluster_'+str(new_cluster_id), number=int(new_cluster_id), confidence=100)


def get_cluster_keywords(document,cluster_number,docgraph):
	neigh = docgraph.neighbors(document.id)
	incluster_keywords = []
	outcluster_keywords = []
	for node_id in neigh:
		node = docgraph.get_node(node_id)
		edge = docgraph.get_edge(document.id,node.doc_id)
		if node.cluster == cluster_number:
			[incluster_keywords.append(keyword) for keyword in edge.shared_words]
		else:
			[outcluster_keywords.append(keyword) for keyword in edge.shared_words]
	for expr in outcluster_keywords:
		if expr in incluster_keywords:
			incluster_keywords.pop(incluster_keywords.index(expr))
	return incluster_keywords



#################### Database cluster info
def dbinfo(request,cluster_query):
	try:
		entry = Cluster.objects.get(number=cluster_query)
	except:
		print('Cluster {} not found.'.format(cluster_query))
		return render(request,'dbinfo.html',
		{ 'document': {},'query': cluster_query})

	return render(request,'dbinfo.html',
		{ 'document': sorted(entry.__dict__.items()),'query': cluster_query})



## DEPRECATED
"""
def request_display_csv(request):
	evia_paths = cevia.EviaPaths(settings.PDF_PATH)
	csv_table,console_message = get_csv(evia_paths)
	print(console_message)
	#return render(request,'results_classif.html',{'csv_table' : csv_table, 'console_message' : console_message})
	return render(request,'results_classif.html',{'csv_table' : sorted(csv_table.items()),
		'pdf_path' : PDF_PATH,  'console_message' : console_message})


def get_csv(paths_object):
	global stdoutstream
	print('Loading CSV.')
	with redirect_stdout(stdoutstream):
		data_dic,console_message = cevia.get_csv(paths_object)
	return data_dic,console_message
"""
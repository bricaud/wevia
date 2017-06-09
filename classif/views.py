from django.shortcuts import render
import commands.eviascripts as cevia
import sys
from contextlib import redirect_stdout 
import io 
import os
from django.conf import settings
from classif.models import Cluster
from fileupload.models import Document


stdoutstream = io.StringIO()


def index(request):
	num_var = 0
	output = ''
	graph_threshold = 8
	evia_paths = cevia.EviaPaths(settings.PDF_PATH)
	if(request.GET.get('run_classify')):
		output = run_classify(evia_paths)
	if(request.GET.get('classify_in_folders')):
		output = classify_in_folders(evia_paths)
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
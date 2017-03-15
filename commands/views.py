from django.shortcuts import render
from django.http import HttpResponse
import commands.eviascripts as cevia
import sys
from contextlib import redirect_stdout 
import io 

stdoutstream = io.StringIO()
PDF_PATH = '/media/benjamin/Largo/testspdfs'

def index(request):
	return HttpResponse("Hello, world. You're at the commands page.")


def request_page(request):
	global PDF_PATH
	num_var = 0
	output = ''
	graph_threshold = 8
	evia_paths = cevia.EviaPaths(PDF_PATH)
	if(request.GET.get('run_pdf2txt')):
		output = run_pdf2txt(evia_paths)
	if(request.GET.get('make_graph')):
		graph_threshold = int(request.GET.get('graph_threshold'))
		output = make_graph(graph_threshold,evia_paths)
		print(output)
		#output = request_output(request)
	if(request.GET.get('run_classify')):
		output = run_classify(evia_paths)
	if(request.GET.get('classify_in_folders')):
		output = classify_in_folders(evia_paths)
	return render(request,'commands/wevia_template.html',
		{'console_message' :output, 'loading':'False', 'graph_threshold' : graph_threshold})


def make_graph(graph_threshold,paths_object):
	global stdoutstream
	with redirect_stdout(stdoutstream):
		output = cevia.make_graph(graph_threshold,paths_object)
	print('Console message: '+output)
	return output


def run_pdf2txt(paths_objects):
	global stdoutstream
	with redirect_stdout(stdoutstream):
		output = cevia.run_pdf2txt(paths_objects)
	return output

	
def run_classify(paths_objects):
	global stdoutstream
	print('Running classification.')
	with redirect_stdout(stdoutstream):
		output = cevia.run_classify(paths_objects)
	return output


def request_output_page(request):
	global stdoutstream, PDF_PATH
	evia_paths = cevia.EviaPaths(PDF_PATH)
	text = '{}'.format(stdoutstream.getvalue())
	text = text.split('\n')
	return render(request,'commands/outputs.html',{'output_messages' :text})
	#return HttpResponse("Hello, world. You're at the commands page.")

def request_display_csv(request):
	global PDF_PATH
	evia_paths = cevia.EviaPaths(PDF_PATH)
	csv_table,console_message = get_csv(evia_paths)
	print(console_message)
	return render(request,'commands/results.html',{'csv_table' : csv_table, 'console_message' : console_message})

def get_csv(paths_object):
	global stdoutstream
	print('Loading CSV.')
	with redirect_stdout(stdoutstream):
		data_dic,console_message = cevia.get_csv(paths_object)
	return data_dic,console_message

def classify_in_folders(paths_object):
	global stdoutstream
	print('Classifying clusters into folders.')
	with redirect_stdout(stdoutstream):
		output = cevia.csv2folders(paths_object)
	return output

def make_search(searchquery,paths_object):
	print('starting the search, keyword: {}'.format(searchquery))	
	search_results,console_message = cevia.make_search(searchquery,paths_object)
	print(console_message)
	return search_results,console_message
	
def request_search_results(request):
	global PDF_PATH
	evia_paths = cevia.EviaPaths(PDF_PATH)
	searchquery = ''
	search_results = {}
	console_message = ''	
	if(request.GET.get('make_search')):
		searchquery = str(request.GET.get('search'))
		search_results,console_message = make_search(searchquery,evia_paths)
	return render(request,'commands/searchresults.html',
		{ 'query':searchquery, 'search_results' :search_results, 'console_message' : console_message})

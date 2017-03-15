from django.shortcuts import render
import commands.eviascripts as cevia
import sys
from contextlib import redirect_stdout 
import io 

stdoutstream = io.StringIO()
PDF_PATH = '/media/benjamin/Largo/testspdfs'

def index(request):
	global PDF_PATH
	num_var = 0
	output = ''
	graph_threshold = 8
	evia_paths = cevia.EviaPaths(PDF_PATH)
	if(request.GET.get('run_classify')):
		output = run_classify(evia_paths)
	if(request.GET.get('classify_in_folders')):
		output = classify_in_folders(evia_paths)
	return render(request,'classify_template.html',
		{'console_message' :output, 'loading':'False'})

	
def run_classify(paths_objects):
	global stdoutstream
	print('Running classification.')
	with redirect_stdout(stdoutstream):
		output = cevia.run_classify(paths_objects)
	return output

def classify_in_folders(paths_object):
	global stdoutstream
	print('Classifying clusters into folders.')
	with redirect_stdout(stdoutstream):
		output = cevia.csv2folders(paths_object)
	return output

def request_output_page(request):
	global stdoutstream, PDF_PATH
	evia_paths = cevia.EviaPaths(PDF_PATH)
	text = '{}'.format(stdoutstream.getvalue())
	text = text.split('\n')
	return render(request,'outputs_classify.html',{'output_messages' :text})
	#return HttpResponse("Hello, world. You're at the commands page.")

def request_display_csv(request):
	global PDF_PATH
	evia_paths = cevia.EviaPaths(PDF_PATH)
	csv_table,console_message = get_csv(evia_paths)
	print(console_message)
	return render(request,'results_classif.html',{'csv_table' : csv_table, 'console_message' : console_message})

def get_csv(paths_object):
	global stdoutstream
	print('Loading CSV.')
	with redirect_stdout(stdoutstream):
		data_dic,console_message = cevia.get_csv(paths_object)
	return data_dic,console_message
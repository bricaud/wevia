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
	if(request.GET.get('run_pdf2txt')):
		output = run_pdf2txt(evia_paths)
	return render(request,'extraction_template.html',
		{'console_message' :output, 'loading':'False'})


def run_pdf2txt(paths_objects):
	global stdoutstream
	with redirect_stdout(stdoutstream):
		output = cevia.run_pdf2txt(paths_objects)
	return output

def request_output_page(request):
	global stdoutstream, PDF_PATH
	evia_paths = cevia.EviaPaths(PDF_PATH)
	text = '{}'.format(stdoutstream.getvalue())
	text = text.split('\n')
	return render(request,'outputs_extract.html',{'output_messages' :text})
	#return HttpResponse("Hello, world. You're at the commands page.")
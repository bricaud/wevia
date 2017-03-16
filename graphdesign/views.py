from django.shortcuts import render
import commands.eviascripts as cevia
import sys
from contextlib import redirect_stdout 
import io 
from django.conf import settings

stdoutstream = io.StringIO()
#PDF_PATH = '/media/benjamin/Largo/testspdfs'
PDF_PATH = settings.PDF_PATH

def index(request):
	global PDF_PATH
	num_var = 0
	output = ''
	graph_threshold = 8
	evia_paths = cevia.EviaPaths(PDF_PATH)
	if(request.GET.get('make_graph')):
		graph_threshold = int(request.GET.get('graph_threshold'))
		output = make_graph(graph_threshold,evia_paths)
		print(output)
	return render(request,'graphdesign_template.html',
		{'console_message' :output, 'loading':'False', 'graph_threshold' : graph_threshold})


def make_graph(graph_threshold,paths_object):
	global stdoutstream
	with redirect_stdout(stdoutstream):
		output = cevia.make_graph(graph_threshold,paths_object)
	print('Console message: '+output)
	return output


def request_output_page(request):
	global stdoutstream, PDF_PATH
	evia_paths = cevia.EviaPaths(PDF_PATH)
	text = '{}'.format(stdoutstream.getvalue())
	text = text.split('\n')
	return render(request,'outputs_graphd.html',{'output_messages' :text})
	#return HttpResponse("Hello, world. You're at the commands page.")
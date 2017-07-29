from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
 
from fileupload.forms import UploadFileForm
from fileupload.models import Document

import os

import commands.eviascripts as cevia
from django.conf import settings

import grevia


def index(request):
	try:
		graph = grevia.wordgraph.Graph('GremlinGraph',settings.GRAPH_SERVER_ADDRESS)
	except:
		message = 'Unable to connect to the graph server.'
		raise ValueError('Unable to connect to the graph server.')
	message =''
	evia_paths = cevia.EviaPaths(settings.PDF_PATH)
	#for obj in Document.objects.all():
	#	path,filename = os.path.split(obj.file.name)
	#	print(filename)
	#	if os.path.isfile(obj.file.path):
	#		#print(obj.file.size)
	#		print(obj.file.name)
	#		#print(obj.file.path)
	#print([objname.name for objname in Document.objects.filter(name__contains='EVIA')])
	#graph = grevia.wordgraph.Graph('GremlinGraph',settings.GRAPH_SERVER_ADDRESS)

	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			(root_name,ext) = os.path.splitext(request.FILES['file'].name)
			process_file(root_name,request.FILES['file'],evia_paths,graph)
			return HttpResponseRedirect(reverse('fileupload'))
	else:
		form = UploadFileForm()
 
	data = {'form': form, 'message': message}
	#return render_to_response('main/index.html', data, context_instance=RequestContext(request))
	return render(request,'fileupload/index.html',data)

def process_file(name,data,evia_paths,graph):
	# Check if the file is already recorded (check name and size)
	same_name_entries = Document.objects.filter(name=name)
	if same_name_entries:
		# if same name, check if same size
		same_size = []
		for item in same_name_entries:
			if os.path.isfile(item.file.path) and item.file.size==data.size:
				same_size.append(item)	
		if same_size: # Only add to graph
			add_to_graph(name,graph)
		else:
			extract_file(data,name,evia_paths,graph)
	else:
		extract_file(data,name,evia_paths,graph)


def extract_text(file,evia_paths):
	file_data,message = cevia.run_singlefile_textextract(file,evia_paths)
	return file_data,message

def run_pdf2txt(paths_objects):
	global stdoutstream
	with redirect_stdout(stdoutstream):
		output = cevia.run_pdf2txt(paths_objects)
	return output

def save_info_to_db(file_data,db_entry):
	db_entry.extract_error = file_data['error']
	if not file_data['error']:
		db_entry.txt_error = file_data['error_in_txt']
		db_entry.nb_pages = file_data['nb_pages']
		db_entry.text = file_data['text']
		db_entry.path = file_data['path']
		db_entry.png_path = file_data['pngpath']
		db_entry.txt_path = file_data['txtpath']
	db_entry.save()
	return db_entry

def extract_file(request_file,name,evia_paths,graph):
	new_file = Document(file = request_file, name = name)
	new_file.save()
	message = 'processed!!' #request.FILES['file'] # + ' processed!'
	#print(new_file.file.name)
	#print(new_file.file.path)
	pdf_rel_name = new_file.file.path
	file_data,message = extract_text(pdf_rel_name,evia_paths)
	db_entry = save_info_to_db(file_data,new_file)
	add_to_graph(name,graph)
	
def add_to_graph(name,graph):
	# Add the document from the DB to the graph
	db_entry_r = Document.objects.get(name=name)
	if not db_entry_r.is_in_graph:
		db_entry_dic = {'name':db_entry_r.name, 'id':db_entry_r.id, 'text':db_entry_r.text}
		cevia.add_document_to_graph(db_entry_dic,graph)
		db_entry_r.is_in_graph = True
		db_entry_r.save()
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
 
from fileupload.forms import UploadFileForm
from fileupload.models import Document

import os

import commands.eviascripts as cevia
from django.conf import settings
PDF_PATH = settings.PDF_PATH
UPLOAD_PATH = settings.UPLOAD_PATH

def index(request):
	global PDF_PATH
	global UPLOAD_PATH
	message =''
	evia_paths = cevia.EviaPaths(PDF_PATH)
	#for obj in Document.objects.all():
	#	path,filename = os.path.split(obj.file.name)
	#	print(filename)
	#	if os.path.isfile(obj.file.path):
	#		#print(obj.file.size)
	#		print(obj.file.name)
	#		#print(obj.file.path)
	#print([objname.name for objname in Document.objects.filter(name__contains='EVIA')])

	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			(root,ext) = os.path.splitext(request.FILES['file'].name)
			# Check if the file is already recorded (check name and size)
			same_name_entries = Document.objects.filter(name=root)
			if not same_name_entries:
				process_file(request.FILES['file'],root,evia_paths)
			else:
				same_size = []
				for item in same_name_entries:
					if os.path.isfile(item.file.path) and item.file.size==request.FILES['file'].size:
						same_size.append(item)	
				if not same_size:
					#[item.delete() for item in same_name_entries]
					process_file(request.FILES['file'],root,evia_paths)
			return HttpResponseRedirect(reverse('fileupload'))
	else:
		form = UploadFileForm()
 
	data = {'form': form, 'message': message}
	#return render_to_response('main/index.html', data, context_instance=RequestContext(request))
	return render(request,'fileupload/index.html',data)

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

def process_file(request_file,name,evia_paths):
	new_file = Document(file = request_file, name = name)
	new_file.save()
	message = 'processed!!' #request.FILES['file'] # + ' processed!'
	#print(new_file.file.name)
	#print(new_file.file.path)
	pdf_rel_name = new_file.file.path
	file_data,message = extract_text(pdf_rel_name,evia_paths)
	save_info_to_db(file_data,new_file)
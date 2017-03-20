from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
 
from fileupload.forms import UploadFileForm
from fileupload.models import UploadFile
 
import commands.eviascripts as cevia
from django.conf import settings
PDF_PATH = settings.PDF_PATH
UPLOAD_PATH = settings.UPLOAD_PATH

def index(request):
	message =''
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			new_file = UploadFile(file = request.FILES['file'])
			new_file.save()
			message = 'processed!!' #request.FILES['file'] # + ' processed!'
			print(request.FILES['file'])
			print(new_file)
			return HttpResponseRedirect(reverse('fileupload'))
	else:
		form = UploadFileForm()
 
	data = {'form': form, 'message': message}
	#return render_to_response('main/index.html', data, context_instance=RequestContext(request))
	return render(request,'fileupload/index.html',data)

def extract_text(file,path):
	pass

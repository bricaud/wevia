from django.shortcuts import render
from django.http import HttpResponse
import commands.eviascripts as cevia
import sys
from contextlib import redirect_stdout 
import io 

stdoutstream = io.StringIO()
PDF_PATH = '/media/benjamin/Largo/testspdfs'

def index(request):
	return render(request,'home_template.html')

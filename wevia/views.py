from django.shortcuts import render
from django.conf import settings

import sys
grevia_path = '../grevia'
sys.path.append(grevia_path)
import grevia

def index(request):
	return render(request,'home_template.html',{ 'weviana_version' : settings.VERSION ,'grevia_version' : grevia.__version__})

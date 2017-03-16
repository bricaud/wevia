from django.shortcuts import render
import commands.eviascripts as cevia
import sys
from contextlib import redirect_stdout 
import io 
from django.conf import settings
PDF_PATH = settings.PDF_PATH

stdoutstream = io.StringIO()


def index(request):
	global PDF_PATH
	evia_paths = cevia.EviaPaths(PDF_PATH)
	searchquery = ''
	search_results = {}
	console_message = ''	
	if(request.GET.get('make_search')):
		searchquery = str(request.GET.get('search'))
		search_results,console_message = make_search(searchquery,evia_paths)
	return render(request,'search.html',
		{ 'query':searchquery, 'search_results' :search_results, 'console_message' : console_message})

	

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
	return render(request,'search.html',
		{ 'query':searchquery, 'search_results' :search_results, 'console_message' : console_message})

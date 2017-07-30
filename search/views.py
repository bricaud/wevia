from django.shortcuts import render
import commands.eviascripts as cevia
from django.http import HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

# load the models (database objects)
from classif.models import Cluster
from fileupload.models import Document
from graphdesign.models import GraphNode

from fileupload.forms import DocModifForm



def index(request):
	evia_paths = cevia.EviaPaths(settings.PDF_PATH)
	searchquery = ''
	search_results = {}
	console_message = ''	
	if(request.GET.get('make_search')):
		searchquery = str(request.GET.get('search'))
		search_results,console_message = make_search_texts(searchquery,evia_paths)
	if(request.GET.get('make_search_cluster')):
		searchquery = str(request.GET.get('search'))
		search_results,console_message = make_search_texts(searchquery,evia_paths,sorted_param='cluster')
	return render(request,'searchtext.html',
		{ 'query':searchquery, 'search_results' :search_results, 'console_message' : console_message})


def advanced(request):
	evia_paths = cevia.EviaPaths(settings.PDF_PATH)
	searchquery = ''
	search_results = {}
	console_message = ''	
	if(request.GET.get('make_search')):
		searchquery = str(request.GET.get('search'))
		search_results,console_message = make_search_groupdoc(searchquery,evia_paths)
	if(request.GET.get('make_search_cluster')):
		searchquery = str(request.GET.get('search'))
		search_results,console_message = make_search_groupdoc(searchquery,evia_paths,sorted_param='cluster')
	return render(request,'search-groupdoc.html',
		{ 'query':searchquery, 'search_results' :search_results, 'console_message' : console_message})

	

def make_search(searchquery,paths_object,sorted_param='keyword'):
	if not searchquery:
		return {},''
	print('starting the search, keyword: {}'.format(searchquery))	
	search_results,console_message = cevia.make_search_graphdb(searchquery)#,paths_object)
	print(console_message)
	search_flat = []
	for keyword in search_results.keys():
		for doc_id in search_results[keyword].keys():
			results_dic = search_results[keyword][doc_id]
			results_dic['keyword'] = keyword
			results_dic['color'] = cevia.set_cluster_color(search_results[keyword][doc_id]['cluster'])
			search_flat.append(results_dic)
	if sorted_param=='keyword':
		return search_flat,console_message
	else:
		sorted_search = sorted(search_flat,key= lambda results_dic:results_dic[sorted_param])
		return sorted_search,console_message

def make_search_groupdoc(searchquery,paths_object,sorted_param='keyword'):
	if not searchquery:
		return {},''
	print('starting the search, keyword: {}'.format(searchquery))	
	search_results,console_message = cevia.make_search_doc_graphdb(searchquery)#,paths_object)
	print(console_message)
	search_flat = []
	for docname in search_results.keys():
		for entry in search_results[docname]:
			results_dic = entry
			#print(entry)
			results_dic['document'] = docname
			results_dic['color'] = cevia.set_cluster_color(entry['cluster'])
			search_flat.append(results_dic)
	if sorted_param=='keyword':
		return search_flat,console_message
	else:
		sorted_search = sorted(search_flat,key= lambda results_dic:results_dic[sorted_param])
		return sorted_search,console_message


def make_search_texts(searchquery,paths_object,sorted_param='keyword'):
	if not searchquery:
		return {},''
	print('starting the search, keyword: {}'.format(searchquery))	
	search_results,console_message = cevia.make_search_doc_graphdb(searchquery)#,paths_object)
	print(console_message)
	search_flat = []
	for docname in search_results.keys():
		results_dic = {}
		results_dic['name'] = search_results[docname][0]['name']
		results_dic['cluster'] = search_results[docname][0]['cluster']
		results_dic['color'] = cevia.set_cluster_color(results_dic['cluster'])
		results_dic['text_list'] = []
		for entry in search_results[docname]:
			text_string = ('...' + " ".join(entry['text_before']) + " <b> " + entry['expression']
				+ " </b> " + " ".join(entry['text_after'])+ '...')
			results_dic['text_list'].append(['...' + " ".join(entry['text_before']),
				entry['expression']," ".join(entry['text_after'])+ '...' ])
		search_flat.append(results_dic)
	if sorted_param=='keyword':
		return search_flat,console_message
	else:
		sorted_search = sorted(search_flat,key= lambda results_dic:results_dic[sorted_param])
		return sorted_search,console_message

def dbinfo(request,document_query):
	try:
		entry = Document.objects.get(name=document_query)
	except:
		print('Document "{}" not found.'.format(document_query))
		return render(request,'dbinfo.html',
		{ 'document': {},'query': document_query})

	return render(request,'dbinfo.html',
		{ 'document': sorted(entry.__dict__.items()),'query': document_query})


def dbinfo_and_modif(request,document_query):
	try:
		entry = Document.objects.get(name=document_query)
	except:
		print('Document "{}" not found.'.format(document_query))
		return render(request,'dbinfomod.html',
		{ 'document': {},'query': document_query})

	return render(request,'dbinfomod.html',
		{ 'document': entry,'query': document_query, 'cluster_color': cevia.set_cluster_color(entry.cluster.number)})


def modif_db(request):
	message =''
	if(request.GET.get('modif_db')):
		print('GET received')
		document_query = request.GET.get('entryname')
		#print(document_query)
		try:
			entry = Document.objects.get(name=document_query)
		except:
			print('No document found with name: ',document_query)
			message = 'No document found with name {}'.format(document_query)
			form = DocModifForm()
			return render(request,'dbmodif.html',
				{ 'message': message,'query': document_query, 'form': form})
		form = DocModifForm(instance=entry)#, initial={'name':document_query})
		#print(form['text'].value())
		#form = DocModifForm(initial={'date': entry.date, 
		#	'description': entry.description, #'cluster': entry.cluster.id,
		#	'text': entry.text})


	elif request.method == 'POST':
		print('POST received')
		form = DocModifForm(request.POST)
		if form.is_valid():
			print('Form valid')
			document_query = form.cleaned_data['name']
			print(document_query)
			#if form.has_changed():
			#	message = "The following fields changed: %s" % ", ".join(form.changed_data)
			#	print(message)
			doc_record = Document.objects.get(name=document_query)
			doc_record.text_date = form.cleaned_data['text_date']
			doc_record.description = form.cleaned_data['description']
			doc_record.cluster = form.cleaned_data['cluster']
			doc_record.text = form.cleaned_data['text']
			doc_record.last_modified = timezone.now()
			doc_record.save()
			message = 'Modifications saved to database.'
			return render(request,'dbmodif.html',
				{ 'message': message,'query': document_query, 'form': form})
		else:
			form_dic = form.__dict__
			print(form_dic)
			for key,value in form_dic['fields'].items():
				print(key,value)
			document_query = form_dic['data']['name']
			message = 'Invalid form!'
	else:
		form = DocModifForm()
		 
	return render(request,'dbmodif.html',
		{ 'message': message,'query': document_query, 'form': form})


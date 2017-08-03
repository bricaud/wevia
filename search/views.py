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

from operator import itemgetter

import txt2graph

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

	
##################### Search functions
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
		return [],'Nothing found for {}'.format(searchquery)
	print('starting the search, keyword: {}'.format(searchquery))	
	search_results = cevia.search_graphdb(searchquery)#,paths_object)
	search_results = rank_expressions_search_results(search_results)
	search_results = group_nodes_in_doc_entries(search_results)
	search_results = node_to_doc_dic(search_results)
	search_results = build_text_strips(search_results)
	#print(search_results)
	message = 'Search results for keyword: {}'.format(searchquery)	
	return search_results,message

def node_to_dic(search_results):
	search_flat = []
	for docname in search_results.keys():
		results_dic = {}
		#Common values between all the results, pick the ones of the first result [0]
		results_dic['name'] = search_results[docname][0]['name']
		results_dic['cluster'] = search_results[docname][0]['cluster']
		results_dic['color'] = cevia.set_cluster_color(results_dic['cluster'])
		results_dic['text_list'] = []
		expr_list = process_expressions(search_results[docname])
		results_dic['text_list'] = expr_list
		search_flat.append(results_dic)
	if sorted_param=='keyword':
		return search_flat,console_message
	else:
		sorted_search = sorted(search_flat,key= lambda results_dic:results_dic[sorted_param])
		return sorted_search,console_message


def rank_expressions_search_results(search_results):
	search_results = [(node, rank_formula(node)) for node in search_results]
	search_results = sorted(search_results, key=itemgetter(1),reverse=True)
	return search_results

def rank_formula(node):
	return 1./((node.degree_sim1+1)*(node.degree_sim2+1))

def get_text_strips(search_string):

	#search_results = add_flux_to_list(G,None,search_results,1./len(search_results))
	data_dic = get_info_from_list_doc(search_results)

	console_message = 'Search results:'
	return data_dic,console_message


def group_nodes_in_doc_entries(search_results):
	data_dic = {}
	#print(search_results)
	for (node,score) in search_results:
		text_ids = node.get_text_ids()
		for text_id in text_ids:
			if text_id not in data_dic:
				data_dic[text_id] = []
			data_dic[text_id].append((node,score))
	return data_dic

def node_to_doc_dic(search_results):
	results = []
	for text_id in search_results:
		documents_list = Document.objects.filter(id=text_id)
		document = documents_list[0]
		# get document info
		data_dic = {}
		data_dic['text_id'] = text_id
		data_dic['name'] = document.name
		data_dic['cluster'] = document.get_cluster_id()
		data_dic['color'] = cevia.set_cluster_color(data_dic['cluster'])
		data_dic['url'] = document.get_url()
		data_dic['text'] = document.text
		# get expression info
		data_dic['position_info_list'] = []
		data_dic['score'] = 0
		for (node,score) in search_results[text_id]:
			position_list = node.get_paths(text_id)
			nb_pos = len(position_list)
			data_dic['position_info_list'] += [(pos,pos+len(node.expression),score) for pos in position_list]
			data_dic['score'] += score*nb_pos 
		results.append(data_dic)
	results = sorted(results, key=lambda x: x['score'], reverse=True)
	return results


def build_text_strips(data):
	surrounding_len = 10
	results = []
	for doc_entry in data:
		doc_text = doc_entry['text']
		positions = doc_entry['position_info_list']
		positions = sorted(positions, key=itemgetter(0) )
		strip_list = group_in_strips(positions,surrounding_len)
		filtered_text = txt2graph.filter_text(doc_text) 
		expression_list = strip_to_expression(strip_list,surrounding_len,filtered_text)
		expression_list = sorted(expression_list, key=itemgetter(1), reverse=True)
		doc_entry['expression_list'] = expression_list
		del doc_entry['text']
		results.append(doc_entry)
	return results

def group_in_strips(positions,surrounding_len):
	strip_list = []
	first_pos = positions[0]
	postart = first_pos[0]
	posend = first_pos[1]
	strip = [first_pos]
	score = first_pos[2]
	for pos in positions[1:]:
		if pos[0]<posend+surrounding_len:
			strip.append(pos)
			score += pos[2]
		else:
			strip_list.append((strip,score))
			strip = [pos]
			score = pos[2]
		posend = pos[1]
	strip_list.append((strip,score)) # for the last strip
	return strip_list

def strip_to_expression(strip_list,surrounding_len,text):
	text_cuts = []
	for (strip,score) in  strip_list:
		pstart = max(0,strip[0][0]-surrounding_len)
		pend = min(len(text),strip[-1][1]+surrounding_len)
		text_list = []
		for pos in strip:
			if pos[0]<=pstart:
				if pos[1]<=pstart:
					pass
				else:
					text_list.append((" ".join(text[pstart:pos[1]]),True))
			else:
				text_list.append((" ".join(text[pstart:pos[0]]),False)) # False = normal text
				text_list.append((" ".join(text[pos[0]:pos[1]]),True)) # True = emphasized text
			pstart = pos[1]
		text_list.append((" ".join(text[pstart:pend]),False))
		text_cuts.append((text_list,score))
	return text_cuts






#################### Database document info
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


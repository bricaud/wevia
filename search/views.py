from django.shortcuts import render
import commands.eviascripts as cevia

from django.conf import settings


def index(request):
	evia_paths = cevia.EviaPaths(settings.PDF_PATH)
	searchquery = ''
	search_results = {}
	console_message = ''	
	if(request.GET.get('make_search')):
		searchquery = str(request.GET.get('search'))
		search_results,console_message = make_search(searchquery,evia_paths)
	if(request.GET.get('make_search_cluster')):
		searchquery = str(request.GET.get('search'))
		search_results,console_message = make_search(searchquery,evia_paths,sorted_param='cluster')
	return render(request,'search.html',
		{ 'query':searchquery, 'search_results' :search_results, 'console_message' : console_message})

	

def make_search(searchquery,paths_object,sorted_param='keyword'):
	if not searchquery:
		return {},''
	print('starting the search, keyword: {}'.format(searchquery))	
	search_results,console_message = cevia.make_search_db(searchquery)#,paths_object)
	print(console_message)
	search_flat = []
	for keyword in search_results.keys():
		for doc_id in search_results[keyword].keys():
			results_dic = search_results[keyword][doc_id]
			results_dic['keyword'] = keyword
			results_dic['color'] = set_cluster_color(search_results[keyword][doc_id]['cluster'])
			search_flat.append(results_dic)
	if sorted_param=='keyword':
		return search_flat,console_message
	else:
		sorted_search = sorted(search_flat,key= lambda results_dic:results_dic[sorted_param])
		return sorted_search,console_message

def set_cluster_color(cluster_id):
	d3_category20 = (['#1f77b4', '#aec7e8',
		'#ff7f0e', '#ffbb78',
		'#2ca02c', '#98df8a',
		'#d62728', '#ff9896',
		'#9467bd', '#c5b0d5',
		'#8c564b', '#c49c94',
		'#e377c2', '#f7b6d2',
		'#7f7f7f', '#c7c7c7',
		'#bcbd22', '#dbdb8d',
		'#17becf', '#9edae5'
	])
	if cluster_id==-1:
		return '#333333'
	return d3_category20[cluster_id]

"""	
def request_search_results(request):
	evia_paths = cevia.EviaPaths(settings.PDF_PATH)
	searchquery = ''
	search_results = {}
	console_message = ''	
	if(request.GET.get('make_search')):
		searchquery = str(request.GET.get('search'))
		search_results,console_message = make_search(searchquery,evia_paths)
	return render(request,'search.html',
		{ 'query':searchquery, 'search_results' :search_results, 'console_message' : console_message})
"""

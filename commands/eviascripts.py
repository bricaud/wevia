#!/usr/bin/env python3
import os
import sys
import csv
import warnings
from itertools import permutations
import shutil
sys.path.append('../OCR')
sys.path.append('./OCR')

import pdf2txtbox
import textbox
import txt2graph
import tqdm

from graphdesign.models import GraphNode, DocumentIndex
from fileupload.models import Document
from classif.models import Cluster

import grevia.g_gremlin as graphdatabase

class EviaPaths():

	def	__init__(self,PDF_PATH):

		#self.PDF_PATH = PDF_PATH
		self.PDF_PATH = PDF_PATH
		self.WEVIANA_PATH = os.path.join(self.PDF_PATH,'weviana')
		self.PNG_PATH = os.path.join(self.WEVIANA_PATH,'png')
		self.TXT_PATH = os.path.join(self.WEVIANA_PATH,'txt')
		self.PICKLE_PATH = os.path.join(self.WEVIANA_PATH,'pickle')
		self.EX_TXT_PICKLE = os.path.join(self.PICKLE_PATH,'extract_texts.pkl')
		self.TXT_PICKLE = os.path.join(self.PICKLE_PATH,'texts.pkl')
		self.GRAPH_NAME = os.path.join(self.PICKLE_PATH,'graph.pkl')
		self.CSV_PATH = os.path.join(self.WEVIANA_PATH,'csv')
		self.CSV_FILE = 'table_classif.csv'
		self.CSV_full_name = os.path.join(self.CSV_PATH,self.CSV_FILE)	
		self.CLASSIF_PATH = os.path.join(self.WEVIANA_PATH,'classif')
		self.LOGS_PATH = os.path.join(self.WEVIANA_PATH,'logs')

		if not os.path.exists(self.WEVIANA_PATH):
			os.makedirs(self.WEVIANA_PATH)
		if not os.path.exists(self.PNG_PATH):
			os.makedirs(self.PNG_PATH)
		if not os.path.exists(self.PICKLE_PATH):
			os.makedirs(self.PICKLE_PATH)
		if not os.path.exists(self.CSV_PATH):
			os.makedirs(self.CSV_PATH)
		if not os.path.exists(self.TXT_PATH):
			os.makedirs(self.TXT_PATH)
		if not os.path.exists(self.CLASSIF_PATH):
			os.makedirs(self.CLASSIF_PATH)
		if not os.path.exists(self.LOGS_PATH):
			os.makedirs(self.LOGS_PATH)

def check_files(files_list):
	""" Check if the files exists"""
	for file in files_list:
		if not os.path.isfile(file):
			print()


def run_pdf2txt(evia_paths):
	""" Extract the text in the pdf files of the PDF_PATH """
	PDF_PATH = evia_paths.PDF_PATH
	LOGS_PATH = evia_paths.LOGS_PATH
	PNG_PATH = evia_paths.PNG_PATH
	TXT_PATH = evia_paths.TXT_PATH
	EX_TXT_PICKLE = evia_paths.EX_TXT_PICKLE
	print('Running pdf2txt on',PDF_PATH)
	output_message = pdf2txtbox.pdf2txt(PDF_PATH,PNG_PATH,TXT_PATH,LOGS_PATH,EX_TXT_PICKLE)
	print('Computation done. Texts extracted.')
	return 'Computation done. Texts extracted.' + '\n' + output_message


def run_singlefile_pdf2txt(pdf_file,evia_paths):
	""" Extract the text of a pdf file filename """
	PDF_PATH = evia_paths.PDF_PATH
	PNG_PATH = evia_paths.PNG_PATH
	TXT_PATH = evia_paths.TXT_PATH
	full_path,filename = os.path.split(pdf_file)
	# keeping the relative path
	rel_path =os.path.relpath(full_path,PDF_PATH)
	print('Running singlefile_pdf2txt on',filename)
	file_data, output_message = pdf2txtbox.singlefile_pdf2txt(filename,rel_path,full_path,PNG_PATH,TXT_PATH)
	print('Computation done. Texts extracted.')
	return file_data,'Computation done. Texts extracted.' + '\n' + output_message


def run_singlefile_textextract(pdf_file,evia_paths):
	file_data,message = run_singlefile_pdf2txt(pdf_file,evia_paths)
	if file_data['error']:
		return file_data,message
	nb_of_pages = file_data['nb_pages']
	txt_path = file_data['txtpath']
	short_name = file_data['name']
	txt_short_filename = os.path.join(txt_path,short_name)
	full_text,error_code = textbox.singlepdf_extract_text(txt_short_filename,nb_of_pages)
	file_data['text'] = full_text
	file_data['error_in_txt'] = error_code
	if error_code:
		message = message + ' Error occured during extraction of text.'
	return file_data,message
"""
def make_graph(graph_threshold,evia_paths):
	TXT_PATH = evia_paths.TXT_PATH
	TXT_PICKLE = evia_paths.TXT_PICKLE
	GRAPH_NAME = evia_paths.GRAPH_NAME
	LOGS_PATH = evia_paths.LOGS_PATH

	if not os.listdir(TXT_PATH):
		print('No text data file. Please extract the text first. Run pdf2txt.')
		console_message = 'No text data file. Please extract the text first. Run pdf2txt.'
	else:
		print('Making the graph...')
		# Extract the text from the txt files and save them in a pickle file
		textbox.auto_extract(TXT_PATH,TXT_PICKLE,LOGS_PATH)
		# Create the graph from the pickle file
		output_message = txt2graph.run(TXT_PICKLE,GRAPH_NAME,min_weight=graph_threshold,max_iter=20000)
		print('Graph saved in file {}'.format(GRAPH_NAME))
		console_message = output_message+ '\n' + 'Graph saved in file {}'.format(GRAPH_NAME)
	return console_message
"""

def make_graph_from_db(db_entries_dic,graph_threshold,evia_paths):
	GRAPH_NAME = evia_paths.GRAPH_NAME
	if not db_entries_dic:
		print('empty database!')
		return 'empty database!'
	print('Making the graph...')
	node_dic,output_message = txt2graph.run_from_db(db_entries_dic,GRAPH_NAME,min_weight=graph_threshold,max_iter=20000)
	print('Graph saved in file {}'.format(GRAPH_NAME))
	print('Saving nodes in database...')
	message_db = save_nodes_in_db(node_dic)
	console_message = output_message+ '\n' + 'Graph saved in file {}'.format(GRAPH_NAME) + '\n' + message_db
	return console_message

def save_nodes_in_db(node_dic):
	nb_nodes = len(node_dic)
	# Progess bar
	pbar = tqdm.tqdm(total=nb_nodes)
	for node in node_dic.keys():
		# Save the graph node in the database
		new_node = GraphNode.objects.create(name=node)
		if 'paths' in node_dic[node]:
			for document_id in node_dic[node]['paths'].keys():
				doc = Document.objects.get(id=document_id)
				#print(doc)
				# Create a document index connection the GraphNode with 
				# the documents where it appears
				doc_index = DocumentIndex(document=doc, graphnode=new_node)
				doc_index.load_list(node_dic[node]['paths'][document_id]['word_positions'])
				doc_index.save()
		pbar.update(1)
	pbar.close()
	return 'Nodes saved in DB.'

def run_classify(evia_paths):
	CSV_full_name = evia_paths.CSV_full_name
	TXT_PICKLE = evia_paths.TXT_PICKLE
	GRAPH_NAME = evia_paths.GRAPH_NAME
	EX_TXT_PICKLE = evia_paths.EX_TXT_PICKLE
	if not os.path.isfile(TXT_PICKLE):
		print('No text data file. Please extract the text first with pdf2txt. ')
		console_message = 'No text data file found. Please extract the text first with pdf2txt. '
	elif not os.path.isfile(GRAPH_NAME):
		print('No graph found. Please construct the graph first. ')
		console_message = 'No graph found. Please construct the graph first. '
	elif not os.path.isfile(EX_TXT_PICKLE):
		print('No file with info on extracted text. Please extract the text first with pdf2txt. ')
		console_message = 'No file with info on extracted text. Please extract the text first with pdf2txt. '
	else:
		txt2graph.doc_classif(GRAPH_NAME,TXT_PICKLE,EX_TXT_PICKLE,CSV_full_name)
		console_message = 'CSV file containing the classification saved in {}'.format(CSV_full_name)
	return console_message

def run_classify_db(evia_paths):
	CSV_full_name = evia_paths.CSV_full_name
	GRAPH_NAME = evia_paths.GRAPH_NAME
	if not os.path.isfile(GRAPH_NAME):
		print('No graph found. Please construct the graph first. ')
		return 'No graph found. Please construct the graph first. '
	document_index_dic = {}
	for document in Document.objects.all():
		document_index_dic[document.id] = {}
		document_index_dic[document.id]['name'] = document.name
		if os.path.isfile(document.file.path):
			document_index_dic[document.id]['path'] = document.file.path
		else:
			document_index_dic[document.id]['path'] = ''
			warnMessage = ('Cannot find file for database entry. Document: "{}".'.format(document.name) +
				' You may need to clean the database.')
			warnings.warn(warnMessage)
	clusters_dic = txt2graph.doc_classif_db(GRAPH_NAME,document_index_dic,CSV_full_name)
	# clean old classification and save the new one in the database:
	Cluster.objects.all().delete()
	save_classif_in_db(clusters_dic)
	return 'CSV file containing the classification saved in {}'.format(CSV_full_name)

def save_classif_in_db(clusters_dic):
	pbar = tqdm.tqdm(total=len(clusters_dic))
	for key in clusters_dic.keys():
		c_docids = clusters_dic[key]['doc_ids']
		c_shared_words = clusters_dic[key]['shared_words']
		new_cluster = Cluster(name='Cluster_'+str(key), number=int(key), confidence=(clusters_dic[key]['density']*100))
		new_cluster.load_sharedWords(c_shared_words)
		new_cluster.save()
		# link to the documents
		for doc_id in c_docids:
			document = Document.objects.get(pk=doc_id)
			document.cluster = new_cluster
			document.save()
		pbar.update(1)
	pbar.close()

def get_csv(evia_paths):
	# loading the CSV file into a dict of clusters
	CSV_full_name = evia_paths.CSV_full_name
	cluster_dic ={}
	if not os.path.isfile(CSV_full_name):
		print('No classification found. Please run the document classification. ')
		console_message = 'No classification found. Please run the document classification. '
	else:
		print('Loading: ',CSV_full_name)
		with open(CSV_full_name, 'r') as csvfile:
			clusters_table = csv.reader(csvfile, delimiter=',')
			for row in clusters_table:
				key = row[0]
				cluster_dic[key] = row[1:]
		console_message = 'Classification loaded from {}'.format(CSV_full_name)
	return cluster_dic,console_message
"""
def get_csv():
	# loading the CSV file into a dict of clusters
	global CSV_full_name
	cluster_dic ={}
	print('Loading: ',CSV_full_name)
	with open(CSV_full_name, 'r') as csvfile:
		clusters_table = csv.DictReader(csvfile, delimiter=',')
		for row in clusters_table:
			for key in row.keys():
				if key in cluster_dic.keys():
					cluster_dic[key].append(row[key])
				else:
					cluster_dic[key]=[row[key]]
	# Remove the cluster id given in the first row:
	print(cluster_dic)
	del cluster_dic['']
	return cluster_dic
"""

def csv2folders(evia_paths):
	""" Create a series of folders and store a copy of the classified files in them.
		The folders are created from the csv file.
	"""
	PDF_PATH = evia_paths.PDF_PATH
	CSV_full_name = evia_paths.CSV_full_name
	CLASSIF_PATH = evia_paths.CLASSIF_PATH

	if not os.path.isfile(CSV_full_name):
		print('No classification found. Please run the document classification. ')
		return 'No classification found. Please run the document classification. '

	# Load the data from the CSV file
	cluster_dic ={}
	print('Loading: ',CSV_full_name)
	with open(CSV_full_name, 'r') as csvfile:
		clusters_table = csv.reader(csvfile, delimiter=',')
		for row in clusters_table:
			key = row[0]
			cluster_dic[key] = row[1:]
	# copy classified the files in folders
	for key in cluster_dic.keys():
		c_folder = 'cluster_'+str(key)
		c_path = os.path.join(CLASSIF_PATH,c_folder)
		print('Writing folder {}'.format(c_path))
		if not os.path.exists(c_path):
			os.makedirs(c_path)
		for file in cluster_dic[key]:
			if '\\' in file or file==' ': # stop condition in the list (data other than filenames are stored after the string containing '\')
				break
			if len(file)>0:
				rel_path,short_name = os.path.split(file)
				filename = os.path.join(PDF_PATH,file+'.pdf')
				new_filename = os.path.join(c_path,short_name+'.pdf')
				shutil.copy2(filename,new_filename)
	console_message = 'Classification done. Files written in {}'.format(CLASSIF_PATH)
	return console_message
"""
def make_search(search_string,evia_paths):
	GRAPH_NAME = evia_paths.GRAPH_NAME
	TXT_PICKLE = evia_paths.TXT_PICKLE
	data_dic = {}
	if not os.path.isfile(TXT_PICKLE):
		print('No text data file. Please extract the text first with pdf2txt. ')
		console_message = 'No text data file found. Please extract the text first with pdf2txt. '
	elif not os.path.isfile(GRAPH_NAME):
		print('No graph found. Please construct the graph first. ')
		console_message = 'No graph found. Please construct the graph first. '
	else:
		word_list = search_string.lower().split()
		#import networkx as nx
		#G = nx.read_gpickle(GRAPH_NAME)
		import grevia
		G = grevia.Graph.load_from_file(GRAPH_NAME)
		documents_dic,data_index = txt2graph.read_file(TXT_PICKLE)
		for node,data in G.nodes(data=True):
			if set(word_list) & set(node.split('_')):
				if 'paths' in data.keys():
					data_dic[node] = {}
					for document_id in data['paths'].keys():
						list_of_positions = data['paths'][document_id]['word_positions']
						data_dic[node][document_id] = {}
						doc_name,doc_text = txt2graph.get_document_and_text(documents_dic,data_index,document_id)
						text_around = txt2graph.get_surrounding_text(doc_text,list_of_positions[0],nb_words=10)
						data_dic[node][document_id]['name'] = doc_name
						data_dic[node][document_id]['word_positions'] = list_of_positions
						data_dic[node][document_id]['text'] = text_around
				else:
					data_dic[node] = {}
		console_message = 'Search results:'
	return data_dic,console_message
"""
def make_search_db(search_string):
	word_list = search_string.split()
	total_results = []
	for permlist in permutations(word_list,len(word_list)):
		sentence = '_'.join(permlist)
		print('searching ',sentence)
		search_results = GraphNode.objects.filter(name__icontains=sentence)
		[total_results.append(item) for item in search_results]
	data_dic = {}
	for result in total_results:
		node = result.name
		data_dic[node] = {}
		documents_list = DocumentIndex.objects.filter(graphnode=result)
		for node_doc in documents_list:
			document_id = node_doc.document.id
			doc_text = node_doc.document.text
			list_of_positions = node_doc.get_list()
			text_around = txt2graph.get_surrounding_text(doc_text,list_of_positions[0],nb_words=10)
			data_dic[node][document_id] = {}
			data_dic[node][document_id]['name'] = node_doc.document.name
			data_dic[node][document_id]['word_positions'] = list_of_positions
			data_dic[node][document_id]['text'] = text_around
			try:
				data_dic[node][document_id]['cluster'] = node_doc.document.cluster.number
			except:
				print('Warning: document {} does not belong to any cluster. Please run the classification.'
					.format(data_dic[node][document_id]['name']))
				data_dic[node][document_id]['cluster'] = -1
			if os.path.isfile(node_doc.document.file.path):
				data_dic[node][document_id]['url'] = node_doc.document.file.url
			else:
				warnMessage = ('Cannot find file for database entry. Document: "{}".'.format(node_doc.document.name) +
				' You may need to clean the database.')
				warnings.warn(warnMessage)
	console_message = 'Search results:'
	return data_dic,console_message


def make_search_graphdb(search_string):
	word_list = search_string.split()
	total_results = []
	for permlist in permutations(word_list,len(word_list)):
		sentence = '_'.join(permlist)
		print('searching ',sentence)
		#search_results = GraphNode.objects.filter(name__icontains=sentence)
		G = graphdatabase.DiGraph()
		search_results = G.search_expression(sentence)
		[total_results.append(item) for item in search_results]
	data_dic = {}
	for result in total_results:
		expression = result['expression']
		doc_ids_dic = result['paths']

		data_dic[expression] = {}
		#documents_list = DocumentIndex.objects.filter(graphnode=result)
		for doc_id in doc_ids_dic:
			documents_list = Document.objects.filter(id=doc_id)
			document = documents_list[0]
			document_id = document.id
			doc_text = document.text
			list_of_positions = doc_ids_dic[doc_id]['word_positions']
			text_around = txt2graph.get_surrounding_text(doc_text,list_of_positions[0],nb_words=10)
			data_dic[expression][document_id] = {}
			data_dic[expression][document_id]['name'] = document.name
			data_dic[expression][document_id]['word_positions'] = list_of_positions
			data_dic[expression][document_id]['text'] = text_around
			try:
				data_dic[expression][document_id]['cluster'] = document.cluster.number
			except:
				print('Warning: document {} does not belong to any cluster. Please run the classification.'
					.format(data_dic[expression][document_id]['name']))
				data_dic[expression][document_id]['cluster'] = -1
			if os.path.isfile(document.file.path):
				data_dic[expression][document_id]['url'] = document.file.url
			else:
				warnMessage = ('Cannot find file for database entry. Document: "{}".'.format(document.name) +
				' You may need to clean the database.')
				warnings.warn(warnMessage)
	console_message = 'Search results:'
	return data_dic,console_message

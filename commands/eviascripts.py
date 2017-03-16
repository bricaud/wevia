#!/usr/bin/env python3
import os
import sys
import csv
import shutil
sys.path.append('../OCR')
sys.path.append('./OCR')

import pdf2txtbox
import textbox
import txt2graph


class EviaPaths():

	def	__init__(self,PDF_PATH):

		#self.PDF_PATH = PDF_PATH
		self.PDF_PATH = os.path.join(PDF_PATH,'weviana')
		self.PNG_PATH = os.path.join(self.PDF_PATH,'png')
		self.TXT_PATH = os.path.join(self.PDF_PATH,'txt')
		self.PICKLE_PATH = os.path.join(self.PDF_PATH,'pickle')
		self.TXT_PICKLE = os.path.join(self.PICKLE_PATH,'texts.pkl')
		self.GRAPH_NAME = os.path.join(self.PICKLE_PATH,'graph.pkl')
		self.CSV_PATH = os.path.join(self.PDF_PATH,'csv')
		self.CSV_FILE = 'table_classif.csv'
		self.CSV_full_name = os.path.join(self.CSV_PATH,self.CSV_FILE)	
		self.CLASSIF_PATH = os.path.join(self.PDF_PATH,'classif')
		self.LOGS_PATH = os.path.join(self.PDF_PATH,'logs')

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
	""" Extract the text in the the pdf files """
	PDF_PATH = evia_paths.PDF_PATH
	LOGS_PATH = evia_paths.LOGS_PATH
	PNG_PATH = evia_paths.PNG_PATH
	TXT_PATH = evia_paths.TXT_PATH
	print('Running pdf2txt on',PDF_PATH)
	output_message = pdf2txtbox.pdf2txt(PDF_PATH,PNG_PATH,TXT_PATH,LOGS_PATH)
	print('Computation done. Texts extracted.')
	return 'Computation done. Texts extracted.' + '\n' + output_message


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

def run_classify(evia_paths):
	CSV_full_name = evia_paths.CSV_full_name
	TXT_PICKLE = evia_paths.TXT_PICKLE
	GRAPH_NAME = evia_paths.GRAPH_NAME
	if not os.path.isfile(TXT_PICKLE):
		print('No text data file. Please extract the text first with pdf2txt. ')
		console_message = 'No text data file found. Please extract the text first with pdf2txt. '
	elif not os.path.isfile(GRAPH_NAME):
		print('No graph found. Please construct the graph first. ')
		console_message = 'No graph found. Please construct the graph first. '
	else:
		txt2graph.doc_classif(GRAPH_NAME,TXT_PICKLE,CSV_full_name)
		console_message = 'CSV file containing the classification saved in {}'.format(CSV_full_name)
	return console_message

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
		console_message = 'No classification found. Please run the document classification. '
	else:
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
				if '/' in file or file==' ': # stop condition in the list (data other than filenames are stored after the string containing '/')
					break
				if len(file)>0:
					filename = os.path.join(PDF_PATH,file+'.pdf')
					new_filename = os.path.join(c_path,file+'.pdf')
					shutil.copy2(filename,new_filename)
		console_message = 'Classification done. Files written in {}'.format(CLASSIF_PATH)
	return console_message

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
		import networkx as nx
		G = nx.read_gpickle(GRAPH_NAME)
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
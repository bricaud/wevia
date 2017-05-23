from django.shortcuts import render

import asyncio
import selectors
from goblin import Cluster, Goblin
from aiogremlin import DriverRemoteConnection, Graph


import goblin


class Person(goblin.Vertex):
	name = goblin.Property(goblin.String)



def index(request):
	output = ''
	if(request.GET.get('check_db')):
		output = check_graphdb()
	if(request.GET.get('write_db')):
		output = write_graphdb()
	return render(request,'graphDB/graphdb.html',
		{'console_message' :output})

def write_graphdb():
	selector = selectors.SelectSelector()
	loop = asyncio.SelectorEventLoop(selector)
	asyncio.set_event_loop(loop)
	loop = asyncio.get_event_loop()
	msg = loop.run_until_complete(test1(loop))
	print(msg)
	return msg

def check_graphdb():

	selector = selectors.SelectSelector()
	loop = asyncio.SelectorEventLoop(selector)
	asyncio.set_event_loop(loop)
	loop = asyncio.get_event_loop()
	vertices = loop.run_until_complete(go(loop))
	print(vertices)
	return 'Le bouton marche! Taille du graphe: {} noeuds.'.format(len(vertices))

async def test1(loop):
	app1 = await Goblin.open(loop)
	app1.config_from_file('graphDB/config.yml')

	benjamin = Person()
	benjamin.name = 'Ricaud'
	#session.add(benjamin)
	#await session.flush()
	#app = await goblin.Goblin.open(loop)
	app1.register(Person)
	session = await app1.session()
	session.add(benjamin)
	await session.flush()
	#loop = asyncio.get_event_loop()
	#loop.run_until_complete(test_db(loop))
	return 'hello'

async def test_db(loop):
	cluster = await Cluster.open('ws://localhost:8182/gremlin', loop)
	client = await cluster.connect()
	resp = await client.submit(
		"g.addV('developer').property(k1, v1)",
		bindings={'k1': 'name', 'v1': 'Leif'})
	async for msg in resp:
		print(msg)
	await cluster.close()
	return 'Written.'

async def go(loop):
	remote_connection = await DriverRemoteConnection.open(
		'ws://localhost:8182/gremlin', 'g')
	g = Graph().traversal().withRemote(remote_connection)
	vertices = await g.V().toList()
	await remote_connection.close()
	return vertices
from utils import *
from TrafficGraph import TrafficGraph
from graph_tool.all import *

SOURCE_MAX_FLOW = 9999
SINK_MAX_FLOW = 10
D_CRIT = 0.09
V_FF = 40
MAX_LANES = 6

def calculate_flows(g):
	for e in g.edges():
		# Parabolic jam density based on Tadaki et al.
		Uf = g.freeflow_speed[e]
		Us = g.actual_speed[e]
		Dj = D_CRIT * V_FF/Uf * 2 * (MAX_LANES - g.functional_class[e])
		g.max_flow[e] = Dj*Uf/4
		g.actual_flow[e] = Dj*Us - Dj/Uf * Us**2

def get_source_vertices(g):
	source_vertices = []
	for vertex in g.vertices():
		if vertex.in_degree() == 0:
			source_vertices.append(vertex)
			g.is_source[vertex] = True
	return source_vertices

def master_source(g):
	master_source = g.add_vertex()
	g.is_master_node[master_source] = True
	g.coordinates[master_source] = [0,0]
	source_vertices = get_source_vertices(g)
	for source_vertex in source_vertices:
		e = g.add_edge(master_source, source_vertex)
		g.is_master_edge[e] = True
		g.freeflow_speed[e] = 9999
	return master_source

def master_sink(g, master_source):
	master_sink = g.add_vertex()
	g.coordinates[master_sink] = [0,0]
	g.is_master_node[master_sink] = True
	for vertex in g.vertices():
		if int(vertex) != int(master_sink) and int(vertex) != int(master_source):
			# For now represent the leakage as a sink at every node with max flow 10km/hr
			e = g.add_edge(vertex, master_sink)
			g.freeflow_speed[e] = 10
			g.is_master_edge[e] = True
	return master_sink
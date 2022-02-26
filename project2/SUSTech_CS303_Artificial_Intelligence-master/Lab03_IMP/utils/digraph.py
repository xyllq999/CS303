#!/usr/bin/env python2
# -*- coding: utf-8 -*-

""" A Directed graph Class
A simple Python graph class, demonstrating the essential
facts and functionalities of graphs.
reference: https://www.python-course.eu/graphs_python.php
"""
from collections import defaultdict
from itertools import tee, izip


class DiGraph(object):
    '''
    A class to implement the directed graph
    '''

    def __init__(self, graph_dict=None):
        """ initializes a graph object
            If no dictionary or None is given, an empty dictionary will be used
            data structure: adjacency list
        """
        if graph_dict is None:
            graph_dict = {}
        self.__graph_dict = graph_dict
        self.__inverse_graph = {}
        self.inverse = self.__inverse_graph
        self.shortest_paths_next = None
        self.shortest_paths_data = defaultdict(dict)

    @staticmethod
    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return izip(a, b)

    @staticmethod
    def calculate_path_cost(graph, path):
        '''
        get the cost of the path
        '''
        cost = 0
        for edge in DiGraph.pairwise(path):
            cost += graph[edge[0]][edge[1]]['weight']
        return cost

    def add_edge_attr(self, edge, attrname, value):
        """
        add attribute to some edge
        """
        self.__graph_dict[edge[0]][edge[1]][attrname] = value
        self.__inverse_graph[edge[1]][edge[0]][attrname] = value

    def __getitem__(self, key):
        if key in self.__graph_dict.keys():
            return self.__graph_dict[key]
        return dict()

    def vertices(self):
        """ returns the vertices of a graph """
        return list(self.__graph_dict.keys())

    def edges(self):
        """ returns the edges of a graph """
        return self.__generate_edges()

    def add_vertex(self, vertex):
        """ If the vertex "vertex" is not in 
            self.__graph_dict, a key "vertex" with an empty
            list as a value is added to the dictionary. 
            Otherwise nothing has to be done. 
        """
        if vertex not in self.__graph_dict:
            self.__graph_dict[vertex] = []

    def add_weighted_edge(self, edge, weight):
        self.add_edge(edge)
        self.add_edge_attr(edge, 'weight', weight)

    def add_edge(self, edge):
        """ assumes that edge is of type set, tuple or list;
        only one edge
            between two vertices can be multiple edges!
           undirected edges
        """
        vertex1 = edge[0]
        vertex2 = edge[1]
        if vertex1 in self.__graph_dict:
            self.__graph_dict[vertex1][vertex2] = dict()
        else:
            self.__graph_dict[vertex1] = {vertex2: dict()} 
        if vertex2 not in self.__graph_dict:
            self.__graph_dict[vertex2] = dict()
        if vertex2 in self.__inverse_graph:
            self.__inverse_graph[vertex2][vertex1] = dict()
        else:
            self.__inverse_graph[vertex2] = {vertex1: dict()}
        if vertex1 not in self.__inverse_graph:
            self.__inverse_graph[vertex1] = dict()

    def __generate_edges(self):
        """ A static method generating the edges of the
            graph "graph". Edges are represented as sets
            with one (a loop back to the vertex) or two
            vertices
        """
        edges = []
        for vertex in self.__graph_dict:
            for neighbour in self.__graph_dict[vertex]:
                if {neighbour, vertex} not in edges:
                    edges.append({vertex, neighbour})
        return edges

    def __str__(self):
        res = "vertices: "
        for k in self.__graph_dict:
            res += str(k) + " "
        res += "\nedges: "
        for edge in self.__generate_edges():
            res += str(edge) + " "
        return res

    def find_path(self, start_vertex, end_vertex, path=[]):
        """ find a path from start_vertex to end_vertex
            in graph
        """
        graph = self.__graph_dict
        path = path + [start_vertex]
        if start_vertex == end_vertex:
            return path
        if start_vertex not in graph:
            return None
        for vertex in graph[start_vertex]:
            if vertex not in path:
                extended_path = self.find_path(vertex,
                                               end_vertex,
                                               path)
                if extended_path:
                    return extended_path
        return None

    def find_all_paths(self, start_vertex, end_vertex, path=None):
        """ find all paths from start_vertex to
            end_vertex in graph """
        if path is None:
            path = []
        graph = self.__graph_dict
        path = path + [start_vertex]
        if start_vertex == end_vertex:
            return [path]
        if start_vertex not in graph:
            return []
        paths = []
        for vertex in graph[start_vertex]:
            if vertex not in path:
                extended_paths = self.find_all_paths(vertex,
                                                     end_vertex,
                                                     path)
                for p in extended_paths:
                    paths.append(p)
        return paths

    def vertex_degree(self, vertex):
        """ The degree of a vertex is the number of edges connecting
            it, i.e. the number of adjacent vertices. Loops are counted 
            double, i.e. every occurence of vertex in the list 
            of adjacent vertices. """
        adj_vertices = self.__graph_dict[vertex]
        degree = len(adj_vertices) + adj_vertices.count(vertex)
        return degree

    def __calculate_all_shortest_path(self):
        '''
        calculate all shortest path and store them
        Floyd-Warshall, Maybe it should be Bellman–Ford algorithm
        '''
        # init
        dist = defaultdict(dict)
        next_edge = defaultdict(dict)

        for vertex in self.__graph_dict.keys():
            dist[vertex][vertex] = 0
        for key, value in self.__graph_dict.iteritems():
            for vertex in value.keys():
                dist[key][vertex] = value[vertex]['weight']
                next_edge[key][vertex] = vertex
        for k in self.__graph_dict.keys():
            for i in self.__graph_dict.keys():
                # print(k,i, dist[i].keys(), k not in dist[i].keys())
                if k not in dist[i].keys():
                    continue
                for j in self.__graph_dict.keys():
                    if j not in dist[k].keys():
                        continue
                    if j not in dist[i].keys() or dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_edge[i][j] = next_edge[i][k]
        self.shortest_paths_next = next_edge

    def get_shortest_path(self, edge):
        '''
        get certian shortest path
        '''
        if edge in self.shortest_paths_data.keys():
            path = self.shortest_paths_data[edge]
            return path

        if self.shortest_paths_next is None:
            self.__calculate_all_shortest_path()

        path = list()
        length = 0
        if edge[0] not in self.shortest_paths_next.keys():
            return path, -1
        if edge[1] not in self.shortest_paths_next[edge[0]].keys():
            return path, -1
        source_tmp = edge[0]
        target = edge[1]
        path.append(source_tmp)
        while source_tmp != target:
            tmp = source_tmp
            source_tmp = self.shortest_paths_next[source_tmp][target]
            length += self.__graph_dict[tmp][source_tmp]['weight']
            path.append(source_tmp)
        self.shortest_paths_data[edge] = (path, length)
        return (path, length)

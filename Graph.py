from Fuzzy import *
from util import *
from Edge import *
from typing import List


class Graph:
    def __init__(self, *args):
        if len(args) == 0:
            return
        self.graph = [[]]
        self.source = 0
        self.sink = 0
        self.num_vertices = 0
        self.num_edges = 0
        file = args[0]
        with open(file) as f:
            n = int(f.readline())
            self.num_vertices = n
            self.graph = [[] for i in range(n)]
            m = int(f.readline())
            self.num_edges = m
            self.source = int(f.readline())
            self.sink = int(f.readline())
            for i in range(m):
                if i == 3:
                    pass
                line = f.readline().split()
                assert len(line) == 2, "1st line must have exactly 2 numbers - vertices ids"
                vertices = to_int(line)
                v_from, v_to = vertices[0], vertices[1]

                line = f.readline().split(',')
                assert len(line) == 3, "2nd line must have exactly 3 numbers - fuzzy number for a flow"
                fl = to_float(line)
                flow = FuzzyNumber(fl[0], fl[1], fl[2])

                line = f.readline().split(',')
                assert len(line) == 3, "3nd line must have exactly 3 numbers - fuzzy number for a capacity"
                cap = to_float(line)
                capacity = FuzzyNumber(cap[0], cap[1], cap[2])

                w = int(f.readline())
                new_edge = Edge(vert_from=v_from,
                                vert_to=v_to,
                                capacity=capacity,
                                flow=flow,
                                weight=w)
                self.graph[v_from].append(new_edge)

    def add_edge(self, edge):
        edge_copy = edge.__copy__()
        self.graph[edge.vert_from].append(edge_copy)
        self.num_edges += 1
        return edge_copy

    def __getitem__(self, item):
        return self.graph[item]

    def __copy__(self):
        copy_instance = Graph()
        copy_instance.num_vertices = self.num_vertices
        copy_instance.num_edges = self.num_edges
        copy_instance.source = self.source
        copy_instance.sink = self.sink

        n = self.num_vertices
        copy_instance.graph = [[] for i in range(n)]
        for i in range(n):
            for j in range(len(self[i])):
                copy_instance[i].append(self[i][j])
        return copy_instance

    def drop_edges(self):
        for edge_list in self.graph:
            edge_list.clear()
        self.num_edges = 0


def calc_path_distance(gr: Graph, path_as_edges: List[Edge]):
    d = 0
    for edge in path_as_edges:
        d += edge.weight
    return d


def build_residual_graph(gr: Graph):
    n = gr.num_vertices
    # res_graph = [[] for i in range(n)]
    # Copy just for comfortable initialisation. TODO make it right
    res_graph = gr.__copy__()
    res_graph.drop_edges()
    for i in range(n):
        for j in range(len(gr[i])):
            current_edge = gr[i][j].__copy__()
            reverse_edge = current_edge.reverse()
            if current_edge.flow == FuzzyNumber(0):
                res_graph.add_edge(current_edge)
            if current_edge.flow > FuzzyNumber(0) and \
                    current_edge.flow < current_edge.capacity:
                res_graph.add_edge(current_edge)
                res_graph.add_edge(reverse_edge)
            if current_edge.flow == current_edge.capacity:
                res_graph.add_edge(reverse_edge)
    return res_graph


def ford_bellman(gr: Graph, s,  t):
    """
    Ford bellman algorithm
    :param gr: graph
    :param s: source
    :param t: sink
    :return: Shortest tour length, shortest tour path. Path is represented by graph vertices
    """
    gr_copy = gr.__copy__()
    # s, t = gr_copy.source, gr_copy.sink
    n = gr_copy.num_vertices
    d = [INF for i in range(n)]
    d[s] = 0
    p = [-1 for i in range(n)]
    while True:
        any_ = False
        for i in range(n):
            for j in range(len(gr_copy[i])):
                cur_edge = gr_copy[i][j]
                if d[cur_edge.vert_from] < INF:
                    if d[cur_edge.vert_to] > d[cur_edge.vert_from] + cur_edge.weight:
                        d[cur_edge.vert_to] = d[cur_edge.vert_from] + cur_edge.weight
                        p[cur_edge.vert_to] = cur_edge.vert_from
                        any_ = True
        if not any_:
            break
    if d[t] == INF:
        raise RuntimeError("No path found")
    # проверять путь на наличие ненасыщенного помеченного ребра. если такого нет, то?
    # как вариант, если путь не тот, то добавлять всем ребрам на текущем полученном пути + K к стоимости
    path = []
    cur_v = t
    while cur_v != -1:
        path.append(cur_v)
        cur_v = p[cur_v]
    path = list(reversed(path))
    # возвращать путь, как ребра за O(m) полным обходом(что, если есть кратные ребра?)
    return d[t], path


def convert_path_to_edges(gr: Graph, path):
    """
    Tries to build path as graph edges from vertices. If such path cant be made, an exception wiil be thrown.
    :param gr: graph
    :param path: path of vertices
    :return: path of edges
    """
    path_edges = []
    for i, vertex in enumerate(path[0:-1]):
        next_vertex = path[i+1]

        found = False
        for edge in gr[vertex]:
            if edge.vert_to == next_vertex:
                path_edges.append(edge)
                found = True
        if found:
            continue
        raise RuntimeError(f"Couldn't find corresponding edge for vertices ({vertex},{next_vertex})")
    return path_edges


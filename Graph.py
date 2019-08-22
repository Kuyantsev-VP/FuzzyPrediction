import os
from collections import deque
from typing import List

from Edge import Edge
from Fuzzy import FuzzyNumber
from util import *


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
            # TODO fix stupid line reading
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

    def __getitem__(self, item) -> List[Edge]:
        return self.graph[item]

    def __copy__(self):
        """
        Makes a copy of graph. Edges are not copied.
        :return:
        """
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

    def total_flow_log_entropy(self):
        raise NotImplementedError
        # TODO it is weird sht
        total_l_e = 0
        for i in range(self.num_vertices):
            for j in range(len(self.graph[i])):
                total_l_e = 0 + self.graph[i][j].flow.logarithmic_entropy()
        return total_l_e

    def get_graph_skeleton(self):
        g = []
        for i in range(self.num_vertices):
            g.append([])
            for j in range(len(self.graph[i])):
                g[i].append(0)
        return g

    def eval_source_flow(self):
        return sum((e.flow for e in self.graph[self.source]))

    def print_config_file(self, output=None):
        res = list()
        res.append(str(self.num_vertices))
        res.append(str(self.num_edges))
        res.append(str(self.source))
        res.append(str(self.sink))
        for i in range(self.num_vertices):
            for j in range(len(self.graph[i])):
                res.append(str(self.graph[i][j]))

        res_str = "\n".join(res)
        if output:
            with open(os.path.join(output), 'w') as out:
                out.write(res_str)
        else:
            print(res_str)

    def pretty(self):
        res = list()
        res.append("num_vert = " + str(self.num_vertices))
        res.append("num_edges = " + str(self.num_edges))
        res.append("source: " + str(self.source))
        res.append("sink: " + str(self.sink))
        for i in range(self.num_vertices):
            res.append(str(i) + ":")
            for edge in self.graph[i]:
                res.append("\t " + edge.pretty())
        return "\n".join(res)


##############################################


def bfs(gr: Graph, s, t) -> List[Edge]:
    queue = deque()
    queue.append(s)
    visited = [-1] * gr.num_vertices

    iter_counter = 0
    max_iter = 10000

    while len(queue) > 0:
        iter_counter += 1
        assert iter_counter < max_iter, "BFS max iteration count exceeded."
        u = queue.popleft()
        for edge in gr[u]:
            if edge.flow < edge.capacity and visited[edge.vert_to] == -1 and edge.vert_to != s:
                visited[edge.vert_to] = edge
                queue.append(edge.vert_to)
            if edge.vert_to == t:
                break
    path = list()
    if visited[t] != -1:
        u = t
        while visited[u] != -1:
            path.append(visited[u])
            u = visited[u].vert_from
        assert u == s, "BFS path does not contain the source."
    return [x for x in reversed(path)]


def calc_path_distance(path_as_edges: List[Edge]):
    d = 0
    for edge in path_as_edges:
        d += edge.weight
    return d


def str_path(path: List[Edge]):
    res = [str(path[0].vert_from)]
    for edge in path:
        res.append("->")
        res.append(str(edge.vert_to))
    return "".join(res)


def ford_bellman(gr: Graph, s, t):
    """
    Ford-Bellman algorithm for finding lowest cost path from s to t
    :param gr: graph
    :param s: source
    :param t: sink
    :return: Shortest tour length, shortest tour path. Path is represented by graph vertices
    """
    gr_copy = gr.__copy__()
    # s, t = gr_copy.source, gr_copy.sink
    n = gr_copy.num_vertices
    d = [INF] * n
    d[s] = 0
    p = [-1] * n
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
    Tries to build path as graph edges from vertices. If such path cant be made, an exception will be thrown.
    :param gr: graph
    :param path: path of vertices
    :return: path of edges from graph.
    """
    path_edges = []
    for i, vertex in enumerate(path[0:-1]):
        next_vertex = path[i + 1]

        found = False
        for edge in gr[vertex]:
            if edge.vert_to == next_vertex:
                path_edges.append(edge)
                found = True
        if found:
            continue
        raise RuntimeError(f"Couldn't find corresponding edge for vertices ({vertex},{next_vertex})")
    return path_edges

import Graph
from abc import ABC, abstractmethod
from typing import List
from Fuzzy import FuzzyNumber
from Edge import Edge
from util import INF


class Predictor(ABC):
    @abstractmethod
    def fit(self, g: Graph, new_edges: List[Edge]):
        pass

    @abstractmethod
    def predict(self):
        pass

    @abstractmethod
    def _prepare_graph_for_calc(self, g: Graph, new_edges: List[Edge]):
        pass

    @abstractmethod
    def _build_residual(self, g: Graph):
        pass


class FixedFlowPredictor(Predictor):
    def __init__(self, g, new_edges: List[Edge]):
        self.marked_edges = None
        self.fixed_flow = None
        self.prepared_graph = None
        self.prediction = None
        # self.residual = None
        self.fit(g, new_edges)

    def fit(self, g: Graph, new_edges):
        self.fixed_flow = self._calculate_fixed_flow(g)
        self.marked_edges, self.prepared_graph = self._prepare_graph_for_calc(g, new_edges)
        # self.residual = self._build_residual()

    def predict(self):
        current_flow = FuzzyNumber(0)
        s, t = self.prepared_graph.source, self.prepared_graph.sink

        counter = 0
        current_graph = self.prepared_graph.__copy__()
        while current_flow < self.fixed_flow:
            counter += 1
            # 1.  Gf
            res_gr = self._build_residual(current_graph)

            best_dist = INF
            best_path = []
            residual_path = []
            for new_edge in self.marked_edges:
                if new_edge.flow == new_edge.capacity:
                    continue

                v_from = new_edge.vert_from
                v_to = new_edge.vert_to
                edge_weight = new_edge.weight

                path_to_edge_dist, path_to_e = Graph.ford_bellman(res_gr, s, v_from)
                path_from_edge_dist, path_from_e = Graph.ford_bellman(res_gr, v_to, t)

                if path_to_edge_dist + edge_weight + path_from_edge_dist < best_dist:
                    best_dist = path_to_edge_dist + edge_weight + path_from_edge_dist

                    # Building path as edges by the visited vertices in G
                    ## Converting path of vertices to path of edges returns refs on edges from current_graph
                    best_path = Graph.convert_path_to_edges(current_graph, path_to_e)
                    best_path.append(new_edge)
                    best_path.extend(Graph.convert_path_to_edges(current_graph, path_from_e))

                    # Building path as edges by the visited vertices in G_f
                    residual_path = Graph.convert_path_to_edges(res_gr, path_to_e)
                    residual_path.append(new_edge)
                    residual_path.extend(Graph.convert_path_to_edges(res_gr, path_from_e))
            if best_dist == INF:
                raise RuntimeError("No path through the marked edge was found BUT graph was not saturated")

            min_flow = FuzzyNumber(0, INF, 0)
            for i, edge in enumerate(best_path):
                # TODO dangerous. logic is hidden.
                if residual_path[i].reversed:
                    min_flow = min(min_flow, edge.flow)
                else:
                    min_flow = min(min_flow, edge.capacity - edge.flow)
            min_flow = min(min_flow, self.fixed_flow - current_flow)

            for edge in best_path:
                edge.flow = edge.flow + min_flow
            current_flow = current_flow + min_flow
        self.prediction = current_graph
        return current_graph

    def _calculate_fixed_flow(self, g: Graph):
        """
        Now it calculates total flow of original graph.
        :param g:
        :return: total flow from the source
        """
        return g.eval_source_flow

    def _prepare_graph_for_calc(self, g: Graph, new_edges):
        """
        Initialises marked edges and pre-graph for further calculations.
        Pre-graph is copy of original graph with zero-flow edges.
        :param g:
        :param new_edges:
        :return:
        """
        # 0. Preparing graph
        # 0.1. Marking new edges
        pr_gr = g.__copy__()
        for new_edge in new_edges:
            new_edge.mark = True
            pr_gr.add_edge(new_edge)

        # 0.2. Initialising flows by zero value
        marked_edges = []
        zero_flow = FuzzyNumber(0)
        for i in range(g.num_vertices):
            for j in range(len(pr_gr[i])):
                # TODO UNNECESSARY COPING AND SETTING
                current_edge = pr_gr[i][j].__copy__()
                if current_edge.mark:
                    current_edge.capacity = current_edge.flow
                    marked_edges.append(current_edge)
                current_edge.flow = zero_flow
                pr_gr[i][j] = current_edge
        return marked_edges, pr_gr

    def _build_residual(self, g: Graph):
        n = g.num_vertices
        # res_graph = [[] for i in range(n)]
        # Copy just for comfortable initialisation. TODO make it right
        res_graph = g.__copy__()
        res_graph.drop_edges()
        for i in range(n):
            for j in range(len(g[i])):
                current_edge = g[i][j].__copy__()
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


class MaxFlowPredictor(Predictor):
    def __init__(self, g, new_edges: List[Edge]):
        self.marked_edges = None
        self.prepared_graph = None
        self.residual_graph = None
        self.prediction = None
        self.fit(g, new_edges)

    def fit(self, g: Graph, new_edges: List[Edge]):
        self.marked_edges, self.prepared_graph = self._prepare_graph_for_calc(g, new_edges)
        self.residual_graph = self._build_residual(self.prepared_graph)

    def predict(self) -> Graph:
        """
        Edmonds-Karp's algorithm

        :return:
        """
        s, t = self.prepared_graph.source, self.prepared_graph.sink

        flow = FuzzyNumber(0)

        # First fill up marked edges, then all the rest
        marked_edges_to_fill = set(self.marked_edges)
        while True:
            while len(marked_edges_to_fill) > 0:
                edge = marked_edges_to_fill.pop()

                path = self._find_path(self.residual_graph, s, t, through_edge=edge)

                # If path through the current marked edge does not exist,
                # skip current edge and don't consider it again
                if len(path) == 0:
                    continue

                d_flow = self._augment_path(path)
                flow += d_flow

                # If path is found and marked edge still has capacity,
                # push it back to consider it later
                if edge.flow < edge.capacity:
                    marked_edges_to_fill.add(edge)
                print("found through")
                print("\t", Graph.str_path(path), "added flow:", d_flow)

            path = self._find_path(self.residual_graph, s, t)
            if len(path) == 0:
                break

            d_flow = self._augment_path(path)
            flow += d_flow

            print("found")
            print("\t", Graph.str_path(path), "added flow:", d_flow)
        print("TOTAL FLOW", flow)
        return self.residual_graph

    def _find_path(self, g: Graph, s: int, t: int, through_edge=None) -> List[Edge]:
        """
        Finds path in given graph from source s to sink t.
        :param g: graph
        :param s: source
        :param t: sink
        :param through_edge: (optional) if provided, method will return path through specified edge
        :return: path from s to t. If path is not found, empty list will be returned
        """
        if through_edge:
            v_from = through_edge.vert_from
            v_to = through_edge.vert_to

            path_to_edge = Graph.bfs(g, s, v_from)
            path_from_edge = Graph.bfs(g, v_to, t)

            # If path through the current marked edge does not exist,
            # skip current edge and don't consider it again
            if s != v_from and len(path_to_edge) == 0:
                return []
            if t != v_to and len(path_from_edge) == 0:
                return []

            path = path_to_edge
            path.append(through_edge)
            path.extend(path_from_edge)
            return path
        return Graph.bfs(g, s, t)

    def _augment_path(self, path: List[Edge]) -> FuzzyNumber:
        """
        Calculates minimum value among capacities of residual graph and adjust it to all edges of the path.
        NOTE edges are considered to be edge-objects of residual graph
        :param path: path to augment
        :return: adjusted flow
        """
        df = min((e.capacity - e.flow for e in path))
        # dfs = [FuzzyNumber(0)] * len(path)
        # for e in path:
        #     if e.flow + df < e.capacity
        for e in path:
            if e.is_reversed:
                e.flow -= df
            else:
                e.flow += df
        return df

    def _prepare_graph_for_calc(self, g: Graph, new_edges: List[Edge]):
        """
        Prepares graph for further calculations.
        :param g:
        :param new_edges:
        :return:
        """
        # 0. Preparing graph
        # 0.1. Marking new edges
        pr_gr = g.__copy__()
        for new_edge in new_edges:
            new_edge.mark = True
            pr_gr.add_edge(new_edge)

        # 0.2. Initialising flows by zero value
        marked_edges = []
        for i in range(g.num_vertices):
            for j in range(len(pr_gr[i])):
                current_edge = pr_gr[i][j]
                if current_edge.mark:
                    current_edge.capacity = current_edge.flow
                    marked_edges.append(current_edge)
                current_edge.flow = FuzzyNumber(0)
        return marked_edges, pr_gr

    def _build_residual(self, g: Graph) -> Graph:
        """
        Creates residual graph. Direct edges are the same objects as in original graph.
        :param g: original graph.
        :return: residual graph
        """
        n = g.num_vertices
        res_graph = g.__copy__()
        for i in range(n):
            for edge in g[i]:
                current_flow = edge.flow
                current_cap = edge.capacity

                edge.capacity = current_cap
                rev = edge.reverse()
                # TODO THIS NEGATION COULD BE TOTALLY WRONG
                rev.flow = FuzzyNumber(0) - current_flow
                rev.capacity = current_cap
                res_graph.add_edge(rev)
        return res_graph

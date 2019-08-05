from Graph import *


def prediction(initial_graph: Graph, edges_to_add: List[Edge]):
    # Без кратных рёбер
    fixed_flow = FuzzyNumber(0)
    for i in range(len(initial_graph[initial_graph.source])):
        fixed_flow = fixed_flow + initial_graph[initial_graph.source][i].flow
    n, m = initial_graph.num_vertices, initial_graph.num_edges
    cur_gr = initial_graph.__copy__()

    # 0. Preparing graph
    # 0.1. Marking new edges
    for new_edge in edges_to_add:
        new_edge.mark = True
        cur_gr.add_edge(new_edge)

    # 0.2. Initialising flows by zero value
    added_edges = []
    zero_flow = FuzzyNumber(0, 0, 0)
    for i in range(n):
        for j in range(len(cur_gr[i])):
            # TODO UNNECESSARY COPING AND SETTING
            current_edge = cur_gr[i][j].__copy__()
            if current_edge.mark:
                current_edge.capacity = current_edge.flow
                added_edges.append(current_edge)
            current_edge.flow = zero_flow
            cur_gr[i][j] = current_edge

    current_flow = FuzzyNumber(0)
    s, t = initial_graph.source, initial_graph.sink
    counter = 0
    while current_flow < fixed_flow:
        counter += 1
        # 1.  Gf
        # print(fixed_flow)
        res_gr = build_residual_graph(cur_gr)

        best_dist = INF
        best_path = []
        residual_path = []
        for new_edge in added_edges:
            if new_edge.flow == new_edge.capacity:
                continue

            v_from = new_edge.vert_from
            v_to = new_edge.vert_to
            edge_weight = new_edge.weight

            path_to_edge_dist, path_to_e = ford_bellman(res_gr, s, v_from)
            path_from_edge_dist, path_from_e = ford_bellman(res_gr, v_to, t)

            if path_to_edge_dist + edge_weight + path_from_edge_dist < best_dist:
                best_dist = path_to_edge_dist + edge_weight + path_from_edge_dist

                # Building path as edges by the vertices in G
                best_path = convert_path_to_edges(cur_gr, path_to_e)
                best_path.append(new_edge)
                best_path.extend(convert_path_to_edges(cur_gr, path_from_e))

                # Building path as edges by the vertices in G_f
                residual_path = convert_path_to_edges(res_gr, path_to_e)
                residual_path.append(new_edge)
                residual_path.extend(convert_path_to_edges(res_gr, path_from_e))
        if best_dist == INF:
            raise RuntimeError("No path through the marked edge was found BUT graph was not saturated")

        min_flow = FuzzyNumber(0, INF, 0)
        for i, edge in enumerate(best_path):
            if residual_path[i].reversed:
                min_flow = min(min_flow, edge.flow)
            else:
                min_flow = min(min_flow, edge.capacity - edge.flow)
        min_flow = min(min_flow, fixed_flow - current_flow)

        for edge in best_path:
            edge.flow = edge.flow + min_flow
        current_flow = current_flow + min_flow
        
    a = 1


if __name__ == '__main__':
    g = Graph('input')
    fuzz_edge = Edge(2, 3, FuzzyNumber(0, 7, 0), FuzzyNumber(1, 5, 2), 3)

    prediction(g, [fuzz_edge])
    a = 1

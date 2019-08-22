from Graph import *
from Predictor import FixedFlowPredictor, MaxFlowPredictor
import copy




def optimisation_fm(g: Graph, fuzziness_limit: float, expert_prices: List[List[float]]):
    """
    First method of optimisation
    :param g: input graph
    :param fuzziness_limit: numeric limit for fuzziness of flows
    :param expert_prices: price of expert work for each edge
    :return: optimised graph
    """
    n, m = g.num_vertices, g.num_edges
    bad_edges = []
    bad_edges_indices = []
    for i in range(n):
        for j in range(len(g[i])):
            if g[i][j].flow.logarithmic_entropy() > fuzziness_limit:
                bad_edges.append(g[i][j])
                bad_edges_indices.append((i, j))
    # if len(bad_edges) == 0:
    #     return

    initial_entropy = g.total_flow_log_entropy()
    alphas = g.get_graph_skeleton()

    while len(bad_edges_indices) > 0:
        g_copy = g.__copy__()
        i, j = bad_edges.pop(0)
        g_copy[i].pop(j)
        g_copy.total_flow_log_entropy()



if __name__ == '__main__':
    g = Graph('input')
    # g.print_config_file('output')
    fuzz_edge = Edge(2, 3, FuzzyNumber(0, 7, 0), FuzzyNumber(1, 5, 2), 3)

    mf_pred = MaxFlowPredictor(g, [fuzz_edge])
    final_gr = mf_pred.predict()
    print(final_gr.pretty())
    # optimisation_fm(g, 0.5, [[]])
    a = 1

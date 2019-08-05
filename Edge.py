class Edge:
    def __init__(self, vert_from, vert_to, capacity, flow, weight):
        self.vert_from = vert_from
        self.vert_to = vert_to
        self.capacity = capacity
        self.flow = flow
        self.weight = weight
        self.mark = False
        self.reversed = False

    def __copy__(self):
        edge_copy = Edge(self.vert_from, self.vert_to, self.capacity, self.flow, self.weight)
        edge_copy.mark = self.mark
        edge_copy.reversed = self.reversed
        return edge_copy

    def __repr__(self):
        return f"({self.vert_from},{self.vert_to}), f={self.flow}, c={self.capacity}, w={self.weight}"

    def reverse(self):
        copy_inst = self.__copy__()
        fr = copy_inst.vert_from
        copy_inst.vert_from = copy_inst.vert_to
        copy_inst.vert_to = fr
        copy_inst.weight = - copy_inst.weight
        copy_inst.reversed = True
        return copy_inst

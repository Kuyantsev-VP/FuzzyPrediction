class Edge:
    def __init__(self, vert_from, vert_to, capacity, flow, weight):
        self.vert_from = vert_from
        self.vert_to = vert_to
        self.capacity = capacity
        self.flow = flow
        self.weight = weight
        self.mark = False
        self.is_reversed = False
        self.rev_link = None
        ###
        self.original_capacity = capacity
        self.pseudo_filled = False
        ###

    def __copy__(self):
        edge_copy = Edge(self.vert_from, self.vert_to, self.capacity, self.flow, self.weight)
        edge_copy.mark = self.mark
        edge_copy.is_reversed = self.is_reversed
        return edge_copy

    def __repr__(self):
        return f"({self.vert_from},{self.vert_to}), f={self.flow}, c={self.capacity}, w={self.weight}"

    def __str__(self):
        return f"{self.vert_from} {self.vert_to}\n{self.flow}\n{self.capacity}\n{self.weight}"

    def pretty(self):
        s = f"({self.vert_from}->{self.vert_to}), f=<{self.flow}>, c=<{self.capacity}>, w={self.weight}"
        if self.is_reversed:
            s += " (REV)"
        return s

    def reverse(self):
        """
        Creates instance of reversed edge and link to it's object
        :return: instance of reversed edge and link to it's object
        """
        copy_inst = self.__copy__()
        fr = copy_inst.vert_from
        copy_inst.vert_from = copy_inst.vert_to
        copy_inst.vert_to = fr

        copy_inst.weight = - copy_inst.weight

        copy_inst.rev_link = self
        self.rev_link = copy_inst

        copy_inst.is_reversed = True
        return copy_inst

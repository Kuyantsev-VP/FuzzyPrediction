class FuzzyNumber:
    def __init__(self, *args):
        self.l = 0
        self.val = 0
        self.r = 0
        if len(args) == 1:
            self.val = args[0]
        if len(args) == 3:
            self.l = args[0]
            self.val = args[1]
            self.r = args[2]

    def __add__(self, other):
        if isinstance(other, FuzzyNumber):
            return FuzzyNumber(self.l + other.l, self.val + other.val, self.r + other.r)
        # if isinstance(other, Number):
        #     return FuzzyNumber(self.l, self.val + other, self.r)
        raise TypeError("Object is not a number of fuzzy number.")

    def __sub__(self, other):
        if isinstance(other, FuzzyNumber):
            return FuzzyNumber(self.l + other.l, self.val - other.val, self.r + other.r)
        # if isinstance(other, Number):
        #     return FuzzyNumber(self.l, self.val - other, self.r)
        raise TypeError("Object is not a number of fuzzy number.")

    def __lt__(self, other):
        if isinstance(other, FuzzyNumber):
            return self.val + (self.r - self.r) / 4 < other.val + (other.r - other.l) / 4
        # if isinstance(other, Number):
        #     return self.val + (self.r - self.r) / 4 < other
        raise TypeError("Object is not a number of fuzzy number.")

    def __eq__(self, other):
        return self.val == other.val and self.l == other.l and self.r == other.r

    def is_explicit(self):
        return self.l == 0 and self.r == 0

    def __repr__(self):
        return f"<{self.l},{self.val},{self.r}>"

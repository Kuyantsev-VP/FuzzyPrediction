import numpy as np
from main import FuzzyNumber

a = [1,2,3]
b = (*a,)
c = reversed(a)
a2 = [4,5,6]
a.extend(a2)

cf = FuzzyNumber(1,2,3)
f = FuzzyNumber(0,6,2)
v = FuzzyNumber(0,0,0)
g = min(f,v)
print(b)

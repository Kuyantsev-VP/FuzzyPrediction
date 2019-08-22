# import numpy as np
from Fuzzy import FuzzyNumber
#
# a = [1,2,3]
# b = (*a,)
# c = reversed(a)
# a2 = [4,5,6]
# a.extend(a2)
#
# cf = FuzzyNumber(1,2,3)
# f = FuzzyNumber(0,6,2)
# v = FuzzyNumber(0,0,0)
# g = min(f,v)
# print(b)

# import copy
#
# a = [[1,2,3], [4,5,6]]
# b= copy.deepcopy(a)
# b[0][0]=666
# print(a)
# print(b)
#
# c = []
# c.append([])
# print(c)

a= FuzzyNumber(1)
b=FuzzyNumber(2)
c=FuzzyNumber(3)

print(FuzzyNumber(1.0,10.0,2.0) < FuzzyNumber(0.0,10.0,0.0))



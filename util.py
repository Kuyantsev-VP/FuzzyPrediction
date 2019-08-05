INF = float('inf')


def to_float(arr):
    return [float(x) for x in arr]


def to_int(arr):
    return [int(x) for x in arr]


def dist(coords_a, coords_b):
    assert len(coords_b) == len(coords_a), "Vectors of different length"
    return sum(((coords_a[i] - coords_b[i]) ** 2 for i in range(len(coords_a)))) ** (1 / 2)

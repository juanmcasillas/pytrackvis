def manhattan_distance(a,b):
    # Σ|Ai – Bi|
    return sum(abs(val1-val2) for val1, val2 in zip(a,b))

def manhattan_point(p1,p2):
    a = [p1.latitude, p1.longitude, p1.elevation]
    b = [p2.latitude, p2.longitude, p2.elevation]
    return sum(abs(val1-val2) for val1, val2 in zip(a,b))


def module(vector):
    return math.sqrt(sum(v**2 for v in vector))


def track_similarity(trk1, trk2):
    # iterate the track with less points, and calculate
    # the sum of the manhattan_distance between points.

    if len(trk1.points) >= len(trk2.points):
        max_points = len(trk2.points) 
    else:
        max_points = len(trk1.points)

    similarity = 0.0
    for i in range(0,max_points):
        similarity += manhattan_point(trk1.points[i], trk2.points[i])

    return similarity / max_points 

if __name__ == "__main__":
    a = [ 1, 2, 3, 4, 5, 7, 8, 9, 10 ]
    b = [ 1, 2, 3, 4, 5 ]

    len_a = len(a)
    len_b = len(b)

    print("a", len_a)
    print("b", len_b)

    what = "-"
    if len_b != len_a:
        if len_b > len_a:
            diff = len_b - len_a
            a += [0] *diff
        else:
            diff = len_a - len_b
            b += [0] *diff

    print("the smallest is %s" % what)
    print(a)
    print(b)


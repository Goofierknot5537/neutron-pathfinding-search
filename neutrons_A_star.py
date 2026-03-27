# A lot of this was taken from https://www.datacamp.com/tutorial/a-star-algorithm
import heapq
import neutrons_kdtree

class A_Node:
    def __init__(self, coords: tuple[float, float, float], g: float, h: float, id64: int):
        self.coords = coords
        self.g = g
        self.h = h
        self.f = h + g
        self.parent = None
        self.id64 = id64

def heuristic_calc(x1, y1, z1):
    "Returns estimated best-case jumps from coords to Colonia"
    dist = neutrons_kdtree.find_coord_distance(x1, y1, z1, -9530.5, -910.28125, 19808.125)
    return dist / 554

def reconstruct_path(goal_node: A_Node):
    path = []
    current = goal_node
    while current != None:
        path.append(current.id64)
        current = current.parent

    return path[::-1]

def find_path():
    kd_tree = neutrons_kdtree.make_tree()

    start = A_Node((0, 0, 0), 0, heuristic_calc(0, 0, 0), 10477373803)

    open_list = [(start.f, start.coords)]
    open_dict = {start.coords: start}
    closed_set = set()
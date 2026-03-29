import jsonlines
import math
from scipy.spatial import KDTree
import numpy as np

class Node:
    def __init__(self, pos: tuple[float, float, float], id64: int):
        self.left = None
        self.right = None
        self.pos = pos
        self.id64 = id64

def make_tree():
    nodes_coords = []
    nodes_data = []
    with jsonlines.open("neutrons_stripped.jsonl", mode='r') as reader:
        for line in reader:
            coords = line["crds"]
            id64 = line["id"]
            nodes_coords.append((coords['x'], coords['y'], coords['z']))
            nodes_data.append(((coords['x'], coords['y'], coords['z']), id64))
        reader.close()
    
    coords_array = np.array(nodes_coords)
    kd_tree = KDTree(coords_array)

    return kd_tree, nodes_data

def test():
    kd_tree, nodes_data = make_tree()
    print("Tree made")
    indicies = kd_tree.query_ball_point((-4942.9375, -2128.84375, 18043.6875), 500, workers=4)
    for i in indicies:
        point1 = nodes_data[i][0]
        print(find_coord_distance(point1, (-4942.9375, -2128.84375, 18043.6875)))
    

def kd_create(nodes: list[tuple:[float, float, float], int], depth) -> None:
    "Obsolete"
    if not nodes:
        return None
    # previous kdtree is unbalanced, so sort nodes by axis, then pick the median as the parent
    axis = depth % 3 # 0 = x, 1 = y, 2 = z
    nodes.sort(key=lambda node: node[0][axis])
    median = len(nodes) // 2

    node = Node(nodes[median][0], nodes[median][1])
    node.left = kd_create(nodes[:median], depth + 1)
    node.right = kd_create(nodes[median + 1:], depth + 1)

    return node

def radius_search(kd_root: Node, point: tuple[float, float, float], dist_sq: float, depth: int, result: list) -> None:
    "Obsolete"
    if kd_root == None:
        return None
    axis = depth % 3 # 0 = x, 1 = y, 2 = z
    data = kd_root.pos
    if node_in_radius(kd_root, point, dist_sq):
        result.append(kd_root)

    plane_dist = point[axis] - data[axis]
    
    if plane_dist <= 0:
        close, far = kd_root.left, kd_root.right
    else:
        far, close = kd_root.left, kd_root.right

    radius_search(close, point, dist_sq, depth + 1, result)

    if plane_dist**2 <= dist_sq:
        radius_search(far, point, dist_sq, depth + 1, result)

def node_in_radius(node: Node, point: tuple[float, float, float], radius_sq: float) -> bool:
    "Obsolete"
    dx = node.pos[0] - point[0]
    dy = node.pos[1] - point[1]
    dz = node.pos[2] - point[2]
    if dx**2 + dy**2 + dz**2 <= radius_sq:
        return True
    return False

def find_coord_distance(point1: tuple[float, float, float], point2: tuple[float, float, float]) -> float:
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

if __name__ == "__main__":
    test()
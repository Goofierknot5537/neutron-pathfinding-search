import jsonlines
import math
import datetime

class Node:
    def __init__(self, pos: tuple[float, float, float], id64: int):
        self.left = None
        self.right = None
        self.pos = pos
        self.id64 = id64

def make_tree():
    nodes = []
    with jsonlines.open("neutrons_stripped.jsonl", mode='r') as reader:
        for line in reader:
            coords = line["crds"]
            id64 = line["id"]
            nodes.append(((coords['x'], coords['y'], coords['z']), id64))
        reader.close()
    
    return kd_create(nodes, 0)

def test():
    root = make_tree()
    nodes = []
    radius_search(root, (-4942.9375, -2128.84375, 18043.6875), 8000**2, 0, nodes)
    with jsonlines.open("neutrons_test.jsonl", mode='w', compact=True) as writer:
        for node in nodes:
            line = {"id":node.id64,"crds":{"x":node.pos[0],"y":node.pos[1],"z":node.pos[2]}}
            writer.write(line)
    

def kd_create(nodes: list[tuple:[float, float, float], int], depth) -> None:
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
    dx = node.pos[0] - point[0]
    dy = node.pos[1] - point[1]
    dz = node.pos[2] - point[2]
    if dx**2 + dy**2 + dz**2 <= radius_sq:
        return True
    return False

def find_coord_distance(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

if __name__ == "__main__":
    test()
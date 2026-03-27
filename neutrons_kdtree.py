import jsonlines
import math
import datetime

class Node:
    def __init__(self, data: tuple[float, float, float], id64: int):
        self.left = None
        self.right = None
        self.data = data
        self.id64 = id64

def make_tree():
    with jsonlines.open("neutrons_stripped.jsonl", mode='r') as reader:
        first = reader.read()
        coords = first["crds"]
        root = Node((coords['x'], coords['y'], coords['z']), first["id"])

        for line in reader:
            coords = line["crds"]
            id64 = line["id"]
            kd_insert(root, (coords['x'], coords['y'], coords['z']), id64)
        reader.close()
    
    return root

def test():
    root = make_tree()
    nodes = radius_search(root, (-4942.9375, -2128.84375, 18043.6875), 100, 0)
    for node in nodes:
        print(node.id64)

# https://opendsa-server.cs.vt.edu/ODSA/Books/CS3/html/KDtree.html Example 15.5.3
def radius_search(kd_root: Node, point: tuple[float, float, float], dist: float, depth: int) -> list[Node]:
    if kd_root == None:
        return []
    node_list = []
    axis = depth % 3 # 0 = x, 1 = y, 2 = z
    data = kd_root.data
    if node_in_radius(kd_root, point, dist):
        node_list.append(kd_root)
    if data[axis] >= (point[axis] - dist):
        node_list.extend(radius_search(kd_root.left, point, dist, depth + 1))
    if data[axis] < (point[axis] + dist):
        node_list.extend(radius_search(kd_root.right, point, dist, depth + 1))

    return node_list
    

def kd_insert(root: Node, data: tuple[float, float, float], id64: int) -> None:
    depth = 0
    node = Node(data, id64)
    current = root
    while True:
        axis = depth % 3 # 0 = x, 1 = y, 2 = z
        if data[axis] < current.data[axis]:
            if current.left == None:
                current.left = node
                return
            else:
                current = current.left
                depth += 1
        else: #data[axis] >= current.data[axis]
            if current.right == None:
                current.right = node
                return
            else:
                current = current.right
                depth += 1

def node_in_radius(node: Node, point: tuple[float, float, float], dist: float) -> bool:
    data = node.data
    if find_coord_distance(data[0], data[1], data[2], point[0], point[1], point[2]) < dist:
        return True
    return False

def find_coord_distance(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

if __name__ == "__main__":
    test()
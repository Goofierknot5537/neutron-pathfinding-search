import jsonlines
import math

class Node:
    def __init__(self, data: tuple[float, float, float]):
        self.left = None
        self.right = None
        self.data = data

def make_tree():
    with jsonlines.open("neutrons_stripped.jsonl", mode='r') as reader:
        first = reader.read()
        coords = first["crds"]
        root = Node((coords['x'], coords['y'], coords['z']))

        for line in reader:
            coords = line["crds"]
            kd_insert(root, (coords['x'], coords['y'], coords['z']))
        reader.close()
    
    return root
    #radius_search(root, (-4942.9375, -2128.84375, 18043.6875), 100, 0)

# https://opendsa-server.cs.vt.edu/ODSA/Books/CS3/html/KDtree.html Example 15.5.3
def radius_search(kd_root: Node, point: tuple[float, float, float], dist: float, depth: int) -> None:
    if kd_root == None:
        return None
    axis = depth % 3
    data = kd_root.data
    if node_in_radius(kd_root, point, dist):
        print(f"{data} - depth {depth}")
    if data[axis] > (point[axis] - dist):
        radius_search(kd_root.left, point, dist, depth + 1)
    if data[axis] < (point[axis] + dist):
        radius_search(kd_root.right, point, dist, depth + 1)

def kd_insert(root: Node, data: tuple[float, float, float]) -> None:
    depth = 0
    node = Node(data)
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
    make_tree()
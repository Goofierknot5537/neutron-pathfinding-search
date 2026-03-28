# A lot of this was taken from https://www.datacamp.com/tutorial/a-star-algorithm
import heapq
import kdtree
import math

class A_Node: # terrible since it's nowhere consistent with nodes in kdtree, but I'm too lazy to change it rn
    def __init__(self, coords: tuple[float, float, float], jumps: int, h: float, id64: int):
        self.coords = coords
        self.jumps = jumps
        self.h = h
        self.f = jumps + h
        self.parent = None
        self.fuel = None
        self.id64 = id64

# https://opendsa-server.cs.vt.edu/ODSA/Books/CS3/html/KDtree.html Example 15.5.3
def radius_search(kd_root: kdtree.Node, point: tuple[float, float, float], dist: float, depth: int) -> list[kdtree.Node]:
    if kd_root == None:
        return []
    node_list = []
    axis = depth % 3 # 0 = x, 1 = y, 2 = z
    data = kd_root.pos
    if node_in_radius(kd_root, point, dist):
        node_list.append(kd_root)
    if data[axis] >= (point[axis] - dist):
        node_list.extend(radius_search(kd_root.left, point, dist, depth + 1))
    if data[axis] < (point[axis] + dist):
        node_list.extend(radius_search(kd_root.right, point, dist, depth + 1))

    return node_list

def node_in_radius(node: kdtree.Node, point: tuple[float, float, float], dist: float) -> bool:
    data = node.pos
    if find_coord_distance(data[0], data[1], data[2], point[0], point[1], point[2]) < dist:
        return True
    return False

def find_coord_distance(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def heuristic_calc(coords: tuple[float, float, float]):
    "Returns estimated best-case jumps from coords to Colonia"
    x1, y1, z1 = coords
    dist = find_coord_distance(x1, y1, z1, -9530.5, -910.28125, 19808.125)
    return dist / 554

def reconstruct_path(goal_node: A_Node):
    path = []
    current = goal_node
    while current != None:
        path.append(current.id64)
        current = current.parent

    return path[::-1]

# From EDSY https://github.com/taleden/EDSY/blob/master/edsy.js
# Stats are manually chosen from my Caspian build
def getJumpFuelCost(dist: float, fuel: float):
    maxDist = getJumpDistance(fuel)
    return (dist / maxDist)**2.5025 * min(fuel, 6.8)

def getJumpDistance(fuel: float):
    dist = (min(fuel, 6.8) / 0.011)**(1 / 2.5025) * (7528.04 / (1194.07 + fuel)) + 10.5
    return dist * 6

def find_path():
    print("Starting")
    kd_tree = kdtree.make_tree()
    print("Tree made, starting pathfinding")
    # 3 Capricorni -210.53125, -186.59375, 342.40625
    start = A_Node((-4682.65625, -2902.625, 17540.3125), 0, heuristic_calc((-4682.65625, -2902.625, 17540.3125)), 22663776292)
    goal = (-4909.0625, -2045.21875, 19005.40625)
    # Colonia -9530.5, -910.28125, 19808.125

    start.fuel = 304

    open_list = [(start.f, start.coords, start.fuel)]
    open_dict = {start.coords: start}
    closed_set = set()
    i = 0
    while open_list:
        _, current_pos, current_fuel = heapq.heappop(open_list)
        current_node = open_dict[current_pos]

        if current_pos == goal:
            return reconstruct_path(current_node)
        
        closed_set.add(current_node.id64)
        if i % 100 == 0:
            print(f"Node {i} added")
        i += 1

        for neighbor_node in radius_search(kd_tree, current_pos, getJumpDistance(current_fuel), 0):
            if neighbor_node.id64 in closed_set:
                continue
            neighbor_pos = neighbor_node.pos
            x1, y1, z1 = neighbor_pos
            x2, y2, z2 = current_pos
            fuel_used = getJumpFuelCost(find_coord_distance(x1, y1, z1, x2, y2, z2), current_fuel) # terrible

            if neighbor_pos not in open_dict:
                neighbor = A_Node(neighbor_pos, current_node.jumps + 1, heuristic_calc(neighbor_pos), neighbor_node.id64)
                neighbor.parent = current_node
                neighbor.fuel = current_fuel - fuel_used

                heapq.heappush(open_list, (neighbor.f, neighbor.coords, neighbor.fuel))
                open_dict[neighbor_pos] = neighbor
            elif current_node.jumps + 1 <= open_dict[neighbor_pos].jumps and current_fuel - fuel_used >= open_dict[neighbor_pos].fuel:
                neighbor = open_dict[neighbor_pos]
                neighbor.jumps = current_node.jumps + 1
                neighbor.f = neighbor.jumps + neighbor.h
                neighbor.fuel = current_fuel - fuel_used
                neighbor.parent = current_node
    return []

if __name__ == "__main__":
    path = find_path()
    print(path)
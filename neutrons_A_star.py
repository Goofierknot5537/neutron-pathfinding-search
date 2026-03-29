# A lot of this was taken from https://www.datacamp.com/tutorial/a-star-algorithm
# The LLM Claude was used for some optimizations related to the kdtree and radius search,
# everything else was typed by hand.
import heapq
import kdtree
import math
import cProfile

class A_Node: # terrible since it's nowhere consistent with nodes in kdtree, but I'm too lazy to change it rn
    def __init__(self, coords: tuple[float, float, float], jumps: int, h: float, id64: int):
        self.coords = coords
        self.jumps = jumps
        self.h = h
        self.f = jumps + h
        self.parent = None
        self.fuel = None
        self.id64 = id64

def radius_search(kd_root: kdtree.Node, point: tuple[float, float, float], dist_sq: float, depth: int, result: list) -> None:
    if kd_root == None:
        return None
    axis = depth % 3 # 0 = x, 1 = y, 2 = z
    data = kd_root.pos
    if node_in_radius(kd_root, point, dist_sq):
        result.append(kd_root)

    plane_dist = point[axis] - data[axis]
    
    # Only search sides within our search radius
    if plane_dist <= 0:
        close, far = kd_root.left, kd_root.right
    else:
        far, close = kd_root.left, kd_root.right

    radius_search(close, point, dist_sq, depth + 1, result)

    if plane_dist**2 <= dist_sq:
        radius_search(far, point, dist_sq, depth + 1, result)

def node_in_radius(node: kdtree.Node, point: tuple[float, float, float], radius_sq: float) -> bool:
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

def heuristic_calc(coords: tuple[float, float, float], goal: tuple[float, float, float]):
    dist = find_coord_distance(coords, goal)
    return dist / 554

def reconstruct_path(goal_node: A_Node):
    path = []
    current = goal_node
    while current != None:
        path.append([(current.coords), current.fuel, current.id64])
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

    # A dynamic weight. This will decrease gradually until it reaches 1.
    # This makes it so A* acts greedily until a certain point, so it can find a semi-optimal path
    # After optimizations, though, this became obsolete.
    dyn_w = 0.0

    # Colonia -9530.5, -910.28125, 19808.125
    # {"id":3238296097059,"crds":{"x":-9530.5,"y":-910.28125,"z":19808.125}}
    goal = 3238296097059
    goal_pos = (-9530.5, -910.28125, 19808.125)
    start_id = 10477373803
    start_pos = (0, 0, 0)
    start = A_Node(start_pos, 0, (1 + dyn_w) * heuristic_calc(start_pos, goal_pos), start_id)
    # 3 Capricorni -210.53125, -186.59375, 342.40625
    # {"id":4994888293,"crds":{"x":-210.53125,"y":-186.59375,"z":342.40625}}
    # Sol 0, 0, 0
    # {"id":10477373803,"crds":{"x":0,"y":0,"z":0}}

    start.fuel = 310

    open_list = [(start.f, start.coords, start.fuel, start.id64)]
    open_dict = {start.id64: start}
    closed_set = set()

    while open_list:
        _, current_pos, current_fuel, cur_id64 = heapq.heappop(open_list)
        current_node = open_dict[cur_id64]
        open_dict.pop(cur_id64)

        if cur_id64 == goal:
            print("Goal found, getting path")
            return reconstruct_path(current_node)
        
        closed_set.add(current_node.id64)
        x1, y1, z1 = current_pos
        x2, y2, z2 = goal_pos
        dist2 = (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2

        if dyn_w > 1:
            dyn_w = dyn_w * 0.95
        else:
            dyn_w = 1
        
        neighbor_list = []
        radius_search(kd_tree, current_pos, getJumpDistance(current_fuel)**2, 0, neighbor_list)

        for neighbor_node in neighbor_list:
            if neighbor_node.id64 in closed_set:
                continue
            x1, y1, z1 = neighbor_node.pos
            x2, y2, z2 = goal_pos
            dist1 = (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2
            if dist1 - 1125000 > dist2:
                continue 
            fuel_used = getJumpFuelCost(find_coord_distance(neighbor_node.pos, current_pos), current_fuel)

            if neighbor_node.id64 not in open_dict:
                neighbor = A_Node(neighbor_node.pos, current_node.jumps + 1, (1 + dyn_w) * heuristic_calc(neighbor_node.pos, goal_pos), neighbor_node.id64)
                neighbor.parent = current_node
                neighbor.fuel = current_fuel - fuel_used

                heapq.heappush(open_list, (neighbor.f, neighbor.coords, neighbor.fuel, neighbor.id64))
                open_dict[neighbor_node.id64] = neighbor
            elif current_node.jumps + 1 <= open_dict[neighbor_node.id64].jumps and current_fuel - fuel_used >= open_dict[neighbor_node.id64].fuel:
                neighbor = open_dict[neighbor_node.id64]
                neighbor.jumps = current_node.jumps + 1
                neighbor.f = neighbor.jumps + neighbor.h
                neighbor.fuel = current_fuel - fuel_used
                neighbor.parent = current_node
    return []

def main():
    path = find_path()
    prev_jump = None
    i = 1
    print("Jumps Left\t\tFuel Left\t\tFuel used\t\tDistance\t\tid64")
    for jump in path:
        print(f"{len(path) - i}\t\t\t{round(jump[1],2)}\t\t\t{round(prev_jump[1] - jump[1],3) if prev_jump else 0}\t\t\t{round(find_coord_distance(prev_jump[0],jump[0]),3) if prev_jump else 0}\t\t\t{jump[2]}")
        prev_jump = jump
        i += 1

if __name__ == "__main__":
    #cProfile.run('main()', sort='time')
    main()
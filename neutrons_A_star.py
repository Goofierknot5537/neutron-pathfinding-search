# A lot of this was taken from https://www.datacamp.com/tutorial/a-star-algorithm
# The LLM Claude was used in finding optimizations,
# though everything else was typed by hand
import heapq
import kdtree
import math
import cProfile

class A_Node:
    def __init__(self, coords: tuple[float, float, float], jumps: int, h: float, id64: int):
        self.coords = coords
        self.jumps = jumps
        self.h = h
        self.f = jumps + h
        self.parent = None
        self.fuel = None
        self.id64 = id64

def find_coord_distance(point1: tuple[float, float, float], point2: tuple[float, float, float]) -> float:
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def heuristic_calc(coords: tuple[float, float, float], goal: tuple[float, float, float]) -> float:
    dist = find_coord_distance(coords, goal)
    return dist / 554

def reconstruct_path(goal_node: A_Node) -> list:
    path = []
    current = goal_node
    while current != None:
        path.append([(current.coords), current.fuel, current.id64])
        current = current.parent

    return path[::-1]

# From EDSY https://github.com/taleden/EDSY/blob/master/edsy.js
# Stats are manually chosen from my Caspian build
def getJumpFuelCost(dist: float, fuel: float) -> float:
    maxDist = getJumpDistance(fuel)
    return (dist / maxDist)**2.5025 * min(fuel, 6.8)

def getJumpDistance(fuel: float) -> float:
    dist = (min(fuel, 6.8) / 0.011)**(1 / 2.5025) * (7528.04 / (1194.07 + fuel)) + 10.5
    return dist * 6

def find_path():
    print("Starting")
    kd_tree, kd_tree_data = kdtree.make_tree()
    print("Tree made, starting pathfinding")

    # A dynamic weight. This will decrease gradually until it reaches (near) 1.
    # This makes it so A* acts greedily until a certain point, so it can find a semi-optimal path
    # Optimizations left this mostly obsolete, though. I'm looking for the global minium, after all
    dyn_w = 0

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

    x2, y2, z2 = goal_pos

    while open_list:
        _, current_pos, current_fuel, cur_id64 = heapq.heappop(open_list)
        current_node = open_dict[cur_id64]
        open_dict.pop(cur_id64)

        if cur_id64 == goal:
            print("Goal found, getting path")
            return reconstruct_path(current_node)
        
        closed_set.add(current_node.id64)
        x1, y1, z1 = current_pos
        
        curr_goal_dist = (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2

        #dyn_w *= 0.90
        nodes_i = kd_tree.query_ball_point(current_pos, getJumpDistance(current_fuel), workers=4)
        neighbor_list = [kd_tree_data[i] for i in nodes_i]

        # pruning
        neighbor_list_filtered = []
        for neighbor_node in neighbor_list:
            if neighbor_node[1] in closed_set:
                continue
            x1, y1, z1 = neighbor_node[0]
            node_goal_dist = (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2
            if node_goal_dist > curr_goal_dist:
                continue
            neighbor_list_filtered.append(neighbor_node)

        for neighbor_node in neighbor_list_filtered:
            fuel_used = getJumpFuelCost(find_coord_distance(neighbor_node[0], current_pos), current_fuel)
            
            if neighbor_node[1] not in open_dict:
                neighbor = A_Node(neighbor_node[0], current_node.jumps + 1, (1 + dyn_w) * heuristic_calc(neighbor_node[0], goal_pos), neighbor_node[1])
                neighbor.parent = current_node
                neighbor.fuel = current_fuel - fuel_used

                heapq.heappush(open_list, (neighbor.f, neighbor.coords, neighbor.fuel, neighbor.id64))
                open_dict[neighbor_node[1]] = neighbor
            else:
                neighbor_jumps = open_dict[neighbor_node[1]].jumps
                current_jumps = current_node.jumps + 1
                if current_node.jumps < neighbor_jumps or (current_jumps == neighbor_jumps and current_fuel - fuel_used >= open_dict[neighbor_node[1]].fuel):
                    neighbor = open_dict[neighbor_node[1]]
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
    cProfile.run('main()', sort='time')
    #main()
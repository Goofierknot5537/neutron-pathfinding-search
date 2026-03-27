import json
import jsonlines
import math

def main():
    with open("systems_neutron.json", "r") as data_file, jsonlines.open("neutrons_stripped.jsonl", mode="w", compact=True) as output_file:
        for line in data_file:
            if line != '[\n' and line != ']\n':
                line = line.strip()
                system = json.loads(line.strip(','))
                try:
                    n_mainstar = system['mainStar']
                except:
                    n_mainstar = ''
                    exit
                if n_mainstar == "Neutron Star":
                    n_x = system["coords"]["x"]
                    n_y = system["coords"]["y"]
                    n_z = system["coords"]["z"]
                    distance_sol = find_coord_distance(n_x, n_y, n_z, 0, 0, 0)
                    distance_colonia = find_coord_distance(n_x, n_y, n_z, -9530.5, -910.28125, 19808.125)
                    if (distance_sol + distance_colonia) < 25000:
                        id_64 = system['id64']
                        n_system = {"id":id_64,"crds":{"x":n_x,"y":n_y,"z":n_z}}
                        output_file.write(n_system)
                
def find_coord_distance(x1, y1, z1, x2, y2, z2) -> float:
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

main()
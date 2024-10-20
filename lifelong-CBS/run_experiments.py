#!/usr/bin/python
import argparse
import glob
from pathlib import Path
from lifelong import visualize_movement
from visualize import Animation
from single_agent_planner import get_sum_of_cost

SOLVER = "CBS"

HEIGHT =0
WIDTH = 0

def print_mapf_instance(my_map, starts, goals):
    print('Start locations')
    print_locations(my_map, starts)
    print('Goal locations')
    print_locations(my_map, goals)
 
def print_locations(my_map, locations):
    starts_map = [[-1 for _ in range(len(my_map[0]))] for _ in range(len(my_map))]
    for i in range(len(locations)):
        starts_map[locations[i][0]][locations[i][1]] = i
    to_print = ''
    for x in range(len(my_map)):
        for y in range(len(my_map[0])):
            if starts_map[x][y] >= 0:
                to_print += str(starts_map[x][y]) + ' '
            elif my_map[x][y]:
                to_print += '@ '
            else:
                to_print += '. '
        to_print += '\n'
    print(to_print)

def import_mapf_instance(filename):
    f = Path(filename)
    if not f.is_file():
        raise BaseException(filename + " does not exist.")
    f = open(filename, 'r')
    # first line: #rows #columns
    line = f.readline()
    rows, columns = [int(x) for x in line.split(' ')]
    rows = int(rows)
    columns = int(columns)
    HEIGHT = rows
    WIDTH = columns
    # #rows lines with the map
    my_map = []
    for r in range(rows):
        line = f.readline()
        my_map.append([])
        for cell in line:
            if cell == '@':
                my_map[-1].append(1)
            elif cell == '.':
                my_map[-1].append(0)
            elif cell == 'I':
                my_map[-1].append(2)
            elif cell == 'O':
                my_map[-1].append(3)
    # #agents
    line = f.readline()
    num_agents = int(line)
    # #agents lines with the start/goal positions
    goals = []
    for a in range(num_agents):
        line = f.readline()
        arr = [int(x) for x in line.split(' ')]
        goal_agent = []
        goal_agent.append((arr[0], arr[1]))
        goals.append(goal_agent)
    f.close()
    return my_map, goals



def save_paths_to_file(paths, filename):
    with open(filename, 'w') as file:
        max_t = max([len(path) for path in paths])
        for t in range(max_t):
            line = f"{t}:"
            for path in paths:
                if t < len(path):
                    line += f"({path[t][1]},{path[t][0]}),"
                else:
                    line += f"({path[-1][1]},{path[-1][0]}),"
            file.write(line + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs various MAPF algorithms')
    parser.add_argument('--instance', type=str, default=None,
                        help='The name of the instance file(s)')
    parser.add_argument('--batch', action='store_true', default=False,
                        help='Use batch output instead of animation')
    parser.add_argument('--disjoint', action='store_true', default=False,
                        help='Use the disjoint splitting')
    parser.add_argument('--solver', type=str, default=SOLVER,
                        help='The solver to use (one of: {CBS}), defaults to ' + str(SOLVER))

    args = parser.parse_args()

    result_file = open("results.csv", "w", buffering=1)

    for file in sorted(glob.glob(args.instance)):

        print("***Import an instance***")
        my_map, goals = import_mapf_instance(file)
        # TODO: fix this function as per the new format i.e. multiple starts and goals (multi-layered)
        # print_mapf_instance(my_map, starts, goals)

        # if args.solver == "CBS":
        #     print("***Run CBS***")
        #     cbs = CBSSolver(my_map, goals)
        #     paths = cbs.find_solution(args.disjoint)
        # else:
        #     raise RuntimeError("Unknown solver!")

        # cost = get_sum_of_cost(paths)
        # save_paths_to_file(paths, file + '.paths')
        # result_file.write("{},{}\n".format(file, cost))
        visualize_movement(my_map, goals)
        # if not args.batch:
            # print("***Test paths on a simulation***")
            # animation = Animation(args,my_map, goals)
    #         # animation.save("output.mp4", 1.0)
    #         animation.show()
    # result_file.close()

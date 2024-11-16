#!/usr/bin/python
import argparse
import glob
from pathlib import Path
import random
from cbs import CBSSolver
from visualize import Animation
from single_agent_planner import get_sum_of_cost

SOLVER = "CBS"


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

def get_new_goal(layout, rows, column):
    goal = (random.randint(0, rows - 3), random.randint(0, column - 2))
    while layout[goal[0]][goal[1]] == 1:
        goal = (random.randint(1, rows - 3), random.randint(1, column - 2))
    return goal

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
    # #rows lines with the map
    my_map = []
    for r in range(rows):
        line = f.readline()
        my_map.append([])
        for cell in line:
            if cell == '@':
                my_map[-1].append(True)
            elif cell == '.':
                my_map[-1].append(False)
            elif cell == 'I':
                my_map[-1].append('inbound')
            elif cell == 'O':
                my_map[-1].append('outbound')
    # #agents
    line = f.readline()
    inbound_agents = int(line)
    new_line = f.readline()
    outbound_agents = int(new_line)
    # #agents lines with the start/goal positions
    inbound_goals = []
    outbound_goals = []
    for a in range(inbound_agents):
        goal_agent = []
        for i in range(2):
            goal_agent.append(get_new_goal(my_map, rows, columns))
        inbound_goals.append(goal_agent)
    for a in range(outbound_agents):
        goal_agent = []
        for i in range(3):
            goal_agent.append(get_new_goal(my_map, rows, columns))
        outbound_goals.append(goal_agent)
    f.close()
    return my_map, inbound_goals, outbound_goals



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
                        help='The solver to use (one of: {CBS,Independent,Prioritized}), defaults to ' + str(SOLVER))

    args = parser.parse_args()

    result_file = open("results.csv", "w", buffering=1)

    for file in sorted(glob.glob(args.instance)):

        print("***Import an instance***")
        my_map, inbound_agents, outbound_agents = import_mapf_instance(file)
        print(inbound_agents, outbound_agents)
        # TODO: fix this function as per the new format i.e. multiple starts and goals (multi-layered)
        # print_mapf_instance(my_map, starts, goals)

        if args.solver == "CBS":
            print("***Run CBS***")
            cbs = CBSSolver(my_map, inbound_agents, outbound_agents)
            paths = cbs.find_solution(args.disjoint)

        cost = get_sum_of_cost(paths)
        save_paths_to_file(paths, file + '.paths')
        result_file.write("{},{}\n".format(file, cost))

        if not args.batch:
            print("***Test paths on a simulation***")
            animation = Animation(my_map, inbound_agents, outbound_agents, paths)
            # animation.save("output.mp4", 1.0)
            animation.show()
    result_file.close()

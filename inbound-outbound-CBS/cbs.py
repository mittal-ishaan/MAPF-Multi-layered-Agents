import random
import time as timer
import heapq
from single_agent_planner import compute_heuristics, a_star, compute_heuristics_for_complete_map, get_location, get_sum_of_cost

DEBUG = True


def normalize_paths(pathA, pathB):
    """
    given path1 and path2, finds the shortest path and pads it with the last location
    """
    path1 = pathA.copy()
    path2 = pathB.copy()
    shortest, pad = (path1, len(path2) - len(path1)) if len(path1) < len(path2) else (path2, len(path1) - len(path2))
    for _ in range(pad):
        shortest.append(shortest[-1])
    return path1, path2


def detect_collision(pathA, pathB, inbound_stations, outbound_stations):
    ##############################
    # Task 3.1: Return the first collision that occurs between two robot paths (or None if there is no collision)
    #           There are two types of collisions: vertex collision and edge collision.
    #           A vertex collision occurs if both robots occupy the same location at the same timestep
    #           An edge collision occurs if the robots swap their location at the same timestep.
    #           You should use "get_location(path, t)" to get the location of a robot at time t.
    # this function detects if an agent collides with another even after one of the two reached the goal
    path1, path2 = normalize_paths(pathA, pathB)
    ignore_stations = inbound_stations + outbound_stations
    length = len(path1)
    for t in range(length):
        # check for vertex collision
        pos1 = get_location(path1, t)
        pos2 = get_location(path2, t)
        if pos1 == pos2 and pos1 not in ignore_stations:
            # we return the vertex and the timestep causing the collision
            return [pos1], t, 'vertex'
        # check for edge collision (not if we are in the last timestep)
        if t < length - 1:
            next_pos1 = get_location(path1, t + 1)
            next_pos2 = get_location(path2, t + 1)
            if pos1 == next_pos2 and pos2 == next_pos1 and pos1 not in ignore_stations and next_pos1 not in ignore_stations:
                # we return the edge and timestep causing the collision
                return [next_pos2, next_pos1], t + 1, 'edge'
    return None


def detect_collisions(paths, inbound_stations, outbound_stations):
    ##############################
    # Task 3.1: Return a list of first collisions between all robot pairs.
    #           A collision can be represented as dictionary that contains the id of the two robots, the vertex or edge
    #           causing the collision, and the timestep at which the collision occurred.
    #           You should use your detect_collision function to find a collision between two robots.
    collisions = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            coll_data = detect_collision(paths[i], paths[j], inbound_stations, outbound_stations)
            # if coll_data is not None (collision detected)
            if coll_data:
                collisions.append({
                    'a1': i,
                    'a2': j,
                    'loc': coll_data[0],  # vertex or edge
                    'timestep': coll_data[1],  # timestep
                    'type': coll_data[2]
                })
    return collisions


def standard_splitting(collision):
    ##############################
    # Task 3.2: Return a list of (two) constraints to resolve the given collision
    #           Vertex collision: the first constraint prevents the first agent to be at the specified location at the
    #                            specified timestep, and the second constraint prevents the second agent to be at the
    #                            specified location at the specified timestep.
    #           Edge collision: the first constraint prevents the first agent to traverse the specified edge at the
    #                          specified timestep, and the second constraint prevents the second agent to traverse the
    #                          specified edge at the specified timestep
    # in this case, we can ignore final as all the paths are normalized
    constraints = []
    if collision['type'] == 'vertex':
        constraints.append({
            'agent': collision['a1'],
            'loc': collision['loc'],
            'timestep': collision['timestep'],
            'final': False
        })
        constraints.append({
            'agent': collision['a2'],
            'loc': collision['loc'],
            'timestep': collision['timestep'],
            'final': False
        })
    elif collision['type'] == 'edge':
        constraints.append({
            'agent': collision['a1'],
            'loc': collision['loc'],
            'timestep': collision['timestep'],
            'final': False
        })
        constraints.append({
            'agent': collision['a2'],
            # revesred returns an iterator. In python list == iterator returns false, not an error: nasty bug
            'loc': list(reversed(collision['loc'])),
            'timestep': collision['timestep'],
            'final': False
        })
    return constraints


def disjoint_splitting(collision):
    ##############################
    # Task 4.1: Return a list of (two) constraints to resolve the given collision
    #           Vertex collision: the first constraint enforces one agent to be at the specified location at the
    #                            specified timestep, and the second constraint prevents the same agent to be at the
    #                            same location at the timestep.
    #           Edge collision: the first constraint enforces one agent to traverse the specified edge at the
    #                          specified timestep, and the second constraint prevents the same agent to traverse the
    #                          specified edge at the specified timestep
    #           Choose the agent randomly

    pass


class CBSSolver(object):
    """The high-level search of CBS."""

    def __init__(self, my_map, inbound_agents, outbound_agents):
        """my_map   - list of lists specifying obstacle positions
        starts      - [[(x1, y1), (x2, y2)], ...] list of start locations for each agent
        goals       - [[(x1, y1), (x2, y2)], ...] list of goal locations for each agent
        """

        self.start_time = 0
        self.my_map = my_map
        self.inbound_agents = inbound_agents
        self.outbound_agents = outbound_agents
        self.inbound_goals = len(inbound_agents)
        self.outbound_goals = len(outbound_agents)

        self.num_of_generated = 0
        self.num_of_expanded = 0
        self.CPU_time = 0

        self.open_list = []
        self.constraint_counts = {}

        inbound_agents = [self.inbound_agents[i][j] for i in range(self.inbound_goals) for j in range(len(self.inbound_agents[i]))]
        outbound_agents = [self.outbound_agents[i][j] for i in range(self.outbound_goals) for j in range(len(self.outbound_agents[i]))]
        # Find inbound and outbound stations
        self.inbound_stations = [(row, col) for row in range(len(my_map)) for col in range(len(my_map[0])) if my_map[row][col] == 'inbound']
        self.outbound_stations = [(row, col) for row in range(len(my_map)) for col in range(len(my_map[0])) if my_map[row][col] == 'outbound']
        # Compute heuristics for all possible goal locations
        self.heuristics = {}
        self.heuristics = compute_heuristics_for_complete_map(my_map)

    def push_node(self, node):
        heapq.heappush(self.open_list, (len(node['collisions']), node['cost'], self.num_of_generated, node))
        if DEBUG:
            print("Generate node {}".format(self.num_of_generated))
        self.num_of_generated += 1

    def pop_node(self):
        _, _, id, node = heapq.heappop(self.open_list)
        if DEBUG:
            print("Expand node {}".format(id))
            self.num_of_expanded += 1
        return node

    def find_solution(self, disjoint=True):
        """ Finds paths for all agents from their start locations to their goal locations

        disjoint    - use disjoint splitting or not
        """

        self.start_time = timer.time()

        # Generate the root node
        # constraints   - list of constraints
        # paths         - list of paths, one for each agent
        #               [[(x11, y11), (x12, y12), ...], [(x21, y21), (x22, y22), ...], ...]
        # collisions     - list of collisions in paths
        root = {'cost': 0,
                'constraints': [],
                'paths': [],
                'collisions': []}
        # Find initial path for each agent from start to goal
        for i in range(self.inbound_goals):
            final_path = []
            inbound = random.choice(self.inbound_stations)
            path_to_start = a_star(self.my_map, inbound, self.inbound_agents[i][0], self.heuristics[self.inbound_agents[i][0]], i, root['constraints'])
            final_path += path_to_start
            if path_to_start is None:
                raise BaseException('No solutions')
            for j in range(len(self.inbound_agents[i])):
                path = None
                if j == len(self.inbound_agents[i]) - 1:
                    path = a_star(self.my_map, self.inbound_agents[i][j], inbound, self.heuristics[inbound], i, root['constraints'])
                else:
                    path = a_star(self.my_map, self.inbound_agents[i][j], self.inbound_agents[i][j+1], self.heuristics[self.inbound_agents[i][j+1]], i, root['constraints'])
                if path is None:
                    raise BaseException('No solutions')
                final_path += path
            root['paths'].append(final_path)
        for i in range(self.outbound_goals):
            final_path = []
            outbound = random.choice(self.outbound_stations)
            path_to_start = a_star(self.my_map, outbound, self.outbound_agents[i][0], self.heuristics[self.outbound_agents[i][0]], i, root['constraints'])
            final_path += path_to_start
            if path_to_start is None:
                raise BaseException('No solutions')
            for j in range(len(self.outbound_agents[i])):
                path = None
                if j == len(self.outbound_agents[i]) - 1:
                    path = a_star(self.my_map, self.outbound_agents[i][j], outbound, self.heuristics[outbound], i, root['constraints'])
                else:
                    path = a_star(self.my_map, self.outbound_agents[i][j], self.outbound_agents[i][j+1], self.heuristics[self.outbound_agents[i][j+1]], i, root['constraints'])
                if path is None:
                    raise BaseException('No solutions')
                final_path += path
            root['paths'].append(final_path)
        root['cost'] = get_sum_of_cost(root['paths'])
        root['collisions'] = detect_collisions(root['paths'], self.inbound_stations, self.outbound_stations)
        self.push_node(root)

        # Task 3.1: Testing
        if DEBUG:
            print(root['collisions'])

        # Task 3.2: Testing
        if DEBUG:
            for collision in root['collisions']:
                print(standard_splitting(collision))

        ##############################
        # Task 3.3: High-Level Search
        #           Repeat the following as long as the open list is not empty:
        #             1. Get the next node from the open list (you can use self.pop_node())
        #             2. If this node has no collision, return solution
        #             3. Otherwise, choose the first collision and convert to a list of constraints (using your
        #                standard_splitting function). Add a new child node to your open list for each constraint
        #           Ensure to create a copy of any objects that your child nodes might inherit

        while self.open_list:
            p = self.pop_node()
            # if there are no collisions, we found a solution
            if not p['collisions']:
                self.print_results(p)
                return p['paths']
            collision = random.choice(p['collisions'])
            constraints = standard_splitting(collision)
            for c in constraints:
                constraint_key = (c['agent'], tuple(c['loc']), c['timestep'])
                if constraint_key in self.constraint_counts:
                    self.constraint_counts[constraint_key] += 1
                else:
                    self.constraint_counts[constraint_key] = 1
                if self.constraint_counts[constraint_key] >= 3:
                    continue
                q = {'cost': 0,
                     'constraints': p['constraints'] + [c],
                     'paths': p['paths'].copy(),
                     'collisions': []}
                agent = c['agent']
                final_path = []
                if agent < self.inbound_goals:
                    inbound = random.choice(self.inbound_stations)
                    path_to_start = a_star(self.my_map, inbound, self.inbound_agents[agent][0], self.heuristics[self.inbound_agents[agent][0]], agent, q['constraints'])
                    final_path += path_to_start
                    if path_to_start is None:
                        raise BaseException('No solutions')
                    for j in range(len(self.inbound_agents[agent])):
                        path = None
                        if j == len(self.inbound_agents[agent]) - 1:
                            path = a_star(self.my_map, self.inbound_agents[agent][j], inbound, self.heuristics[inbound], agent, q['constraints'])
                        else:
                            path = a_star(self.my_map, self.inbound_agents[agent][j], self.inbound_agents[agent][j+1], self.heuristics[self.inbound_agents[agent][j+1]], agent, q['constraints'])
                        if path is None:
                            raise BaseException('No solutions')
                        final_path += path
                else:
                    outbound = random.choice(self.outbound_stations)
                    path_to_start = a_star(self.my_map, outbound, self.outbound_agents[agent-self.inbound_goals][0], self.heuristics[self.outbound_agents[agent-self.inbound_goals][0]], agent, q['constraints'])
                    final_path += path_to_start
                    if path_to_start is None:
                        raise BaseException('No solutions')
                    for j in range(len(self.outbound_agents[agent-self.inbound_goals])):
                        path = None
                        if j == len(self.outbound_agents[agent-self.inbound_goals]) - 1:
                            path = a_star(self.my_map, self.outbound_agents[agent-self.inbound_goals][j], outbound, self.heuristics[outbound], agent, q['constraints'])
                        else:
                            path = a_star(self.my_map, self.outbound_agents[agent-self.inbound_goals][j], self.outbound_agents[agent-self.inbound_goals][j+1], self.heuristics[self.outbound_agents[agent-self.inbound_goals][j+1]], agent, q['constraints'])
                        if path is None:
                            raise BaseException('No solutions')
                        final_path += path
                if final_path:
                    q['paths'][agent] = final_path
                    q['collisions'] = detect_collisions(q['paths'], self.inbound_stations, self.outbound_stations)
                    q['cost'] = get_sum_of_cost(q['paths'])
                    print(q['collisions'])
                    self.push_node(q)
    
        return None  # No solution found

    def print_results(self, node):
        print("\n Found a solution! \n")
        CPU_time = timer.time() - self.start_time
        print("CPU time (s):    {:.2f}".format(CPU_time))
        print("Sum of costs:    {}".format(get_sum_of_cost(node['paths'])))
        print("Expanded nodes:  {}".format(self.num_of_expanded))
        print("Generated nodes: {}".format(self.num_of_generated))

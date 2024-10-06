import numpy as np
import matplotlib.pyplot as plt
from queue import PriorityQueue
import random

# Parameters
WIDTH = 40  # Width of the warehouse
HEIGHT = 20  # Height of the warehouse
NUM_ROBOTS = 10  # Number of robots
OBSTACLE_RATE = 0.15  # Rate of obstacles in the warehouse

# Define possible moves (up, down, left, right)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# Node class for the A* algorithm
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start to current node
        self.h = 0  # Estimated cost to goal
        self.f = 0  # Total cost

    def __lt__(self, other):
        return self.f < other.f


# A* Pathfinding Algorithm
def a_star(start, goal, obstacles):
    open_list = PriorityQueue()
    closed_list = set()
    start_node = Node(start)
    goal_node = Node(goal)
    open_list.put(start_node)

    while not open_list.empty():
        current_node = open_list.get()
        closed_list.add(current_node.position)

        # If we reached the goal
        if current_node.position == goal_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]  # Return reversed path

        for direction in DIRECTIONS:
            neighbor_pos = (current_node.position[0] + direction[0], current_node.position[1] + direction[1])

            if (0 <= neighbor_pos[0] < HEIGHT and
                    0 <= neighbor_pos[1] < WIDTH and
                    neighbor_pos not in obstacles and
                    neighbor_pos not in closed_list):

                neighbor_node = Node(neighbor_pos, current_node)
                neighbor_node.g = current_node.g + 1
                neighbor_node.h = abs(neighbor_pos[0] - goal_node.position[0]) + abs(
                    neighbor_pos[1] - goal_node.position[1])
                neighbor_node.f = neighbor_node.g + neighbor_node.h

                if all(neighbor_node.f < n.f for n in open_list.queue if n.position == neighbor_pos):
                    open_list.put(neighbor_node)

    return None  # No path found


# Create Warehouse Layout with Obstacles
def create_warehouse():
    layout = np.zeros((HEIGHT, WIDTH), dtype=int)  # 0 for free space

    # Randomly add obstacles
    num_obstacles = int(HEIGHT * WIDTH * OBSTACLE_RATE)
    for _ in range(num_obstacles):
        x = random.randint(1, HEIGHT - 2)
        y = random.randint(1, WIDTH - 2)
        layout[x, y] = 1  # 1 for obstacle

    return layout


# Get a new random goal
def get_new_goal(layout, current_position):
    goal = (random.randint(1, HEIGHT - 2), random.randint(1, WIDTH - 2))
    while layout[goal] == 1 or goal == current_position:
        goal = (random.randint(1, HEIGHT - 2), random.randint(1, WIDTH - 2))
    return goal


# Simulate robot movement
def simulate_robots(layout):
    robots = []
    paths = []

    for _ in range(NUM_ROBOTS):
        start = (random.randint(1, HEIGHT - 2), random.randint(1, WIDTH - 2))
        goal = get_new_goal(layout, start)

        while layout[start] == 1 or layout[goal] == 1 or start == goal:
            start = (random.randint(1, HEIGHT - 2), random.randint(1, HEIGHT - 2))
            goal = get_new_goal(layout, start)

        robots.append((start, goal))
        path = a_star(start, goal, {(x, y) for x in range(HEIGHT) for y in range(WIDTH) if layout[x, y] == 1})
        paths.append(path)

    return robots, paths


# Visualize the robot movement with collision avoidance
def visualize_movement(layout, robots, paths):
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots(figsize=(10, 5))

    robot_colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'brown',
                    'pink']  # Different colors for each robot

    while True:  # Run indefinitely
        ax.clear()  # Clear the previous frame
        ax.imshow(layout, cmap='Greys', origin='upper')  # Update layout for obstacles

        # Create a set to store dynamic obstacles
        dynamic_obstacles = set()

        for i, (start, goal) in enumerate(robots):
            if paths[i]:
                current_position = paths[i].pop(0)  # Get next position in path
                dynamic_obstacles.add(current_position)  # Add current position to dynamic obstacles
                ax.plot(current_position[1], current_position[0], marker='o', color=robot_colors[i],
                        markersize=8)  # Robot position

                # Draw the path taken by the robot
                for pos in paths[i]:
                    ax.plot(pos[1], pos[0], marker='o', color=robot_colors[i], markersize=5, alpha=0.5)

                # Keep robot at goal position once reached
                if len(paths[i]) == 0:
                    ax.plot(goal[1], goal[0], marker='o', color=robot_colors[i], markersize=8)  # Keep at goal position
                    ax.plot(goal[1], goal[0], marker='X', color=robot_colors[i], markersize=10,
                            alpha=0.8)  # Draw goal marker

                    # Assign a new goal
                    new_goal = get_new_goal(layout, current_position)
                    robots[i] = (current_position, new_goal)  # Update robot with new goal
                    new_path = a_star(current_position, new_goal,
                                      {(x, y) for x in range(HEIGHT) for y in range(WIDTH) if
                                       layout[x, y] == 1} | dynamic_obstacles)
                    paths[i] = new_path  # Recalculate the path

        # Collision Detection and Path Recalculation
        for i in range(NUM_ROBOTS):
            if len(paths[i]) > 0:
                next_position = paths[i][0]
                if next_position in dynamic_obstacles:
                    # If next position is occupied, recalculate path
                    new_path = a_star(robots[i][0], robots[i][1],
                                      {(x, y) for x in range(HEIGHT) for y in range(WIDTH) if
                                       layout[x, y] == 1} | dynamic_obstacles)
                    paths[i] = new_path if new_path else []  # Update path if a new one is found

        ax.set_title("Lifelong Warehouse Robot Movement Simulation with Collision Avoidance")
        ax.set_xlabel("Width")
        ax.set_ylabel("Height")
        ax.set_xlim(-0.5, WIDTH - 0.5)  # Set limits to avoid black borders
        ax.set_ylim(HEIGHT - 0.5, -0.5)  # Reverse Y-axis to have (0,0) at the top left
        plt.pause(0.3)  # Pause for 0.3 seconds for the animation effect

    plt.ioff()  # Turn off interactive mode
    plt.show()


# Run the lifelong simulation
layout = create_warehouse()
robots, paths = simulate_robots(layout)
print(paths)
visualize_movement(layout, robots, paths)
import numpy as np
import matplotlib.pyplot as plt
from queue import PriorityQueue
import random
from cbs import CBSSolver

# Parameters
WIDTH = 17  # Width of the warehouse
HEIGHT = 12  # Height of the warehouse

# Get a new random goal
def get_new_goal(layout, goals):
    goal = (random.randint(0, HEIGHT - 3), random.randint(0, WIDTH - 2))
    while layout[goal[0]][goal[1]] == 1 or goal in goals:
        goal = (random.randint(1, HEIGHT - 3), random.randint(1, WIDTH - 2))
    return goal


# Visualize the robot movement with collision avoidance
def visualize_movement(layout, robots: int):
    plt.ion()  # Turn on interactive mode
    HEIGHT = len(layout)
    WIDTH = len(layout[0])
    fig, ax = plt.subplots(figsize=(10, 5))
    goals = []
    for i in range(robots):
        goal = get_new_goal(layout, goals)
        goals.append(goal)
    cbs = CBSSolver(layout, goals)
    paths = cbs.find_solution()
    robot_colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'brown',
                    'pink']  # Different colors for each robot

    while True:  # Run indefinitely
        ax.clear()  # Clear the previous frame
        ax.imshow(layout, cmap='Greys', origin='upper')  # Update layout for obstacles


        for i, goal in enumerate(goals):
            if paths[i]:
                current_position = paths[i][0]  # Get next position in path
                ax.plot(current_position[1], current_position[0], marker='o', color=robot_colors[i],
                        markersize=8)  # Robot position
                ax.plot(goal[1], goal[0], marker='X', color=robot_colors[i], markersize=5,
                        alpha=0.8) 
                # Draw the path taken by the robot
                for pos in paths[i]:
                    ax.plot(pos[1], pos[0], marker='o', color=robot_colors[i], markersize=2, alpha=0.5)
                
            # Keep robot at goal position once reached
                if len(paths[i]) == 1:
                    ax.plot(goal[1], goal[0], marker='X', color=robot_colors[i], markersize=5,
                            alpha=0.8)  # Draw goal marker

                    # Assign a new goal
                    new_goal = get_new_goal(layout, goals)
                    goals[i] = new_goal
                    # print("New goal for robot", i, ":", new_goal)
                    paths = cbs.find_extended_solution(i, current_position, paths)
        # print(paths)
        for i in range(len(paths)):
            paths[i].pop(0)
        ax.set_title("Lifelong Warehouse Robot Movement Simulation with Collision Avoidance")
        ax.set_xlabel("Width")
        ax.set_ylabel("Height")
        ax.set_xlim(-0.5, WIDTH - 0.5)  # Set limits to avoid black borders
        ax.set_ylim(HEIGHT - 0.5, -0.5)  # Reverse Y-axis to have (0,0) at the top left
        plt.pause(0.5)  # Pause for 0.3 seconds for the animation effect

    plt.ioff()  # Turn off interactive mode
    plt.show()

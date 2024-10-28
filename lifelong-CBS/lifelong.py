import numpy as np
import matplotlib.pyplot as plt
from queue import PriorityQueue
import random
from cbs import CBSSolver
import time
import csv

# Parameters
WIDTH = 17  # Width of the warehouse
HEIGHT = 12  # Height of the warehouse
fieldnames = ['robot', 'start', 'goal', 'time_taken', 'cost']

def clear_results():
    with open('results.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

#Write results to a CSV file
import os

def write_results(results):
    file_exists = os.path.isfile('results.csv')
    with open('results.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()  # Write header only if file does not exist
        while len(results) > 0:
            writer.writerow(results.pop(0))

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
    results = []
    for i in range(robots):
        goal = get_new_goal(layout, goals)
        goals.append(goal)
    cbs = CBSSolver(layout, goals)
    clear_results()
    start_time = time.time()
    paths = cbs.find_solution()
    end_time = time.time()
    time_taken = end_time - start_time
    for i, path in enumerate(paths):
        #  for cost 2 minus due to wait added at gaol and 1 more minus due to start position
        results.append({
            'robot': i,
            'start': path[0],
            'goal': goals[i],
            'time_taken': time_taken,
            'cost': len(path) - 3
        })
    write_results(results)
    robot_colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'brown', 'pink']  # Different colors for each robot

    while True:  # Run indefinitely
        ax.clear()  # Clear the previous frame
        ax.imshow(layout, cmap='Greys', origin='upper')  # Update layout for obstacles


        for i, goal in enumerate(goals):
            if paths[i]:
                current_position = paths[i][0]  # Get next position in path
                ax.plot(current_position[1], current_position[0], marker='o', color=robot_colors[i], markersize=8)  # Robot position
                ax.plot(goal[1], goal[0], marker='X', color=robot_colors[i], markersize=5, alpha=0.8) 
                # Draw the path taken by the robot
                for pos in paths[i]:
                    ax.plot(pos[1], pos[0], marker='o', color=robot_colors[i], markersize=2, alpha=0.5)
                
                # Keep robot at goal position once reached
                if len(paths[i]) == 1:
                    ax.plot(goal[1], goal[0], marker='X', color=robot_colors[i], markersize=5, alpha=0.8)  # Draw goal marker

                    # Assign a new goal
                    new_goal = get_new_goal(layout, goals)
                    goals[i] = new_goal

                    # Measure the time taken for path calculation
                    start_time = time.time()
                    paths = cbs.find_extended_solution(i, current_position, paths)
                    end_time = time.time()
                    time_taken = end_time - start_time

                    # Store the result
                    results.append({
                        'robot': i,
                        'start': current_position,
                        'goal': new_goal,
                        'time_taken': time_taken,
                        'cost': len(paths[i]) - 3
                    })

        for i in range(len(paths)):
            if paths[i]:
                paths[i].pop(0)

        ax.set_title("Lifelong Warehouse Robot Movement Simulation with Collision Avoidance")
        ax.set_xlabel("Width")
        ax.set_ylabel("Height")
        ax.set_xlim(-0.5, WIDTH - 0.5)  # Set limits to avoid black borders
        ax.set_ylim(HEIGHT - 0.5, -0.5)  # Reverse Y-axis to have (0,0) at the top left
        plt.pause(0.5)  # Pause for 0.5 seconds for the animation effect

        write_results(results)
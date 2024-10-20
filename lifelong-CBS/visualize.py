#!/usr/bin/env python3
import random
from matplotlib.patches import Circle, Rectangle
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
import matplotlib.patheffects as PathEffects
from cbs import CBSSolver
import matplotlib
matplotlib.use('TkAgg')

Colors = ['#3498db', '#f1c40f', '#8e44ad', '#e67e22', '#e74c3c', '#1abc9c', '#2ecc71', '#e84393', '#2c3e50']

HEIGHT = 0
WIDTH = 0


def convert_normal_index_to_visulize_index(index):
    return (index[1], HEIGHT - index[0] - 1)

def convert_visulize_index_to_normal_index(index):
    return (HEIGHT - index[1] - 1, index[0])

def get_new_goal(layout, current):
    goal = (random.randint(0, HEIGHT - 2), random.randint(0, WIDTH - 2))
    while layout[goal[1]][HEIGHT - goal[0] - 1] != 'False':
        goal = (random.randint(0, HEIGHT - 2), random.randint(0, WIDTH - 2))
    return convert_normal_index_to_visulize_index(goal)

class Animation:
    def __init__(self, args, my_map, goals):
        global HEIGHT, WIDTH
        HEIGHT = len(my_map)
        WIDTH = len(my_map[0])
        self.cbs = CBSSolver(my_map, goals)
        paths = self.cbs.find_solution(args.disjoint)
        self.normal_paths = paths
        self.my_map = np.flip(np.transpose(my_map), 1)
        print(self.my_map)
        self.agent_length = []
        # self.my_map = my_map
        self.starts = []
        # for start in starts:
        #     st = []
        #     for i in range(len(start)):
        #         st.append((start[i][1], len(self.my_map[0]) - 1 - start[i][0]))
        #     self.starts.append(st)
        self.goals = []
        for goal in goals:
            gl = []
            for i in range(len(goal)):
                gl.append((goal[i][1], len(self.my_map[0]) - 1 - goal[i][0]))
            self.goals.append(gl)
        self.paths = []
        if paths:   
            for path in paths:
                self.paths.append([])
                for loc in path:
                    self.paths[-1].append((loc[1], len(self.my_map[0]) - 1 - loc[0]))

        aspect = len(self.my_map) / len(self.my_map[0])

        # Set figure with enhanced visual properties
        self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4), dpi=100)
        self.ax = self.fig.add_subplot(111, aspect='equal')
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        # Dark background with gridlines for contrast
        self.ax.set_facecolor('#2c3e50')
        self.ax.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.2)

        # Patches and artist lists
        self.patches = []
        self.artists = []
        self.agents = dict()
        self.agent_names = dict()

        # Create grid boundaries
        x_min, y_min = -0.5, -0.5
        x_max, y_max = len(self.my_map) - 0.5, len(self.my_map[0]) - 0.5
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)

        # self.patches.append(Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, facecolor='none', edgecolor='gray'))
        # Draw grid with slightly darker cells for obstacles
        for i in range(len(self.my_map)):
            for j in range(len(self.my_map[0])):
                if self.my_map[i][j] == 'True':
                    self.patches.append(Rectangle((i - 0.5, j - 0.5), 1, 1, facecolor='#34495e', edgecolor='#34495e'))
                if self.my_map[i][j] == 'inbound':
                    self.patches.append(Rectangle((i - 0.5, j - 0.5), 1, 1, facecolor='#27ae60', edgecolor='#1e8449'))
                if self.my_map[i][j] == 'outbound':
                    self.patches.append(Rectangle((i - 0.5, j - 0.5), 1, 1, facecolor='#e67e22', edgecolor='#d35400'))

        # Draw agents and their goals
        self.T = 0
        for i, goal in enumerate(self.goals):
            for j in range(len(goal)):
                self.patches.append(Rectangle((goal[j][0] - 0.25, goal[j][1] - 0.25), 0.5, 0.5, facecolor=Colors[i % len(Colors)],
                                              edgecolor='black', alpha=0.3))

        for i in range(len(self.paths)):
            name = str(i)
            # for j in range(len(self.starts[i])):
            self.agents[i] = Circle((0, 0), 0.25, facecolor=Colors[i % len(Colors)], edgecolor='#ecf0f1', lw=2)
            self.agents[i].original_face_color = Colors[i % len(Colors)]
            self.patches.append(self.agents[i])

            # Add agent number text with shadow for readability
            text = self.ax.text(0, 0 + 0.25, name, fontsize=12, color='white')
            text.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='black')])
            self.agent_names[i] = text
            self.artists.append(self.agent_names[i])
            self.T = max(self.T, len(paths[i]) - 1)

        # Animation function to handle smooth movements
        self.animation = animation.FuncAnimation(self.fig, self.animate_func, init_func=self.init_func,
                                                 frames=int(self.T + 1) * 10, interval=100, blit=True)

    def save(self, file_name, speed):
        self.animation.save(
            file_name,
            fps=10 * speed,
            dpi=200,
            savefig_kwargs={"pad_inches": 0, "bbox_inches": "tight"}
        )

    @staticmethod
    def show():
        plt.show()

    def init_func(self):
        for p in self.patches:
            self.ax.add_patch(p)
        for a in self.artists:
            self.ax.add_artist(a)
        return self.patches + self.artists

    def animate_func(self, t):
        for k in range(len(self.paths)):
            time = int(t / 10)
            if time >= len(self.paths[k]):
                self.goals[k].pop(0)
                goal = get_new_goal(self.my_map, self.paths[k][-1])
                self.goals[k].append(goal)
                self.normal_paths = self.cbs.find_extended_solution(k, convert_visulize_index_to_normal_index(goal), self.normal_paths, int(t/10))
                self.patches.pop(0)
                self.patches.append(Rectangle((goal[0] - 0.25, goal[1] - 0.25), 0.5, 0.5, facecolor=Colors[k % len(Colors)],
                                              edgecolor='black', alpha=0.3))
                self.paths = []
                if self.normal_paths:   
                    for path in self.normal_paths:
                        self.paths.append([])
                        for loc in path:
                            self.paths[-1].append((loc[1], len(self.my_map[0]) - 1 - loc[0]))
                self.T = max(self.T, len(self.paths[k]) - 1)
            pos = self.get_state(t / 10, self.paths[k])
            self.agents[k].center = (pos[0], pos[1])
            self.agent_names[k].set_position((pos[0], pos[1] + 0.5))

        # Reset colors to avoid lingering collision indication
        for _, agent in self.agents.items():
            agent.set_facecolor(agent.original_face_color)

        # Detect and highlight collisions
        agents_array = [agent for _, agent in self.agents.items()]
        for i in range(0, len(agents_array)):
            for j in range(i + 1, len(agents_array)):
                d1 = agents_array[i]
                d2 = agents_array[j]
                pos1 = np.array(d1.center)
                pos2 = np.array(d2.center)
                if np.linalg.norm(pos1 - pos2) < 0.5:  # Collision threshold
                    d1.set_facecolor('#e74c3c')
                    d2.set_facecolor('#e74c3c')

        return self.patches + self.artists

    @staticmethod
    def get_state(t, path):
        if int(t) <= 0:
            return np.array(path[0])
        elif int(t) >= len(path):
            return np.array(path[-1])
        else:
            pos_last = np.array(path[int(t) - 1])
            pos_next = np.array(path[int(t)])
            pos = (pos_next - pos_last) * (t - int(t)) + pos_last
            return pos

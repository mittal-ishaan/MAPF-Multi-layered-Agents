import re

def convert_paths(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    agent_paths = {}

    for line in lines:
        match = re.match(r'Agent (\d+):(.*)', line.strip())
        if match:
            agent_number = int(match.group(1))
            path_str = match.group(2)

            coordinates = re.findall(r'\((\d+),(\d+)\)', path_str)
            original_coordinates = [(int(y), int(x)) for x, y in coordinates]
            agent_paths[agent_number] = original_coordinates

    max_length = max(len(path) for path in agent_paths.values())

    with open(output_file, 'w') as file:
        for t in range(max_length):
            time_step_coords = []
            for agent, path in agent_paths.items():
                if t < len(path):
                    time_step_coords.append(f'({path[t][0]},{path[t][1]}),')
                else:
                    time_step_coords.append(f'({path[-1][0]},{path[-1][1]}),')
            file.write(f'{t}:{"".join(time_step_coords)}\n')

# Example usage
convert_paths('paths.txt', 'final.txt')

import re

def convert_paths(input_file, output_file):
    # Read the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Prepare a dictionary to store paths for each agent
    agent_paths = {}

    # Process each line from the input file
    for line in lines:
        # Extract agent number and path from the line
        match = re.match(r'Agent (\d+):(.*)', line.strip())
        if match:
            agent_number = int(match.group(1))
            path_str = match.group(2)

            # Split the path into coordinates and reverse x and y
            coordinates = re.findall(r'\((\d+),(\d+)\)', path_str)
            reversed_coordinates = [(int(y), int(x)) for x, y in coordinates]
            agent_paths[agent_number] = reversed_coordinates

    # Find the maximum path length to determine the time steps
    max_length = max(len(path) for path in agent_paths.values())

    # Prepare to write to the output file
    with open(output_file, 'w') as file:
        # Write paths for each time step
        for t in range(max_length):
            time_step_coords = []
            for agent, path in agent_paths.items():
                if t < len(path):
                    time_step_coords.append(f'({path[t][0]},{path[t][1]})')
                else:
                    # If no more coordinates, use the last known position
                    time_step_coords.append(f'({path[-1][0]},{path[-1][1]})')
            # Write the time step line
            file.write(f'{t}: {",".join(time_step_coords)}\n')

# Example usage
convert_paths('paths.txt', 'final.txt')

input_file = 'output.txt'
output_file = 'final.txt'

with open(input_file, 'r') as file:
    lines = file.readlines()

with open(output_file, 'w') as file:
    for line in lines:
        time_step, coords = line.split(':')
        coords = coords.strip()
        file.write(f"{time_step}:{coords}\n")

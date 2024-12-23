# MAPF-Multi-layered-Agents
This repository focuses on Multi-Agent Path Finding (MAPF) in multi-layered environments, providing implementations for various algorithms and visualization tools.

## Repository Structure

- **lifelong/**: Contains implementations for lifelong MAPF scenarios where agents are continuously assigned new tasks.
- **[Other folders]**: [Brief description of other folders, if applicable.]
- **visualizer/**: Includes code for visualizing agent paths and interactions within the environment.

## Features

- **Multi-Layer Robots Coordination**: Efficient pathfinding and conflict-free navigation for robots operating across multiple layers in complex warehouse environments.
- **Lifelong MAPF Algorithms**: Strategies for dynamic task allocation and conflict-free pathfinding in ongoing operations.
- **Visualization Tools**: Scripts to render agent movements and interactions, aiding in analysis and debugging.

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mittal-ishaan/MAPF-Multi-layered-Agents.git
   
2. **Navigate to the Project Directory**
  ```bash
  cd MAPF-Multi-layered-Agents
   ```

3. Navigate to the desired environment or algorithm folder:
   Running lifelong MAPF:
   ```bash
   cd lifelong-CBS
   ```

4. **Run the desired script**:
   ```bash
   python3 run_experiments.py --instance instances/test_51.txt
   ```

## Development Team
1. Ishaan Mittal
2. Purav Biyani
3. Dhananjay Singh
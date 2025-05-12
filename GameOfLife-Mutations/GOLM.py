"""
Game of Life with Mutations

This script simulates a variation of Conway's Game of Life, 
a cellular automaton, with added complexity of mutations. 
It operates on a grid where each cell can be in several states: 
alive (1), or alive with one of four types of mutations (2 - blue, 3 - red, 4 - green, 5 - yellow).

Grid Size:
- WIDTH: Width of the grid
- HEIGHT: Height of the grid

Grid History:
- Stores the last 10 states of the grid for analysis.

Generations:
- The simulation runs through a user-defined number of generations.

Mutation Probabilities:
- Each type of mutation (blue, green, yellow, red) has a specific probability of occurring.

Main Functionality:
- The script simulates cellular interactions based on Conway's Game of Life rules, 
  along with additional rules for mutations.
- Each cell interacts with its eight neighbors (horizontal, vertical, diagonal).
- Alive cells and mutated cells follow specific rules to stay alive, die, or mutate.
- New cells can spawn with or without mutations based on certain conditions.

Counters:
- The script tracks both the current and total counts for alive cells and each type of mutation.

Unique Patterns:
- The script identifies and stores unique patterns that emerge during the simulation.

Pattern Lifespans:
- Lifespans of each identified pattern are tracked.

Output:
- The script prints the grid and statistics for each generation.
- At the end of the simulation, it can export identified patterns to a file.

Usage:
- Run the script and enter the maximum number of generations for the simulation.
- Observe the evolution of the grid and mutation spread.
- At the end, choose whether to export the unique patterns identified.

"""

# Script initialization and imports
import random
import time
import os
from collections import deque

# Initialize grid and simulation parameters
WIDTH, HEIGHT = 50, 27
grid = [[random.randint(0, 1) for _ in range(WIDTH)] for _ in range(HEIGHT)]
grid_history = deque(maxlen=10)
generation = 0
total_alive = 0
total_mutations = 0
total_blue_mutations = 0
total_red_mutations = 0
total_green_mutations = 0
total_yellow_mutations = 0
total_counts = (
    total_alive,
    total_mutations,
    total_blue_mutations,
    total_red_mutations,
    total_green_mutations,
    total_yellow_mutations,
)
pattern_lifespans = {}
unique_patterns = set()
neighbor_offsets = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]
b_mutation_probability_denominator = 64
g_mutation_probability_denominator = 64
y_mutation_probability_denominator = 64
r_mutation_probability_denominator = 64
max_generations = int(
    input(
        "Enter the \033[91mmaximum\033[0m number of generations for the simulation to run:"
    )
)
simulation_over = False


# Count the number of cells of a specific type in the grid.
def count_cells(grid, cell_type):
    return sum(cell == cell_type for row in grid for cell in row)


# Find the root of the set in the Union-Find algorithm.
def find(parent, i):
    if parent[i] != i:
        parent[i] = find(parent, parent[i])
    return parent[i]


# Perform the 'union' operation in the Union-Find algorithm.
def union(parent, rank, x, y):
    xroot = find(parent, x)
    yroot = find(parent, y)
    if rank[xroot] < rank[yroot]:
        parent[xroot] = yroot
    elif rank[xroot] > rank[yroot]:
        parent[yroot] = xroot
    else:
        parent[yroot] = xroot
        rank[xroot] += 1


# Calculate the counts of live cells and different types of mutations in the current grid.
def calculate_counts(grid):
    live_cells = count_cells(grid, 1)
    blue_mutations = count_cells(grid, 2)
    red_mutations = count_cells(grid, 3)
    green_mutations = count_cells(grid, 4)
    yellow_mutations = count_cells(grid, 5)
    total_mutations = (
        blue_mutations + red_mutations + green_mutations + yellow_mutations
    )
    total_live_cells = live_cells + total_mutations
    return (
        total_live_cells,
        total_mutations,
        blue_mutations,
        red_mutations,
        green_mutations,
        yellow_mutations,
    )


# Print the current state of the grid along with generation and count statistics.
def print_grid(grid, generation, counts):
    (
        total_live_cells,
        total_mutations,
        blue_mutations,
        red_mutations,
        green_mutations,
        yellow_mutations,
    ) = counts
    os.system("cls" if os.name == "nt" else "clear")
    stats = (
        f"Generation: {generation}\n"
        + "\033[95m-\033[0m" * 15
        + "\nCurrent Stats:\n"
        + f"Alive: {total_live_cells}\nMutations: {total_mutations}\n"
        + f"Blue: {blue_mutations}\nRed: {red_mutations}\nGreen: {green_mutations}\nYellow: {yellow_mutations}\n"
        + "\033[95m-\033[0m" * 15
        + "\nHistoric Stats:\n"
        + f"Total: {total_alive}\nMutations: {total_mutations}\n"
        + f"Total Blue: {total_blue_mutations}\nTotal Red: {total_red_mutations}\nTotal Green: {total_green_mutations}\nTotal Yellow: {total_yellow_mutations}"
    )
    stats_lines = stats.split("\n")
    for y, row in enumerate(grid):
        row_str = (
            "\033[96m|\033[0m"
            + "".join(
                "* "
                if cell == 1
                else "\033[94m*\033[0m "
                if cell == 2
                else "\033[91m*\033[0m "
                if cell == 3
                else "\033[92m*\033[0m "
                if cell == 4
                else "\033[93m*\033[0m "
                if cell == 5
                else "  "
                for cell in row
            )
            + "\033[96m|\033[0m "
        )
        if y < len(stats_lines):
            row_str += " " * (52 - WIDTH * 2) + stats_lines[y]
        print(row_str)


# Update and return the total counts of live cells and mutations over time.
def update_totals(grid, counts, total_counts):
    (
        total_alive,
        total_mutations,
        total_blue_mutations,
        total_red_mutations,
        total_green_mutations,
        total_yellow_mutations,
    ) = total_counts
    (
        live_cells,
        mutations,
        blue_mutations,
        red_mutations,
        green_mutations,
        yellow_mutations,
    ) = counts
    total_alive += live_cells
    total_mutations += mutations
    total_blue_mutations += blue_mutations
    total_red_mutations += red_mutations
    total_green_mutations += green_mutations
    total_yellow_mutations += yellow_mutations
    return (
        total_alive,
        total_mutations,
        total_blue_mutations,
        total_red_mutations,
        total_green_mutations,
        total_yellow_mutations,
    )


# Get the count of neighbors for a cell at a specific position in the grid.
def get_neighbor_count(grid, x, y):
    count = 0
    for dx, dy in neighbor_offsets:
        nx, ny = x + dx, y + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
            count += grid[ny][nx] in [1, 2, 3, 4, 5]
    return count


# Check if a cell at a specific position has a mutated neighbor.
def has_mutated_neighbor(grid, x, y):
    for dx, dy in neighbor_offsets:
        nx, ny = x + dx, y + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
            if grid[ny][nx] in [2, 3, 4, 5]:
                return True
    return False


# Identify and return sets of connected live cells in the grid.
def get_connected_live_cells(grid):
    parent = {i: i for i in range(WIDTH * HEIGHT)}
    rank = [0] * (WIDTH * HEIGHT)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] == 1:
                for nx, ny in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and grid[ny][nx] == 1:
                        union(parent, rank, y * WIDTH + x, ny * WIDTH + nx)
    patterns = {}
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] == 1:
                root = find(parent, y * WIDTH + x)
                if root not in patterns:
                    patterns[root] = set()
                patterns[root].add((x, y))
    return [frozenset(pattern) for pattern in patterns.values()]


# Update and return the lifespans of identified patterns in the grid.
def update_pattern_lifespans(current_patterns, pattern_lifespans):
    new_lifespans = {}
    for pattern in current_patterns:
        if pattern in pattern_lifespans:
            new_lifespans[pattern] = pattern_lifespans[pattern] + 1
        else:
            new_lifespans[pattern] = 1
    return new_lifespans


# Update the grid for the next generation based on the current state and predefined rules.
def update_grid(grid, history, pattern_lifespans):
    new_grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            cell_value = grid[y][x]
            neighbors = get_neighbor_count(grid, x, y)
            if cell_value == 1:
                new_grid[y][x] = 1 if neighbors in [2, 3] else 0
            elif cell_value == 2:
                new_grid[y][x] = 2 if neighbors in [3, 4] else 0
            elif cell_value == 4:
                new_grid[y][x] = 4 if neighbors in [4, 5] else 0
            elif cell_value == 5:
                new_grid[y][x] = 5 if neighbors in [5, 6] else 0
            elif cell_value == 0 and neighbors == 3:
                if random.choice([True, False]):
                    new_grid[y][x] = 1
                else:
                    new_grid[y][x] = (
                        2
                        if has_mutated_neighbor(grid, x, y)
                        or random.randint(1, b_mutation_probability_denominator) == 1
                        else 3
                        if has_mutated_neighbor(grid, x, y)
                        or random.randint(1, r_mutation_probability_denominator) == 1
                        else 4
                        if has_mutated_neighbor(grid, x, y)
                        or random.randint(1, g_mutation_probability_denominator) == 1
                        else 5
                        if has_mutated_neighbor(grid, x, y)
                        or random.randint(1, y_mutation_probability_denominator) == 1
                        else 1
                    )
    current_patterns = get_connected_live_cells(grid)
    pattern_lifespans = update_pattern_lifespans(current_patterns, pattern_lifespans)
    for pattern, lifespan in pattern_lifespans.items():
        if lifespan >= 10:
            valid_spawn_points = set()
            for x, y in pattern:
                for nx in range(x - 1, x + 2):
                    for ny in range(y - 1, y + 2):
                        if (
                            0 <= nx < WIDTH
                            and 0 <= ny < HEIGHT
                            and grid[ny][nx] == 0
                            and (nx, ny) not in pattern
                        ):
                            valid_spawn_points.add((nx, ny))
            if (
                valid_spawn_points
                and random.randint(1, r_mutation_probability_denominator) == 1
            ):
                rx, ry = random.choice(list(valid_spawn_points))
                new_grid[ry][rx] = 3
    return new_grid


# Normalize a pattern by adjusting its position relative to the grid.
def get_normalized_pattern(pattern):
    if not pattern:
        return frozenset()
    min_x = min(x for x, y in pattern)
    min_y = min(y for x, y in pattern)
    normalized_pattern = frozenset((x - min_x, y - min_y) for x, y in pattern)
    return normalized_pattern


# Export uniquely identified patterns to a file.
def export_patterns(patterns, filename="patterns.txt"):
    with open(filename, "w") as file:
        for pattern in patterns:
            live_cell_count = len(pattern)
            max_x = max((pt[0] for pt in pattern), default=0)
            max_y = max((pt[1] for pt in pattern), default=0)
            pattern_width = max_x + 2
            pattern_output = (
                f"Cell Count: {live_cell_count}\n" + "-" * pattern_width + "\n"
            )
            for y in range(max_y + 1):
                line = " "
                for x in range(max_x + 1):
                    line += "*" if (x, y) in pattern else " "
                line += " \n"
                pattern_output += line
            pattern_output += "-" * pattern_width + "\n\n"
            file.write(pattern_output)


# Main simulation loop
while generation < max_generations and not simulation_over:
    counts = calculate_counts(grid)
    total_counts = update_totals(grid, counts, total_counts)
    (
        total_alive,
        total_mutations,
        total_blue_mutations,
        total_red_mutations,
        total_green_mutations,
        total_yellow_mutations,
    ) = total_counts
    print_grid(grid, generation, counts)
    current_patterns = get_connected_live_cells(grid)
    for pattern in current_patterns:
        normalized_pattern = get_normalized_pattern(pattern)
        unique_patterns.add(normalized_pattern)
    grid = update_grid(grid, grid_history, pattern_lifespans)
    grid_history.append([row[:] for row in grid])
    pattern_lifespans = update_pattern_lifespans(current_patterns, pattern_lifespans)
    generation += 1
    time.sleep(0.1)

    # Check and end simulation if certain conditions are met
    if not any(cell in [1, 2, 3, 4, 5] for row in grid for cell in row):
        simulation_over = True

# End of simulation
print("\n\033[93mSimulation Over\033[0m")
user_input = input("Do you want to print unique patterns? (yes/no): ")
if user_input.lower() in ["yes", "y"]:
    export_patterns(unique_patterns)

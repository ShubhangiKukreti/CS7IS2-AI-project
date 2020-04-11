import math
import random
import tkinter as tk
import Functions
from GridWorld import GridWorld

from RunAStar import main_for_genetic


# Random Path Generation Function. This take input of gridworld and the key node to start the randomness
def generate_random_route(grid_world, key):
    graph = grid_world.graph
    adjacent_nodes = graph.adjacency_map[key]
    x = int(key.split(',')[0])
    y = int(key.split(',')[1])
    if x == grid_world.end_x and y == grid_world.end_y:
        grid_world.route.append((x, y))
        grid_world.final_route_genetic.append((x, y))
        return -1
    grid_world.is_visited[x][y] = 1
    grid_world.route.append((x, y))
    random.shuffle(adjacent_nodes)
    for l in adjacent_nodes:
        if grid_world.is_visited[l[0]][l[1]] == 0:
            ret_val = generate_random_route(grid_world, str(l[0]) + "," + str(l[1]))
            if ret_val == -1:
                grid_world.final_route_genetic.append((l[0], l[1]))
                return -1


# Crossover functions to generate hybrid paths
def crossover2(population):
    return_list = []
    random.shuffle(population)
    mid = int(len(population) / 2)
    list1 = population[:mid]
    list2 = population[mid:]
    for i in range(min(len(list1), len(list2))):
        path1 = list1[i]
        path2 = list2[i]
        common_nodes = []
        for node in path1:
            if node in path2:
                common_nodes.append(node)
        if len(common_nodes) > 0:
            random_common_node = random.choice(common_nodes)
            index1 = path1.index(random_common_node)
            index2 = path2.index(random_common_node)
            child1 = path1[:index1]
            child1.extend(path2[index2:])
            child2 = path2[:index2]
            child2.extend(path1[index1:])
            return_list.append(child1)
            return_list.append(child2)
    return_list.extend(population)
    return return_list


# Crossover functions to generate hybrid paths
def crossover(population):
    return_list = []
    random.shuffle(population)
    mid = int(len(population) / 2)
    list1 = population[:mid]
    list2 = population[mid:]
    for i in range(min(len(list1), len(list2))):
        path1 = list1[i]
        path2 = list2[i]
        common_nodes = []
        for node in path1:
            if node in path2:
                common_nodes.append(node)
        if len(common_nodes) > 0:
            random_common_node = random.choice(common_nodes)
            index1 = path1.index(random_common_node)
            index2 = path2.index(random_common_node)
            subpart1 = path1[:index1]
            subpart2 = path2[:index2]
            subpart3 = path1[index1:]
            subpart4 = path2[index2:]
            if len(subpart1) < len(subpart2):
                child1 = subpart1
            else:
                child1 = subpart2
            if len(subpart3) < len(subpart4):
                child1.extend(subpart3)
            else:
                child1.extend(subpart4)
            return_list.append(child1)
    return_list.extend(population)
    return return_list


# Used by mutation function to remove duplicate paths
def remove_duplicates(path):
    reverse_path = path[::-1]
    duplicate = None
    for p in path:
        count = path.count(p)
        if count > 1:
            duplicate = p
    indices = [i for i, x in enumerate(path) if x == duplicate]
    ret_path = path[:indices[0]]
    ret_path = path[indices[-1]:]
    return ret_path


# Mutation function to mutate paths generated by cross over
def mutation2(grid_world, population):
    mutated_list = []
    for i in range(len(population)):
        mutated_path = []
        path1 = population[i]
        # print(path1)
        random_nodes = random.sample(path1, 2)
        # print(random_nodes)
        index1 = path1.index(random_nodes[0])
        index2 = path1.index(random_nodes[1])
        if index1 < index2:
            child1 = path1[:index1]
            rand_path = grid_world.get_random_path(random_nodes[1], random_nodes[0])
            child1.extend(rand_path)
            child2 = path1[index2:]
            child1.extend(child2)
            mutated_path.extend(child1)
        if index1 > index2:
            child1 = path1[:index2]
            rand_path = grid_world.get_random_path(random_nodes[0], random_nodes[1])
            child1.extend(rand_path)
            child2 = path1[index1:]
            child1.extend(child2)
            mutated_path.extend(child1)
        # print(mutated_path)
        # print()
        mutated_path = remove_duplicates(mutated_path[:])
        mutated_list.append(mutated_path)
    # print(len(mutated_list))
    return mutated_list


# Mutation function to mutate paths generated by cross over
def mutation(grid_world, population):
    count = len(population)
    mutation_count = 0.3 * count
    sample = random.sample(population, int(mutation_count))
    for list1 in sample:
        random_node = random.choice(list1)
        mutated1 = grid_world.get_random_path((grid_world.start_x, grid_world.start_y), random_node)
        mutated2 = grid_world.get_random_path(random_node, (grid_world.end_x, grid_world.end_y))
        mutated1.append((grid_world.start_x, grid_world.start_y))
        mutated1 = mutated1[::-1]
        mutated1 = mutated1[:-1]
        mutated2 = mutated2[::-1]
        mutated2 = mutated2[:-1]
        mutated1.extend(mutated2)
        population.append(mutated1)
    return population


# Evaluate the generated paths
def evaluation_function(grid_world, route):
    return len(route)


# Population reduction
def reduce_population(population, starting_population_count):
    ret_list = []
    freq = {}
    unique_population = set()
    for path in population:
        unique_population.add(tuple(path))
    population = list(unique_population)
    for i in range(len(population)):
        freq[i] = len(population[i])
    for k, v in sorted(freq.items(), key=lambda f: f[1]):
        ret_list.append(list(population[k]))
    ret_list = ret_list[:starting_population_count]
    return ret_list


# Start the Genetic Algorithm with static population
def genetic_iterations(grid_world, a_star_length):
    starting_population_count = 50
    population = []
    for i in range(starting_population_count):
        grid_world.route = []
        grid_world.final_route_genetic = []
        grid_world.is_visited = [[0] * grid_world.m for temp in range(grid_world.n)]
        generate_random_route(grid_world, grid_world.start_key)
        grid_world.final_route_genetic.append((grid_world.start_x, grid_world.start_y))
        grid_world.final_route_genetic = grid_world.final_route_genetic[::-1]
        population.append(grid_world.final_route_genetic[:-1])
        if len(grid_world.final_route_genetic[:-1]) == 0:
            # print("No possible route")
            return -1

    grid_world.is_visited = [[0] * grid_world.m for temp in range(grid_world.n)]
    best_path = []
    best_score = math.inf
    grid_world.final_route_genetic = []
    # for i in range(100):  # iterations
    i = 0
    list_of_best_lengths = []
    while True:
        # call Crossover path function
        population = crossover(population)
        # Mutate the paths
        population = mutation(grid_world, population)
        # call population reduction fitness function
        population = reduce_population(population, starting_population_count)
        avg = 0
        for path in population:
            avg += len(path)
        if len(population[0]) < best_score:
            best_score = len(population[0])
            best_path = population[0]
        # print(i, '\t', len(population[0]))
        list_of_best_lengths.append(len(population[0]))
        # if len(population[0]) == a_star_length:
        #     # print('Genetic:', best_score, best_path)
        #     grid_world.final_route_genetic = best_path
        #     return i
        if i >= 50:
            if list_of_best_lengths[i] == list_of_best_lengths[i - 50]:
                grid_world.final_route_genetic = best_path
                return i - 50
        i += 1
    # print('Genetic:', best_score, best_path)
    # grid_world.final_route_genetic = best_path


# Run Genetic Algorithm
def run_genetic(grid_world, a_star_length):
    num_of_iterations_to_converge = genetic_iterations(grid_world, a_star_length)
    # print(grid_world.final_route_genetic)
    return num_of_iterations_to_converge


# Creating Gridworld Environment
grid_size = 2
while grid_size <= 40:
    numeerator = 0
    denomenator = 0
    m = grid_size
    n = grid_size
    loop_count = 0
    sample_size = 10
    while loop_count < sample_size:
        grid_world = GridWorld(m, n)

        # Creating grid ui
        # Functions.create_obstacles_from_hex(grid_world)
        Functions.create_random_obstacles(grid_world, 0.205)
        # Functions.create_fixed_obstacles(grid_world, 6)
        grid_world.scan_grid_and_generate_graph()
        # grid_world.print_graph()

        # Run Genetic Algorithm
        a_star_length = main_for_genetic(grid_world)
        if a_star_length == 0:
            continue
        # print('A-STAR length', a_star_length)
        num_of_iterations_to_converge = run_genetic(grid_world, a_star_length)
        if num_of_iterations_to_converge >= 0:
            numeerator += num_of_iterations_to_converge
            denomenator += 1
        # grid_world.create_grid_ui(grid_world.m, grid_world.n, (grid_world.start_x, grid_world.start_y),
        #                           (grid_world.end_x, grid_world.end_y), grid_world.obstacles)
        # grid_world.move_on_given_route_genetic()
        # tk.mainloop()
        loop_count += 1
    try:
        print(m, numeerator / denomenator)
    except ZeroDivisionError:
        pass

    grid_size += 1

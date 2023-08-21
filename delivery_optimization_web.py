import random
import requests
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours}h {minutes}m {seconds}s"

def create_data_model(locations, num_vehicles=2):
    data = {}
    data['locations'] = locations
    data['num_vehicles'] = num_vehicles
    data['depot'] = 0  # Starting location (index of the Firm location in the locations list)
    return data


def initialize_population(num_routes, num_locations):
    population = []
    for _ in range(num_routes):
        route = list(range(1, num_locations))  # Exclude the starting location (Firm)
        random.shuffle(route)
        population.append(route)
    return population



def calculate_fitness(route, duration_matrix):
    total_duration = duration_matrix[0][route[0]]
    for i in range(len(route) - 1):
        total_duration += duration_matrix[route[i]][route[i + 1]]
    total_duration += duration_matrix[route[-1]][0]  # Return to the Firm
    return total_duration


def selection(population, duration_matrix, num_selected):
    selected_routes = random.sample(population, num_selected)
    return sorted(selected_routes, key=lambda x: calculate_fitness(x, duration_matrix))[:2]


def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + [gene for gene in parent2 if gene not in parent1[:crossover_point]]
    child2 = parent2[:crossover_point] + [gene for gene in parent1 if gene not in parent2[:crossover_point]]
    return child1, child2


def mutation(route):
    mutation_point1, mutation_point2 = random.sample(range(len(route)), 2)
    route[mutation_point1], route[mutation_point2] = route[mutation_point2], route[mutation_point1]
    return route


def genetic_algorithm(distance_matrix, num_routes, num_generations):
    num_locations = len(distance_matrix)
    population = initialize_population(num_routes, num_locations)

    for generation in range(num_generations):
        new_population = []
        for _ in range(num_routes // 2):
            parent1, parent2 = selection(population, distance_matrix, 2)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutation(child1)
            child2 = mutation(child2)
            new_population.extend([child1, child2])
        population = new_population

    best_route = min(population, key=lambda x: calculate_fitness(x, distance_matrix))
    return [0] + best_route + [0]  # Include the starting location (Firm)





def solve_tsp_with_vehicles(data, duration_matrix,max_duration=1):
    max_duration=max_duration*3600

    manager = pywrapcp.RoutingIndexManager(len(duration_matrix),
                                           data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def duration_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return duration_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(duration_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 1

    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        routes = []
        vehicle_id=data['num_vehicles']-1
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            index = solution.Value(routing.NextVar(index))
        routes.append(route)

        total_durations = [
            sum(duration_matrix[route[j - 1]][route[j]] for j in range(1, len(route)))
            for route in routes
        ]

        # Find the best route and check if its duration exceeds one hour
        best_route_idx = total_durations.index(min(total_durations))
        best_route_duration = total_durations[best_route_idx]

        if best_route_duration > max_duration and data['num_vehicles'] >= 2:
            # Split the best route into multiple routes if needed
            best_route = routes[best_route_idx]
            new_routes = split_route(best_route, duration_matrix,max_duration)
            if new_routes:
                routes.pop(best_route_idx)
                routes.extend(new_routes)

        return routes

    return None

def split_route(route, duration_matrix,max_duration=1):
    #max_duration=max_duration*3600: done in split_route
    sub_routes = []
    sub_route = [0]
    duration_sum = 0

    for i in range(1, len(route)):
        duration_sum += duration_matrix[route[i - 1]][route[i]]
        if duration_sum > max_duration:
            if len(sub_route) > 1:  # Avoid sub-routes with only the starting location
                sub_routes.append(sub_route)
            sub_route = [0]
            duration_sum = 0

        sub_route.append(route[i])

    sub_routes.append(sub_route)
    return sub_routes


'''def get_route_distances(locations, api_key):
    url = 'http://www.mapquestapi.com/directions/v2/route'
    distances = [[0] * len(locations) for _ in range(len(locations))]

    for i in range(len(locations)):
        for j in range(i + 1, len(locations)):
            params = {
                'key': api_key,
                'from': locations[i],
                'to': locations[j]
            }
            response = requests.get(url, params=params)
            route_data = response.json()
            distance = route_data['route']['distance']
            distances[i][j] = distance
            distances[j][i] = distance

    return distances'''
def get_route_durations(locations, api_key):
    url = 'http://www.mapquestapi.com/directions/v2/route'
    durations = [[0] * len(locations) for _ in range(len(locations))]

    for i in range(len(locations)):
        for j in range(i + 1, len(locations)):
            params = {
                'key': api_key,
                'from': locations[i],
                'to': locations[j]
            }
            response = requests.get(url, params=params)
            route_data = response.json()
            duration = route_data['route']['time']  # Duration in seconds formattedTime
            durations[i][j] = duration
            durations[j][i] = duration

    return durations

def optimize_delivery(firm,locations,MAPQUEST_API_KEY = 'xxRZu1my4jvVfOfYO6NnFDbJo37lCzLk',num_vehicules=2,max_duration=1):
    # Replace this with your actual API key
    MAPQUEST_API_KEY = MAPQUEST_API_KEY

    # List of locations (Firm, A, B, C, D)
    locations.insert(0,firm)

    locations = locations#["marsa,tunis", "ain zaghouen, tunis", "manouba", "sidi bousaid, tunis"]
    # Create a dictionary to map indices to location names
    index_to_location = {i: loc for i, loc in enumerate(locations)}

    # Number of available vehicles
    num_vehicles = num_vehicules

    # Fetch the route durations using MapQuest API
    duration_matrix = get_route_durations(locations, MAPQUEST_API_KEY)
    # print(duration_matrix)
    data = create_data_model(locations, num_vehicles)
    routes = solve_tsp_with_vehicles(data, duration_matrix,max_duration)
    string=""
    if routes:
        for i, route in enumerate(routes):

            total_duration = sum(duration_matrix[route[j - 1]][route[j]] for j in range(1, len(route)))
            route_names = [index_to_location[loc_idx] for loc_idx in route]
            string+= f"Optimal Route for Vehicle {i + 1}: {' -> '.join(route_names)} \n"
            string+= f"Total Road Time for Vehicle {i + 1}: {seconds_to_hms(total_duration)} seconds \n\n"
            
    else:
        string="No solution found."
    return string
#optimize_delivery(firm='Megrine,tunis',locations=['Megrine,tunis', "marsa,tunis", "ain zaghouen, tunis", "manouba", "sidi bousaid, tunis"],num_vehicules=5)
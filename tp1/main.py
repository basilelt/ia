import tkinter as tk
from tkinter import ttk
import csv
import random
from queue import Queue
from queue import LifoQueue
from queue import PriorityQueue
import math
import time

from src.Node import Node
from src.Town import Town
from src.Road import Road


search_algorithms = (
    "Parcours en largeur",
    "Parcours en profondeur",
    "Parcours en profondeur itératif",
    "Recherche à coût Uniforme",
    "Recherche gloutonne",
    "A*",
)
costs = ("distance", "temps")

town_color = "lightcoral"
road_color = "lightgreen"
path_color = "red"
visited_color = "blue"


def deg2rad(deg):
    return deg * (math.pi / 180)


# Distance vol d'oiseau
def crowfliesdistance(town1, town2):
    lat1 = town1.latitude
    lon1 = town1.longitude
    lat2 = town2.latitude
    lon2 = town2.longitude

    R = 6371  # Radius of the earth in km
    dLat = deg2rad(lat2 - lat1)
    dLon = deg2rad(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(deg2rad(lat1)) * math.cos(
        deg2rad(lat2)
    ) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
    # distance in km


def mark_town_visited(town):
    """Mark a town as visited by changing its color to blue"""
    if town in town_circles:
        canvas1.itemconfig(town_circles[town], fill=visited_color)
        canvas1.update()  # Force GUI update


# A-Star
def a_star(start_town, end_town, cost_type):
    start_node = Node(start_town)
    if start_town == end_town:
        return start_node
    return None


# Recherche gloutonne
def greedy_search(start_town, end_town, cost_type):
    start_node = Node(start_town)

    # Initialize heuristic for start node
    start_node.path_cost = crowfliesdistance(start_town, end_town)

    frontier = PriorityQueue(maxsize=0)
    frontier.put((start_node.path_cost, start_node))
    explored = set()

    # Track actual path costs
    actual_costs = {start_node.state: 0}

    while not frontier.empty():
        node_cost, node = frontier.get()  # get the node with the lowest heuristic cost
        mark_town_visited(node.state)

        if node.state == end_town:
            node.path_cost = actual_costs[node.state]  # Return actual path cost
            return node

        if node.state in explored:
            continue

        explored.add(node.state)
        for neighbour, road in node.state.neighbours.items():
            child = Node(neighbour, node, road)
            if child.state in explored:
                continue

            if cost_type == 0:  # distance
                new_actual_cost = actual_costs[node.state] + road.distance
            else:  # time
                new_actual_cost = actual_costs[node.state] + road.time
            actual_costs[child.state] = new_actual_cost

            # Use heuristic from child to goal for priority
            child.path_cost = crowfliesdistance(neighbour, end_town)
            frontier.put((child.path_cost, child))

    return None  # No path found (greedy is not complete)


# Parcours à coût uniforme
def ucs(start_town, end_town, cost_type):
    start_node = Node(start_town)
    frontier = PriorityQueue(maxsize=0)
    frontier.put((start_node.path_cost, start_node))
    explored = set()

    # Track costs in frontier
    frontier_costs = {start_node.state: start_node.path_cost}

    while not frontier.empty():
        node_cost, node = frontier.get()  # get the node with the lowest cost
        mark_town_visited(node.state)

        # skip if better path found
        if node.state in explored or node_cost > frontier_costs.get(node.state):
            continue

        if node.state == end_town:
            return node

        explored.add(node.state)
        for neighbour, road in node.state.neighbours.items():
            child = Node(neighbour, node, road)

            if cost_type == 0:  # distance
                child.path_cost = node.path_cost + road.distance
            else:  # time
                child.path_cost = node.path_cost + road.time

            if child.state not in explored:
                if (
                    child.state not in frontier_costs
                    or child.path_cost < frontier_costs[child.state]
                ):
                    frontier_costs[child.state] = child.path_cost
                    frontier.put((child.path_cost, child))


def dfs_recursive(node, end_town, explored, cost_type, depth_limit=None):
    mark_town_visited(node.state)

    if node.state == end_town:
        return node

    if depth_limit == 0:
        return None

    explored.add(node.state)
    for neighbour, road in node.state.neighbours.items():
        if neighbour not in explored:
            child = Node(neighbour, node, road)

            if cost_type == 0:  # distance
                child.path_cost = node.path_cost + road.distance
            else:  # time
                child.path_cost = node.path_cost + road.time

            if depth_limit is not None:
                result = dfs_recursive(
                    child, end_town, explored, cost_type, depth_limit - 1
                )
            else:
                result = dfs_recursive(child, end_town, explored, cost_type)
            if result:
                return result


# Parcours en profondeur itératif
def dfs_iter(start_town, end_town, cost_type):
    start_node = Node(start_town)
    depth = 0
    while True:
        explored = set()
        result = dfs_recursive(start_node, end_town, explored, cost_type, depth)
        if result:
            return result
        depth += 1


# Parcours en profondeur récursif
def dfs(start_town, end_town, cost_type):
    start_node = Node(start_town)
    explored = set()
    return dfs_recursive(start_node, end_town, explored, cost_type)


# Parcours en largeur
def bfs(start_town, end_town, cost_type):
    start_node = Node(start_town)
    frontier = Queue(maxsize=0)
    frontier.put(start_node)
    explored = set()

    while not frontier.empty():
        node = frontier.get()
        mark_town_visited(node.state)

        if node.state == end_town:
            return node

        if node.state not in explored:
            explored.add(node.state)
            # print("Exploring:", node.state.name)
            for neighbour, road in node.state.neighbours.items():
                child = Node(neighbour, node, road)

                if cost_type == 0:  # distance
                    child.path_cost = node.path_cost + road.distance
                else:  # time
                    child.path_cost = node.path_cost + road.time

                # print("  Child:", child.state.name, "Cost:", child.path_cost)
                frontier.put(child)


def display_path(path):
    current_node = path
    # print("current_node:", current_node.state.name)
    while current_node.parent is not None:
        canvas1.itemconfig(road_lines[current_node.road_to_parent], fill=path_color)
        # print(
        #     current_node.road_to_parent.town1.name,
        #     current_node.road_to_parent.town2.name,
        # )
        current_node = current_node.parent


def run_search():
    button_run["state"] = tk.DISABLED
    # Reset all roads and towns to normal colors
    for road in roads:
        canvas1.itemconfig(road_lines[road], fill=road_color)
    for town in towns.values():
        canvas1.itemconfig(town_circles[town], fill=town_color)
    start_city = towns[combobox_start.current() + 1]
    end_city = towns[combobox_end.current() + 1]
    search_method = combobox_algorithm.current()
    cost_type = combobox_cost.current()
    computing_time = time.time()
    if search_method == 0:  # Parcours en largeur
        path = bfs(start_city, end_city, cost_type)
    elif search_method == 1:  # Parcours en profondeur
        path = dfs(start_city, end_city, cost_type)
    elif search_method == 2:  # Parcours en profondeur itératif
        path = dfs_iter(start_city, end_city, cost_type)
    elif search_method == 3:  # Parcours à coût uniforme
        path = ucs(start_city, end_city, cost_type)
    elif search_method == 4:  # Recherche gloutonne
        path = greedy_search(start_city, end_city, cost_type)
    elif search_method == 5:  # A*
        path = a_star(start_city, end_city, cost_type)
    else:
        path = None
    computing_time = time.time() - computing_time
    if path is not None:
        label_path_title["text"] = (
            "Itinéraire de "
            + start_city.name
            + " à "
            + end_city.name
            + " avec "
            + search_algorithms[search_method]
        )
        if cost_type == 0:  # distance
            label_distance["text"] = "Distance: " + str(path.path_cost) + "km"
        else:  # time
            label_distance["text"] = "Temps: " + str(path.path_cost) + "min"
        label_computing_time["text"] = "Temps de calcul: " + str(computing_time) + "s"
        display_path(path)
    button_run["state"] = tk.NORMAL


def longitude_to_pixel(longitude):
    return (longitude - map_W) * diff_W_E


def latitude_to_pixel(latitude):
    return (map_N - latitude) * diff_N_S


# Read towns and roads csv and create relative objects
towns = dict()
roads = list()
with open("data/towns.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=";")
    for row in reader:
        towns[int(row["dept_id"])] = Town(
            dept_id=int(row["dept_id"]),
            name=row["name"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
        )
with open("data/roads.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=";")
    for row in reader:
        road = Road(
            town1=towns[int(row["town1"])],
            town2=towns[int(row["town2"])],
            distance=int(row["distance"]),
            time=int(row["time"]),
        )
        roads.append(road)
        road.town1.neighbours[road.town2] = road
        road.town2.neighbours[road.town1] = road


window = tk.Tk()
window.title("Itineria")

# Décommenter la carte pour choisir la bonne taille pour votre machine
# map_image = tk.PhotoImage(file="img/France_map_admin_1066_1024.png")
# map_image = tk.PhotoImage(file="img/France_map_admin_799_768.png")
map_image = tk.PhotoImage(file="img/France_map_admin_499_480.png")


width = map_image.width()
height = map_image.height()
canvas1 = tk.Canvas(window, width=width, height=height)

background_map = canvas1.create_image(0, 0, anchor=tk.NW, image=map_image)

# Dessin des routes et villes
map_N = 51.5
map_S = 41
map_W = -5.8
map_E = 10
diff_W_E = width / (map_E - map_W)
diff_N_S = height / (map_N - map_S)
town_radius = 4
road_width = 3

road_lines = dict()
for road in roads:
    road_lines[road] = canvas1.create_line(
        longitude_to_pixel(road.town1.longitude),
        latitude_to_pixel(road.town1.latitude),
        longitude_to_pixel(road.town2.longitude),
        latitude_to_pixel(road.town2.latitude),
        fill=road_color,
        width=road_width,
    )

town_circles = dict()
for town in towns.values():
    town_circles[town] = canvas1.create_oval(
        longitude_to_pixel(town.longitude) - town_radius,
        latitude_to_pixel(town.latitude) - town_radius,
        longitude_to_pixel(town.longitude) + town_radius,
        latitude_to_pixel(town.latitude) + town_radius,
        fill=town_color,
    )


canvas1.grid(row=0, column=0, columnspan=4)
label_start = tk.Label(window, text="Départ")
label_start.grid(row=1, column=0)
combobox_start = ttk.Combobox(window, state="readonly")
combobox_start.grid(row=1, column=1)

label_end = tk.Label(window, text="Arrivée")
label_end.grid(row=1, column=2)
combobox_end = ttk.Combobox(window, state="readonly")
combobox_end.grid(row=1, column=3)

town_list = []
for town in towns.values():
    town_list.append(str(town.dept_id) + " - " + town.name)
combobox_start["values"] = town_list
combobox_end["values"] = town_list
combobox_start.current(random.randint(0, len(town_list) - 1))
combobox_end.current(random.randint(0, len(town_list) - 1))

label_algorithm = tk.Label(window, text="Algorithme")
label_algorithm.grid(row=2, column=0)
combobox_algorithm = ttk.Combobox(window, state="readonly")
combobox_algorithm.grid(row=2, column=1)
combobox_algorithm["values"] = search_algorithms
combobox_algorithm.current(random.randint(0, len(combobox_algorithm["values"]) - 1))

label_cost = tk.Label(window, text="Coût")
label_cost.grid(row=2, column=2)
combobox_cost = ttk.Combobox(window, state="readonly")
combobox_cost.grid(row=2, column=3)
combobox_cost["values"] = costs
combobox_cost.current(random.randint(0, len(combobox_cost["values"]) - 1))

label_path_title = tk.Label(window, text="")
label_path_title.grid(row=3, column=0, columnspan=4)

label_distance = tk.Label(window, text="")
label_distance.grid(row=4, column=0)

label_computing_time = tk.Label(window, text="")
label_computing_time.grid(row=4, column=3)

button_run = tk.Button(window, text="Calculer", command=run_search)
button_run.grid(row=5, column=0)

button_quit = tk.Button(window, text="Quitter", command=window.destroy)
button_quit.grid(row=5, column=3)
window.mainloop()

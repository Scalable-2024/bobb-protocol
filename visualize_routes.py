import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def visualize_routes_colored_by_type(file_path):
    """
    Reads a JSON file and visualizes all routes in a single graph, 
    with different colors for each route type.
    
    Parameters:
    - file_path (str): Path to the JSON file containing the routes data.
    """
    # Read JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)

    G = nx.DiGraph()
    edge_colors = []
    color_map = {}  # To map route types to colors
    # Use Tableau colors for clarity
    available_colors = list(mcolors.TABLEAU_COLORS.values())

    # Assign colors to each route type dynamically
    for source, destinations in data.items():
        for dest, routes in destinations.items():
            for route in routes:
                route_type = route["type"]
                path = [source] + route["path"] + [dest]
                edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]

                # Add edges to graph
                G.add_edges_from(edges)

                # Assign color based on route type
                if route_type not in color_map:
                    color_map[route_type] = available_colors[len(
                        color_map) % len(available_colors)]

                edge_colors.extend([color_map[route_type]] * len(edges))

    # Plot the graph
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42)  # Layout for consistent visualization
    nx.draw(G, pos, with_labels=True, node_size=1500, font_size=10,
            font_color="black", node_color="blue", edge_color=edge_colors, width=2)

    # Create a legend for route types
    legend_handles = [plt.Line2D([0], [0], color=color, lw=2, label=route_type)
                      for route_type, color in color_map.items()]
    plt.legend(handles=legend_handles, title="Route Types", loc="upper right")

    plt.title("Routes Visualization (Colored by Type)")
    plt.show()


# Call the function with your file path
# Replace this with the actual path to your JSON file
file_path = "resources/satellite_routes/10.6.60.25:33001.json"
visualize_routes_colored_by_type(file_path)

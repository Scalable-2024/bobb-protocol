import json
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import networkx as nx
from enum import Enum, auto


class RouteType(Enum):
    DIRECT = auto()
    FUNCTION_BASED = auto()
    LOAD_BALANCED = auto()
    RANDOM = auto()


@dataclass
class SatelliteNode:
    id: str
    function: str
    last_contact: int
    public_key: str
    neighbours: Dict[str, dict]
    load: int = 0

    def __hash__(self):
        return hash(self.id)


@dataclass
class Route:
    path: List[str]
    type: RouteType
    score: float
    metrics: Dict[str, float]


class RouteGenerator:
    def __init__(self, constellation_file: str):
        self.constellation_file = constellation_file
        self.satellites = self._load_satellites()
        self.route_stats = defaultdict(int)
        self.network_graph = self._create_network_graph()

    def _load_satellites(self) -> Dict[str, SatelliteNode]:
        with open(self.constellation_file, 'r') as f:
            constellation = json.load(f)

        satellites = {}
        for sat_id, data in constellation.items():
            satellites[sat_id] = SatelliteNode(
                id=sat_id,
                function=list(data['neighbours'].values())[0]['function'],
                last_contact=data['freshness'],
                public_key=list(data['neighbours'].values())[0]['public_key'],
                neighbours=data['neighbours']
            )
        return satellites

    def _create_network_graph(self) -> nx.Graph:
        """Create a NetworkX graph of the satellite constellation"""
        G = nx.Graph()
        for sat_id, sat in self.satellites.items():
            G.add_node(sat_id, function=sat.function, load=sat.load)
            for neighbor_id in sat.neighbours:
                G.add_edge(sat_id, neighbor_id)
        return G

    def generate_direct_route(self, source_id: str, dest_id: str) -> Optional[Route]:
        """Generate direct route if possible"""
        if dest_id in self.satellites[source_id].neighbours:
            return Route(
                path=[dest_id],
                type=RouteType.DIRECT,
                score=100.0,
                metrics={"hops": 1, "function_match": 1.0, "load": 0}
            )
        return None

    def generate_function_based_route(
        self, source_id: str, dest_id: str, existing_routes: List[Route]
    ) -> Optional[Route]:
        source = self.satellites[source_id]
        destination = self.satellites[dest_id]
        route = []
        visited = {source_id}
        current = source_id
        metrics = defaultdict(float)

        def score_next_hop(current_sat: SatelliteNode, next_sat: SatelliteNode) -> Tuple[float, Dict[str, float]]:
            scores = {}

            # Function matching
            scores['function_match'] = 100 if next_sat.function == source.function else 0

            # Direct neighbor bonus
            scores['neighbor_bonus'] = 50 if next_sat.id in current_sat.neighbours else 0

            # Connection freshness
            time_diff = abs(next_sat.last_contact - current_sat.last_contact)
            scores['freshness'] = 30 * (1 / (1 + time_diff/1000))

            # Distance to destination
            scores['dest_proximity'] = 40 if dest_id in next_sat.neighbours else 0

            total_score = sum(scores.values())
            return total_score, scores

        while current != dest_id:
            current_sat = self.satellites[current]
            candidates = [
                sat_id for sat_id, sat in self.satellites.items()
                if sat_id not in visited and sat_id in current_sat.neighbours
            ]

            if not candidates:
                return None

            # Score all candidates
            candidate_scores = {
                sat_id: score_next_hop(current_sat, self.satellites[sat_id])
                for sat_id in candidates
            }

            next_hop = max(candidate_scores.keys(),
                           key=lambda x: candidate_scores[x][0])
            score, hop_metrics = candidate_scores[next_hop]

            # Update metrics
            for key, value in hop_metrics.items():
                metrics[key] += value

            route.append(next_hop)
            visited.add(next_hop)
            current = next_hop

            if len(route) > 3:
                return None

        return Route(
            path=route,
            type=RouteType.FUNCTION_BASED,
            score=sum(metrics.values()) / len(route),
            metrics=dict(metrics)
        )

    def generate_load_balanced_route(
        self, source_id: str, dest_id: str, existing_routes: List[Route]
    ) -> Optional[Route]:
        satellite_load = self._calculate_network_load(existing_routes)
        route = []
        visited = {source_id}
        current = source_id
        metrics = defaultdict(float)

        def score_next_hop(next_sat: SatelliteNode) -> Tuple[float, Dict[str, float]]:
            scores = {}

            # Load balancing
            current_load = satellite_load[next_sat.id]
            scores['load_balance'] = 100 * (1 / (1 + current_load))

            # Connection freshness
            time_diff = abs(next_sat.last_contact -
                            self.satellites[current].last_contact)
            scores['freshness'] = 30 * (1 / (1 + time_diff/1000))

            # Available capacity
            available_connections = len(
                next_sat.neighbours) - satellite_load[next_sat.id]
            scores['capacity'] = 20 * \
                (available_connections / len(next_sat.neighbours))

            # Distance to destination
            scores['dest_proximity'] = 40 if dest_id in next_sat.neighbours else 0

            total_score = sum(scores.values())
            return total_score, scores

        while current != dest_id:
            current_sat = self.satellites[current]
            candidates = [
                sat_id for sat_id, sat in self.satellites.items()
                if sat_id not in visited and sat_id in current_sat.neighbours
            ]

            if not candidates:
                return None

            candidate_scores = {
                sat_id: score_next_hop(self.satellites[sat_id])
                for sat_id in candidates
            }

            next_hop = max(candidate_scores.keys(),
                           key=lambda x: candidate_scores[x][0])
            score, hop_metrics = candidate_scores[next_hop]

            for key, value in hop_metrics.items():
                metrics[key] += value

            route.append(next_hop)
            visited.add(next_hop)
            current = next_hop
            satellite_load[next_hop] += 1

            if len(route) > 3:
                return None

        return Route(
            path=route,
            type=RouteType.LOAD_BALANCED,
            score=sum(metrics.values()) / len(route),
            metrics=dict(metrics)
        )

    def generate_random_route(
        self, source_id: str, dest_id: str, max_hops: int = 3
    ) -> Optional[Route]:
        """Generate a random valid route"""
        route = []
        visited = {source_id}
        current = source_id
        metrics = {"randomness": random.random() * 100}

        while current != dest_id:
            current_sat = self.satellites[current]
            candidates = [
                sat_id for sat_id, sat in self.satellites.items()
                if sat_id not in visited and sat_id in current_sat.neighbours
            ]

            if not candidates:
                return None

            next_hop = random.choice(candidates)
            route.append(next_hop)
            visited.add(next_hop)
            current = next_hop

            if len(route) > max_hops:
                return None

        return Route(
            path=route,
            type=RouteType.RANDOM,
            score=50.0,  # Fixed middle score for random routes
            metrics=metrics
        )

    def _calculate_network_load(self, routes: List[Route]) -> Dict[str, int]:
        """Calculate current load on each satellite"""
        load = defaultdict(int)
        for route in routes:
            for hop in route.path:
                load[hop] += 1
        return load


def generate_all_routes(constellation_file: str) -> Dict[str, Dict[str, List[Route]]]:
    generator = RouteGenerator(constellation_file)
    routes = {}

    for source_id in generator.satellites:
        routes[source_id] = {}

        for dest_id in generator.satellites:
            if source_id != dest_id:
                routes[source_id][dest_id] = []
                existing_routes = routes[source_id][dest_id]

                # 1. Direct Route (Highest Priority)
                direct_route = generator.generate_direct_route(
                    source_id, dest_id)
                if direct_route:
                    existing_routes.append(direct_route)

                # 2. Function-based Route
                func_route = generator.generate_function_based_route(
                    source_id, dest_id, existing_routes
                )
                if func_route:
                    existing_routes.append(func_route)

                # 3. Load-balanced Route
                balanced_route = generator.generate_load_balanced_route(
                    source_id, dest_id, existing_routes
                )
                if balanced_route:
                    existing_routes.append(balanced_route)

                # 4. Random Route (Lowest Priority)
                random_route = generator.generate_random_route(
                    source_id, dest_id)
                if random_route:
                    existing_routes.append(random_route)

                # Sort routes by score within their priority class
                existing_routes.sort(
                    key=lambda x: (x.type.value, -x.score)
                )

    # Generate visualizations
    generator.visualize_routes(routes, "resources/route_visualizations")

    return routes


def create_routing_tables():
    base_dir = os.getcwd()
    constellation_dir = os.path.join(
        base_dir, "resources", "satellite_constellation_set")
    routes_dir = os.path.join(base_dir, "resources", "satellite_routes")

    os.makedirs(routes_dir, exist_ok=True)

    for filename in os.listdir(constellation_dir):
        if filename.startswith("constellation_") and filename.endswith(".json"):
            port = filename.split("_")[1].split(".")[0]
            constellation_path = os.path.join(constellation_dir, filename)

            # Read constellation file to get the full satellite ID
            with open(constellation_path, 'r') as f:
                constellation = json.load(f)
                # Get the satellite ID that matches this port
                satellite_id = next(
                    sat_id for sat_id in constellation.keys()
                    if sat_id.endswith(f":{port}")
                )

            # Generate routes with all strategies
            routes = generate_all_routes(constellation_path)

            # Convert Route objects to serializable format
            serializable_routes = {}
            for source in routes:
                serializable_routes[source] = {}
                for dest in routes[source]:
                    serializable_routes[source][dest] = [
                        {
                            "path": route.path,
                            "type": route.type.name,
                            "score": route.score,
                            "metrics": route.metrics
                        }
                        for route in routes[source][dest]
                    ]

            # Save routes to file using full satellite ID
            routes_file = os.path.join(
                routes_dir, f"{satellite_id}.json")  # Using full IP:port
            with open(routes_file, 'w') as f:
                json.dump(serializable_routes, f, indent=4)

            print(f"Generated routes for satellite {satellite_id}")


if __name__ == "__main__":
    create_routing_tables()

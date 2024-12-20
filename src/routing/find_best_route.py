# Written by Aryan, heavily modified by Niels
from typing import Optional, List, Dict, Tuple
import random
from dataclasses import dataclass
from flask import Blueprint, app, jsonify, request  # Add request here
import base64
import json
import os

from flask import Blueprint, app, jsonify

from src.config.constants import SATELLITE_FUNCTION_DISASTER_IMAGING, BASESTATION
from src.controllers.create_headers import create_header
from src.controllers.hello import hello
from src.controllers.identify import return_identity
from src.controllers.handshake import handshake
from src.heartbeat.heartbeat import heartbeat
from src.middleware.header_middleware import check_headers
from enum import Enum
from typing import Dict, List, Optional, Tuple


class RouteType(Enum):
    DIRECT = 10
    FUNCTION_BASED = 3
    LOAD_BALANCED = 2
    RANDOM = 1


@dataclass
class Route:
    path: List[str]
    type: RouteType
    score: float
    metrics: Dict[str, float]


def find_best_route(source: str, destination: str, priority: str = "medium") -> Optional[Dict]:
    """
    Find the best route based on priority and weights.
    Returns route information including path, type, and metrics.
    """
    try:
        # Load routing table for source satellite
        routes_file = f"resources/satellite_routes/{source}.json"

        with open(routes_file, 'r') as f:
            routing_table = json.load(f)
            f.close()

        if destination not in routing_table[source]:
            return None

        available_routes = routing_table[source][destination]

        # Assign weights based on priority
        priority_weights = {
            "high": {
                "DIRECT": 1.0,
                "FUNCTION_BASED": 0.8,
                "LOAD_BALANCED": 0.6,
                "RANDOM": 0.4
            },
            "medium": {
                "DIRECT": 0.8,
                "FUNCTION_BASED": 1.0,
                "LOAD_BALANCED": 0.8,
                "RANDOM": 0.6
            },
            "low": {
                "DIRECT": 0.6,
                "FUNCTION_BASED": 0.8,
                "LOAD_BALANCED": 1.0,
                "RANDOM": 0.8
            }
        }

        # Score each route based on type and metrics
        scored_routes = []
        for route in available_routes:
            # print(route)
            base_weight = RouteType[route["type"]].value
            priority_weight = priority_weights[priority][route["type"]]

            # Calculate composite score
            score = base_weight * priority_weight * route["score"]

            scored_routes.append({
                "path": route["path"],
                "type": route["type"],
                "score": score,
                "metrics": route["metrics"]
            })

        # Select best route
        best_route = max(scored_routes, key=lambda x: x["score"])
        # print(best_route)

        return best_route

    except Exception as e:
        print(f"Error finding route: {str(e)}")
        return None


# Add these imports at the top


def simulate_satellite_failure(satellite_id: str) -> bool:
    """
    Randomly determine if a satellite should fail
    Returns True if satellite fails, False if operational
    """
    # 20% chance of failure (adjust as needed)
    return random.random() < 0.2


def get_next_available_hop(route: List[str], current_hop_index: int, routing_table: Dict) -> Optional[str]:
    """
    Get next available hop from the route, skipping failed satellites
    """
    remaining_hops = route[current_hop_index:]
    for next_hop in remaining_hops:
        if not simulate_satellite_failure(next_hop):
            return next_hop
    return None


def find_alternate_route(source: str, destination: str, failed_satellites: List[str], priority: str = "medium") -> Optional[Dict]:
    """
    Find an alternate route avoiding failed satellites
    """
    try:
        routes_file = f"resources/satellite_routes/{source}.json"
        with open(routes_file, 'r') as f:
            routing_table = json.load(f)

        if destination not in routing_table[source]:
            return None

        available_routes = routing_table[source][destination]

        # Filter out routes that use failed satellites
        valid_routes = [
            route for route in available_routes
            if not any(sat in failed_satellites for sat in route["path"])
        ]

        if not valid_routes:
            return None

        # Use existing priority system to select best valid route
        priority_weights = {
            "high": {
                "DIRECT": 1.0,
                "FUNCTION_BASED": 0.8,
                "BALANCED": 0.6,
                "RANDOM": 0.4
            },
            "medium": {
                "DIRECT": 0.8,
                "FUNCTION_BASED": 1.0,
                "BALANCED": 0.8,
                "RANDOM": 0.6
            },
            "low": {
                "DIRECT": 0.6,
                "FUNCTION_BASED": 0.8,
                "BALANCED": 1.0,
                "RANDOM": 0.8
            }
        }

        scored_routes = []
        for route in valid_routes:
            base_weight = RouteType[route["type"]].value
            priority_weight = priority_weights[priority][route["type"]]
            score = base_weight * priority_weight * route["score"]
            scored_routes.append({
                "path": route["path"],
                "type": route["type"],
                "score": score,
                "metrics": route["metrics"]
            })

        if not scored_routes:
            return None

        best_route = max(scored_routes, key=lambda x: x["score"])
        best_route["routing_table"] = routing_table[source]
        return best_route

    except Exception as e:
        print(f"Error finding alternate route: {str(e)}")
        return None

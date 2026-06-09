from flask import Flask, render_template_string, request
import math
import requests
import urllib.request
import xml.etree.ElementTree as ET

app = Flask(__name__)

WEATHER_API_KEY = "25c9a61b99a4842679a8983536494752"
TRUE_HOST_NATIONS = ["Mexico", "Canada", "USA"]

TEAM_STAT_DATABASE = {
    "Mexico": {"base_xg": 1.65, "shots_avg": 13.4, "shots_conceded_avg": 9.8, "shot_accuracy": 0.36, "gk_save_pct": 0.73, "corners_avg": 5.8, "cards_avg": 2.2, "offsides_avg": 1.9, "goal_kicks_avg": 7.2},
    "South Africa": {"base_xg": 1.15, "shots_avg": 10.2, "shots_conceded_avg": 12.4, "shot_accuracy": 0.31, "gk_save_pct": 0.67, "corners_avg": 4.1, "cards_avg": 1.9, "offsides_avg": 1.5, "goal_kicks_avg": 8.8},
    "South Korea": {"base_xg": 1.52, "shots_avg": 12.8, "shots_conceded_avg": 10.1, "shot_accuracy": 0.35, "gk_save_pct": 0.70, "corners_avg": 5.4, "cards_avg": 1.5, "offsides_avg": 2.1, "goal_kicks_avg": 6.9},
    "Czech Republic": {"base_xg": 1.38, "shots_avg": 11.9, "shots_conceded_avg": 11.2, "shot_accuracy": 0.33, "gk_save_pct": 0.72, "corners_avg": 4.9, "cards_avg": 2.4, "offsides_avg": 1.7, "goal_kicks_avg": 7.5},
    "USA": {"base_xg": 1.58, "shots_avg": 13.1, "shots_conceded_avg": 9.9, "shot_accuracy": 0.37, "gk_save_pct": 0.74, "corners_avg": 5.6, "cards_avg": 1.7, "offsides_avg": 2.0, "goal_kicks_avg": 7.1},
    "England": {"base_xg": 2.04, "shots_avg": 15.8, "shots_conceded_avg": 8.3, "shot_accuracy": 0.40, "gk_save_pct": 0.75, "corners_avg": 6.3, "cards_avg": 1.4, "offsides_avg": 2.1, "goal_kicks_avg": 6.1},
    "France": {"base_xg": 2.12, "shots_avg": 16.6, "shots_conceded_avg": 7.9, "shot_accuracy": 0.42, "gk_save_pct": 0.77, "corners_avg": 6.6, "cards_avg": 1.5, "offsides_avg": 2.4, "goal_kicks_avg": 5.8},
    "Brazil": {"base_xg": 2.15, "shots_avg": 16.8, "shots_conceded_avg": 7.8, "shot_accuracy": 0.42, "gk_save_pct": 0.76, "corners_avg": 6.7, "cards_avg": 1.6, "offsides_avg": 2.2, "goal_kicks_avg": 6.0},
    "Arsenal": {"base_xg": 2.20, "shots_avg": 16.1, "shots_conceded_avg": 8.0, "shot_accuracy": 0.41, "gk_save_pct": 0.76, "corners_avg": 6.8, "cards_avg": 1.3, "offsides_avg": 2.0, "goal_kicks_avg": 6.4},
    "Chelsea": {"base_xg": 1.72, "shots_avg": 13.5, "shots_conceded_avg": 10.9, "shot_accuracy": 0.35, "gk_save_pct": 0.71, "corners_avg": 5.4, "cards_avg": 2.2, "offsides_avg": 1.7, "goal_kicks_avg": 7.3},
    "Real Madrid": {"base_xg": 2.30, "shots_avg": 16.9, "shots_conceded_avg": 8.2, "shot_accuracy": 0.43, "gk_save_pct": 0.78, "corners_avg": 6.5, "cards_avg": 1.5, "offsides_avg": 2.2, "goal_kicks_avg": 6.1},
    "Barcelona": {"base_xg": 2.05, "shots_avg": 15.4, "shots_conceded_avg": 9.1, "shot_accuracy": 0.39, "gk_save_pct": 0.73, "corners_avg": 5.9, "cards_avg": 1.9, "offsides_avg": 2.4, "goal_kicks_avg": 6.8},
    "Slavia Prague": {"base_xg": 1.82, "shots_avg": 14.4, "shots_conceded_avg": 8.5, "shot_accuracy": 0.37, "gk_save_pct": 0.75, "corners_avg": 6.2, "cards_avg": 1.6, "offsides_avg": 1.9, "goal_kicks_avg": 6.5},
    "Sparta Prague": {"base_xg": 1.75, "shots_avg": 13.9, "shots_conceded_avg": 9.0, "shot_accuracy": 0.36, "gk_save_pct": 0.72, "corners_avg": 5.8, "cards_avg": 2.0, "offsides_avg": 1.8, "goal_kicks_avg": 7.0}
}

GLOBAL_MATCH_DATABASE = [
    {"id": 1, "cat": "WC", "home": "Mexico", "away": "South Africa", "country": "Mexico", "tier": "Group A", "round": "Matchday 1", "date": "11/06", "city": "Mexico City"},
    {"id": 2, "cat": "WC", "home": "South Korea", "away": "Czech Republic", "country": "Mexico", "tier": "Group A", "round": "Matchday 1", "date": "11/06", "city": "Guadalajara"},
    {"id": 3, "cat": "Leagues", "home": "Arsenal", "away": "Chelsea", "country": "England", "tier": "Premier League", "round": "Round 32", "date": "12/06", "city": "London"},
    {"id": 4, "cat": "Leagues", "home": "Slavia Prague", "away": "Sparta Prague", "country": "Czechia", "tier": "First League", "round": "Round 28", "date": "13/06", "city": "Prague"},
    {"id": 5, "cat": "Cup", "home": "Arsenal", "away": "Chelsea", "country": "England", "tier": "FA Cup", "round": "Semifinal", "date": "14/06", "city": "London"},
    {"id": 6, "cat": "Elite", "home": "Real Madrid", "away": "Arsenal", "country": "Europe", "tier": "Champions League", "round": "Group Week 1", "date": "15/06", "city": "Madrid"},
    {"id": 7, "cat": "Elite", "home": "Czech Republic", "away": "France", "country": "Europe", "tier": "Euro Nations", "round": "Matchday 1", "date": "16/06", "city": "Prague"},
    {"id": 8, "cat": "International", "home": "Brazil", "away": "England", "country": "Global", "tier": "International Friendly", "round": "Friendly Window", "date": "17/06", "city": "Rio de Janeiro"}
]

# (Insert your functions harvest_live_sports_wire, poisson_probability, run_simulation_variant here)
# (Insert your HTML_TEMPLATE here)
# (Insert your @app.route here)

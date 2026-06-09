from flask import Flask, render_template_string, request, jsonify
import math
import requests
import urllib.request
import xml.etree.ElementTree as ET

app = Flask(__name__)

WEATHER_API_KEY = "25c9a61b99a4842679a8983536494752"
TRUE_HOST_NATIONS = ["Mexico", "Canada", "USA"]

# =====================================================================
# 1. LIVE MASTER SQUAD PERFORMANCE ATTRIBUTE MATRIX
# =====================================================================
TEAM_STAT_DATABASE = {
    "Mexico":        {"base_xg": 1.65, "shots_avg": 13.4, "shots_conceded_avg": 9.8,  "shot_accuracy": 0.36, "gk_save_pct": 0.73, "corners_avg": 5.8, "cards_avg": 2.2, "offsides_avg": 1.9},
    "South Africa":  {"base_xg": 1.15, "shots_avg": 10.2, "shots_conceded_avg": 12.4, "shot_accuracy": 0.31, "gk_save_pct": 0.67, "corners_avg": 4.1, "cards_avg": 1.9, "offsides_avg": 1.5},
    "South Korea":   {"base_xg": 1.52, "shots_avg": 12.8, "shots_conceded_avg": 10.1, "shot_accuracy": 0.35, "gk_save_pct": 0.70, "corners_avg": 5.4, "cards_avg": 1.5, "offsides_avg": 2.1},
    "Czech Republic":{"base_xg": 1.38, "shots_avg": 11.9, "shots_conceded_avg": 11.2, "shot_accuracy": 0.33, "gk_save_pct": 0.72, "corners_avg": 4.9, "cards_avg": 2.4, "offsides_avg": 1.7},
    "Canada":        {"base_xg": 1.45, "shots_avg": 12.2, "shots_conceded_avg": 11.5, "shot_accuracy": 0.34, "gk_save_pct": 0.68, "corners_avg": 5.1, "cards_avg": 2.0, "offsides_avg": 1.6},
    "Bosnia":        {"base_xg": 1.22, "shots_avg": 10.8, "shots_conceded_avg": 13.0, "shot_accuracy": 0.32, "gk_save_pct": 0.65, "corners_avg": 4.4, "cards_avg": 2.3, "offsides_avg": 1.8},
    "USA":           {"base_xg": 1.58, "shots_avg": 13.1, "shots_conceded_avg": 9.9,  "shot_accuracy": 0.37, "gk_save_pct": 0.74, "corners_avg": 5.6, "cards_avg": 1.7, "offsides_avg": 2.0},
    "Paraguay":      {"base_xg": 1.08, "shots_avg": 9.5,  "shots_conceded_avg": 10.8, "shot_accuracy": 0.29, "gk_save_pct": 0.75, "corners_avg": 3.8, "cards_avg": 2.8, "offsides_avg": 1.4},
    "Qatar":         {"base_xg": 1.20, "shots_avg": 10.5, "shots_conceded_avg": 13.8, "shot_accuracy": 0.32, "gk_save_pct": 0.66, "corners_avg": 4.3, "cards_avg": 1.8, "offsides_avg": 1.9},
    "Switzerland":   {"base_xg": 1.42, "shots_avg": 12.0, "shots_conceded_avg": 10.5, "shot_accuracy": 0.34, "gk_save_pct": 0.71, "corners_avg": 5.0, "cards_avg": 2.1, "offsides_avg": 1.7},
    "Germany":       {"base_xg": 1.98, "shots_avg": 15.9, "shots_conceded_avg": 8.6,  "shot_accuracy": 0.39, "gk_save_pct": 0.74, "corners_avg": 6.3, "cards_avg": 1.5, "offsides_avg": 2.0},
    "Curaçao":       {"base_xg": 1.02, "shots_avg": 8.9,  "shots_conceded_avg": 15.2, "shot_accuracy": 0.27, "gk_save_pct": 0.63, "corners_avg": 3.2, "cards_avg": 1.8, "offsides_avg": 1.2},
    "Netherlands":   {"base_xg": 1.85, "shots_avg": 14.8, "shots_conceded_avg": 9.2,  "shot_accuracy": 0.38, "gk_save_pct": 0.75, "corners_avg": 6.0, "cards_avg": 1.6, "offsides_avg": 2.1},
    "Japan":         {"base_xg": 1.58, "shots_avg": 13.8, "shots_conceded_avg": 10.1, "shot_accuracy": 0.37, "gk_save_pct": 0.72, "corners_avg": 5.6, "cards_avg": 1.1, "offsides_avg": 1.9},
    "Ivory Coast":   {"base_xg": 1.44, "shots_avg": 12.5, "shots_conceded_avg": 11.2, "shot_accuracy": 0.34, "gk_save_pct": 0.71, "corners_avg": 5.0, "cards_avg": 2.1, "offsides_avg": 1.8},
    "Ecuador":       {"base_xg": 1.40, "shots_avg": 12.1, "shots_conceded_avg": 10.9, "shot_accuracy": 0.35, "gk_save_pct": 0.73, "corners_avg": 4.9, "cards_avg": 2.2, "offsides_avg": 1.6},
    "Sweden":        {"base_xg": 1.52, "shots_avg": 13.2, "shots_conceded_avg": 10.6, "shot_accuracy": 0.36, "gk_save_pct": 0.71, "corners_avg": 5.3, "cards_avg": 1.8, "offsides_avg": 1.7},
    "Tunisia":       {"base_xg": 1.18, "shots_avg": 10.1, "shots_conceded_avg": 12.5, "shot_accuracy": 0.30, "gk_save_pct": 0.68, "corners_avg": 4.0, "cards_avg": 2.4, "offsides_avg": 1.4},
    "Spain":         {"base_xg": 2.02, "shots_avg": 16.4, "shots_conceded_avg": 8.1,  "shot_accuracy": 0.41, "gk_save_pct": 0.75, "corners_avg": 6.5, "cards_avg": 1.4, "offsides_avg": 2.3},
    "Cape Verde":    {"base_xg": 1.16, "shots_avg": 10.4, "shots_conceded_avg": 13.1, "shot_accuracy": 0.31, "gk_save_pct": 0.69, "corners_avg": 4.1, "cards_avg": 2.0, "offsides_avg": 1.5},
    "Belgium":       {"base_xg": 1.80, "shots_avg": 14.9, "shots_conceded_avg": 9.6,  "shot_accuracy": 0.38, "gk_save_pct": 0.73, "corners_avg": 5.8, "cards_avg": 1.6, "offsides_avg": 1.9},
    "Egypt":         {"base_xg": 1.46, "shots_avg": 12.4, "shots_conceded_avg": 11.0, "shot_accuracy": 0.35, "gk_save_pct": 0.70, "corners_avg": 4.9, "cards_avg": 1.8, "offsides_avg": 1.5},
    "Saudi Arabia":  {"base_xg": 1.25, "shots_avg": 11.0, "shots_conceded_avg": 12.9, "shot_accuracy": 0.32, "gk_save_pct": 0.67, "corners_avg": 4.3, "cards_avg": 1.9, "offsides_avg": 1.6},
    "Uruguay":       {"base_xg": 1.76, "shots_avg": 14.4, "shots_conceded_avg": 9.4,  "shot_accuracy": 0.38, "gk_save_pct": 0.74, "corners_avg": 5.9, "cards_avg": 2.5, "offsides_avg": 2.0},
    "Iran":          {"base_xg": 1.34, "shots_avg": 11.6, "shots_conceded_avg": 11.8, "shot_accuracy": 0.33, "gk_save_pct": 0.71, "corners_avg": 4.6, "cards_avg": 2.1, "offsides_avg": 1.7},
    "New Zealand":   {"base_xg": 1.10, "shots_avg": 9.6,  "shots_conceded_avg": 13.8, "shot_accuracy": 0.29, "gk_save_pct": 0.66, "corners_avg": 3.8, "cards_avg": 1.7, "offsides_avg": 1.4},
    "France":        {"base_xg": 2.12, "shots_avg": 16.6, "shots_conceded_avg": 7.9,  "shot_accuracy": 0.42, "gk_save_pct": 0.77, "corners_avg": 6.6, "cards_avg": 1.5, "offsides_avg": 2.4},
    "Senegal":       {"base_xg": 1.50, "shots_avg": 13.0, "shots_conceded_avg": 10.5, "shot_accuracy": 0.36, "gk_save_pct": 0.73, "corners_avg": 5.2, "cards_avg": 2.1, "offsides_avg": 1.6},
    "Iraq":          {"base_xg": 1.20, "shots_avg": 10.3, "shots_conceded_avg": 13.4, "shot_accuracy": 0.31, "gk_save_pct": 0.66, "corners_avg": 4.2, "cards_avg": 2.2, "offsides_avg": 1.8},
    "Norway":        {"base_xg": 1.68, "shots_avg": 14.1, "shots_conceded_avg": 10.0, "shot_accuracy": 0.39, "gk_save_pct": 0.72, "corners_avg": 5.7, "cards_avg": 1.7, "offsides_avg": 1.9},
    "Argentina":     {"base_xg": 2.08, "shots_avg": 16.1, "shots_conceded_avg": 8.0,  "shot_accuracy": 0.43, "gk_save_pct": 0.76, "corners_avg": 6.4, "cards_avg": 1.8, "offsides_avg": 2.2},
    "Algeria":       {"base_xg": 1.45, "shots_avg": 12.6, "shots_conceded_avg": 11.2, "shot_accuracy": 0.35, "gk_save_pct": 0.71, "corners_avg": 5.1, "cards_avg": 2.3, "offsides_avg": 1.6},
    "Austria":       {"base_xg": 1.56, "shots_avg": 13.5, "shots_conceded_avg": 10.3, "shot_accuracy": 0.37, "gk_save_pct": 0.73, "corners_avg": 5.5, "cards_avg": 2.0, "offsides_avg": 1.8},
    "Jordan":        {"base_xg": 1.14, "shots_avg": 9.9,  "shots_conceded_avg": 13.6, "shot_accuracy": 0.30, "gk_save_pct": 0.67, "corners_avg": 3.9, "cards_avg": 1.9, "offsides_avg": 1.5},
    "Portugal":      {"base_xg": 1.96, "shots_avg": 15.5, "shots_conceded_avg": 8.8,  "shot_accuracy": 0.39, "gk_save_pct": 0.73, "corners_avg": 6.1, "cards_avg": 1.8, "offsides_avg": 2.0},
    "Congo DR":      {"base_xg": 1.26, "shots_avg": 11.1, "shots_conceded_avg": 12.6, "shot_accuracy": 0.33, "gk_save_pct": 0.69, "corners_avg": 4.4, "cards_avg": 2.2, "offsides_avg": 1.4},
    "Uzbekistan":    {"base_xg": 1.30, "shots_avg": 11.4, "shots_conceded_avg": 12.0, "shot_accuracy": 0.34, "gk_save_pct": 0.71, "corners_avg": 4.6, "cards_avg": 1.7, "offsides_avg": 1.6},
    "Colombia":      {"base_xg": 1.66, "shots_avg": 14.0, "shots_conceded_avg": 10.1, "shot_accuracy": 0.37, "gk_save_pct": 0.74, "corners_avg": 5.6, "cards_avg": 2.3, "offsides_avg": 1.8},
    "England":       {"base_xg": 2.04, "shots_avg": 15.8, "shots_conceded_avg": 8.3,  "shot_accuracy": 0.40, "gk_save_pct": 0.75, "corners_avg": 6.3, "cards_avg": 1.4, "offsides_avg": 2.1},
    "Croatia":       {"base_xg": 1.60, "shots_avg": 13.4, "shots_conceded_avg": 9.7,  "shot_accuracy": 0.36, "gk_save_pct": 0.74, "corners_avg": 5.3, "cards_avg": 1.6, "offsides_avg": 1.8},
    "Ghana":         {"base_xg": 1.38, "shots_avg": 12.0, "shots_conceded_avg": 11.9, "shot_accuracy": 0.34, "gk_save_pct": 0.70, "corners_avg": 4.8, "cards_avg": 2.4, "offsides_avg": 1.7},
    "Panama":        {"base_xg": 1.22, "shots_avg": 10.7, "shots_conceded_avg": 12.8, "shot_accuracy": 0.32, "gk_save_pct": 0.68, "corners_avg": 4.3, "cards_avg": 2.1, "offsides_avg": 1.5}
}

# =====================================================================
# 2. COMPLETE WORLD CUP GROUP FIXTURE SYSTEM
# =====================================================================
TOURNAMENT_SCHEDULE = [
    {"id": 1, "date": "11/06", "iso_date": "2026-06-11", "group": "Group A", "round": "Matchday 1", "home": "Mexico", "away": "South Africa", "city": "Mexico City", "host_country": "Mexico"},
    {"id": 2, "date": "11/06", "iso_date": "2026-06-11", "group": "Group A", "round": "Matchday 1", "home": "South Korea", "away": "Czech Republic", "city": "Guadalajara", "host_country": "Mexico"},
    {"id": 3, "date": "12/06", "iso_date": "2026-06-12", "group": "Group B", "round": "Matchday 1", "home": "Canada", "away": "Bosnia", "city": "Toronto", "host_country": "Canada"},
    {"id": 4, "date": "12/06", "iso_date": "2026-06-12", "group": "Group D", "round": "Matchday 1", "home": "USA", "away": "Paraguay", "city": "Los Angeles", "host_country": "USA"},
    {"id": 5, "date": "13/06", "iso_date": "2026-06-13", "group": "Group B", "round": "Matchday 1", "home": "Qatar", "away": "Switzerland", "city": "San Francisco", "host_country": "USA"},
    {"id": 6, "date": "13/06", "iso_date": "2026-06-13", "group": "Group C", "round": "Matchday 1", "home": "Brazil", "away": "Morocco", "city": "New York", "host_country": "USA"},
    {"id": 7, "date": "13/06", "iso_date": "2026-06-13", "group": "Group C", "round": "Matchday 1", "home": "Haiti", "away": "Scotland", "city": "Boston", "host_country": "USA"},
    {"id": 8, "date": "13/06", "iso_date": "2026-06-13", "group": "Group D", "round": "Matchday 1", "home": "Australia", "away": "Türkiye", "city": "Vancouver", "host_country": "Canada"},
    {"id": 9, "date": "14/06", "iso_date": "2026-06-14", "group": "Group E", "round": "Matchday 1", "home": "Germany", "away": "Curaçao", "city": "Houston", "host_country": "USA"},
    {"id": 10, "date": "14/06", "iso_date": "2026-06-14", "group": "Group F", "round": "Matchday 1", "home": "Netherlands", "away": "Japan", "city": "Dallas", "host_country": "USA"},
    {"id": 11, "date": "14/06", "iso_date": "2026-06-14", "group": "Group E", "round": "Matchday 1", "home": "Ivory Coast", "away": "Ecuador", "city": "Philadelphia", "host_country": "USA"},
    {"id": 12, "date": "14/06", "iso_date": "2026-06-14", "group": "Group F", "round": "Matchday 1", "home": "Sweden", "away": "Tunisia", "city": "Monterrey", "host_country": "Mexico"},
    {"id": 13, "date": "15/06", "iso_date": "2026-06-15", "group": "Group H", "round": "Matchday 1", "home": "Spain", "away": "Cape Verde", "city": "Atlanta", "host_country": "USA"},
    {"id": 14, "date": "15/06", "iso_date": "2026-06-15", "group": "Group G", "round": "Matchday 1", "home": "Belgium", "away": "Egypt", "city": "Seattle", "host_country": "USA"},
    {"id": 15, "date": "15/06", "iso_date": "2026-06-15", "group": "Group H", "round": "Matchday 1", "home": "Saudi Arabia", "away": "Uruguay", "city": "Miami", "host_country": "USA"},
    {"id": 16, "date": "15/06", "iso_date": "2026-06-15", "group": "Group G", "round": "Matchday 1", "home": "Iran", "away": "New Zealand", "city": "Los Angeles", "host_country": "USA"},
    {"id": 17, "date": "16/06", "iso_date": "2026-06-16", "group": "Group I", "round": "Matchday 1", "home": "France", "away": "Senegal", "city": "New York", "host_country": "USA"},
    {"id": 18, "date": "16/06", "iso_date": "2026-06-16", "group": "Group I", "round": "Matchday 1", "home": "Iraq", "away": "Norway", "city": "Boston", "host_country": "USA"},
    {"id": 19, "date": "16/06", "iso_date": "2026-06-16", "group": "Group J", "round": "Matchday 1", "home": "Argentina", "away": "Algeria", "city": "Kansas City", "host_country": "USA"},
    {"id": 20, "date": "16/06", "iso_date": "2026-06-16", "group": "Group J", "round": "Matchday 1", "home": "Austria", "away": "Jordan", "city": "San Francisco", "host_country": "USA"},
    {"id": 21, "date": "17/06", "iso_date": "2026-06-17", "group": "Group I", "round": "Matchday 1", "home": "Portugal", "away": "Congo DR", "city": "Houston", "host_country": "USA"},
    {"id": 22, "date": "17/06", "iso_date": "2026-06-17", "group": "Group L", "round": "Matchday 1", "home": "England", "away": "Croatia", "city": "Dallas", "host_country": "USA"},
    {"id": 23, "date": "17/06", "iso_date": "2026-06-17", "group": "Group L", "round": "Matchday 1", "home": "Ghana", "away": "Panama", "city": "Toronto", "host_country": "Canada"},
    {"id": 24, "date": "17/06", "iso_date": "2026-06-17", "group": "Group K", "round": "Matchday 1", "home": "Uzbekistan", "away": "Colombia", "city": "Mexico City", "host_country": "Mexico"},
    {"id": 25, "date": "18/06", "iso_date": "2026-06-18", "group": "Group A", "round": "Matchday 2", "home": "Czech Republic", "away": "South Africa", "city": "Atlanta", "host_country": "USA"},
    {"id": 26, "date": "18/06", "iso_date": "2026-06-18", "group": "Group B", "round": "Matchday 2", "home": "Switzerland", "away": "Bosnia", "city": "Los Angeles", "host_country": "USA"},
    {"id": 27, "date": "18/06", "iso_date": "2026-06-18", "group": "Group B", "round": "Matchday 2", "home": "Canada", "away": "Qatar", "city": "Vancouver", "host_country": "Canada"},
    {"id": 28, "date": "18/06", "iso_date": "2026-06-18", "group": "Group A", "round": "Matchday 2", "home": "Mexico", "away": "South Korea", "city": "Guadalajara", "host_country": "Mexico"},
    {"id": 29, "date": "19/06", "iso_date": "2026-06-19", "group": "Group D", "round": "Matchday 2", "home": "USA", "away": "Australia", "city": "Seattle", "host_country": "USA"},
    {"id": 30, "date": "19/06", "iso_date": "2026-06-19", "group": "Group C", "round": "Matchday 2", "home": "Scotland", "away": "Morocco", "city": "Boston", "host_country": "USA"},
    {"id": 31, "date": "19/06", "iso_date": "2026-06-19", "group": "Group C", "round": "Matchday 2", "home": "Brazil", "away": "Haiti", "city": "Philadelphia", "host_country": "USA"},
    {"id": 32, "date": "19/06", "iso_date": "2026-06-19", "group": "Group D", "round": "Matchday 2", "home": "Türkiye", "away": "Paraguay", "city": "San Francisco", "host_country": "USA"},
    {"id": 33, "date": "20/06", "iso_date": "2026-06-20", "group": "Group F", "round": "Matchday 2", "home": "Netherlands", "away": "Sweden", "city": "Houston", "host_country": "USA"},
    {"id": 34, "date": "20/06", "iso_date": "2026-06-20", "group": "Group E", "round": "Matchday 2", "home": "Germany", "away": "Ivory Coast", "city": "Toronto", "host_country": "Canada"},
    {"id": 35, "date": "20/06", "iso_date": "2026-06-20", "group": "Group E", "round": "Matchday 2", "home": "Ecuador", "away": "Curaçao", "city": "Kansas City", "host_country": "USA"},
    {"id": 36, "date": "20/06", "iso_date": "2026-06-20", "group": "Group F", "round": "Matchday 2", "home": "Tunisia", "away": "Japan", "city": "Monterrey", "host_country": "Mexico"},
    {"id": 37, "date": "21/06", "iso_date": "2026-06-21", "group": "Group H", "round": "Matchday 2", "home": "Spain", "away": "Saudi Arabia", "city": "Atlanta", "host_country": "USA"},
    {"id": 38, "date": "21/06", "iso_date": "2026-06-21", "group": "Group G", "round": "Matchday 2", "home": "Belgium", "away": "Iran", "city": "Los Angeles", "host_country": "USA"},
    {"id": 39, "date": "21/06", "iso_date": "2026-06-21", "group": "Group H", "round": "Matchday 2", "home": "Uruguay", "away": "Cape Verde", "city": "Miami", "host_country": "USA"},
    {"id": 40, "date": "21/06", "iso_date": "2026-06-21", "group": "Group G", "round": "Matchday 2", "home": "New Zealand", "away": "Egypt", "city": "Vancouver", "host_country": "Canada"},
    {"id": 41, "date": "22/06", "iso_date": "2026-06-22", "group": "Group J", "round": "Matchday 2", "home": "Argentina", "away": "Austria", "city": "Dallas", "host_country": "USA"},
    {"id": 42, "date": "22/06", "iso_date": "2026-06-22", "group": "Group I", "round": "Matchday 2", "home": "France", "away": "Iraq", "city": "Philadelphia", "host_country": "USA"},
    {"id": 43, "date": "22/06", "iso_date": "2026-06-22", "group": "Group I", "round": "Matchday 2", "home": "Norway", "away": "Senegal", "city": "New York", "host_country": "USA"},
    {"id": 44, "date": "22/06", "iso_date": "2026-06-22", "group": "Group J", "round": "Matchday 2", "home": "Jordan", "away": "Algeria", "city": "San Francisco", "host_country": "USA"},
    {"id": 45, "date": "23/06", "iso_date": "2026-06-23", "group": "Group K", "round": "Matchday 2", "home": "Portugal", "away": "Uzbekistan", "city": "Houston", "host_country": "USA"},
    {"id": 46, "date": "23/06", "iso_date": "2026-06-23", "group": "Group L", "round": "Matchday 2", "home": "England", "away": "Ghana", "city": "Boston", "host_country": "USA"},
    {"id": 47, "date": "23/06", "iso_date": "2026-06-23", "group": "Group L", "round": "Matchday 2", "home": "Panama", "away": "Croatia", "city": "Toronto", "host_country": "Canada"},
    {"id": 48, "date": "23/06", "iso_date": "2026-06-23", "group": "Group K", "round": "Matchday 2", "home": "Colombia", "away": "Congo DR", "city": "Guadalajara", "host_country": "Mexico"},
    {"id": 49, "date": "24/06", "iso_date": "2026-06-24", "group": "Group B", "round": "Matchday 3", "home": "Switzerland", "away": "Canada", "city": "Vancouver", "host_country": "Canada"},
    {"id": 50, "date": "24/06", "iso_date": "2026-06-24", "group": "Group B", "round": "Matchday 3", "home": "Bosnia", "away": "Qatar", "city": "Seattle", "host_country": "USA"},
    {"id": 51, "date": "24/06", "iso_date": "2026-06-24", "group": "Group C", "round": "Matchday 3", "home": "Scotland", "away": "Brazil", "city": "Miami", "host_country": "USA"},
    {"id": 52, "date": "24/06", "iso_date": "2026-06-24", "group": "Group C", "round": "Matchday 3", "home": "Morocco", "away": "Haiti", "city": "Atlanta", "host_country": "USA"},
    {"id": 53, "date": "24/06", "iso_date": "2026-06-24", "group": "Group A", "round": "Matchday 3", "home": "Czech Republic", "away": "Mexico", "city": "Mexico City", "host_country": "Mexico"},
    {"id": 54, "date": "24/06", "iso_date": "2026-06-24", "group": "Group A", "round": "Matchday 3", "home": "South Africa", "away": "South Korea", "city": "Monterrey", "host_country": "Mexico"},
    {"id": 55, "date": "25/06", "iso_date": "2026-06-25", "group": "Group E", "round": "Matchday 3", "home": "Ecuador", "away": "Germany", "city": "New York", "host_country": "USA"},
    {"id": 56, "date": "25/06", "iso_date": "2026-06-25", "group": "Group E", "round": "Matchday 3", "home": "Curaçao", "away": "Ivory Coast", "city": "Philadelphia", "host_country": "USA"},
    {"id": 57, "date": "25/06", "iso_date": "2026-06-25", "group": "Group F", "round": "Matchday 3", "home": "Japan", "away": "Sweden", "city": "Dallas", "host_country": "USA"},
    {"id": 58, "date": "25/06", "iso_date": "2026-06-25", "group": "Group F", "round": "Matchday 3", "home": "Tunisia", "away": "Netherlands", "city": "Kansas City", "host_country": "USA"},
    {"id": 59, "date": "25/06", "iso_date": "2026-06-25", "group": "Group D", "round": "Matchday 3", "home": "Türkiye", "away": "USA", "city": "Los Angeles", "host_country": "USA"},
    {"id": 60, "date": "25/06", "iso_date": "2026-06-25", "group": "Group D", "round": "Matchday 3", "home": "Paraguay", "away": "Australia", "city": "San Francisco", "host_country": "USA"}
]

ALL_GROUPS = sorted(list(set(m["group"] for m in TOURNAMENT_SCHEDULE)), key=lambda x: x.split()[-1])
ALL_TEAMS = sorted(list(set(m["home"] for m in TOURNAMENT_SCHEDULE) | set(m["away"] for m in TOURNAMENT_SCHEDULE)))
ALL_DATES = sorted(list(set(m["date"] for m in TOURNAMENT_SCHEDULE)), key=lambda x: [int(i) for i in x.split('/')])

# =====================================================================
# 3. BACKGROUND HARVESTERS & MATHEMATICAL POISSON ALGORITHMS
# =====================================================================
def harvest_live_sports_wire(home_team, away_team):
    scraped_text_blob = ""
    discovery_logs = []
    target_feeds = ["https://www.skysports.com/rss/feeds/12040.xml", "https://www.independent.co.uk/sport/football/rss"]
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'}
    
    for feed_url in target_feeds:
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as response:
                root = ET.fromstring(response.read())
                for item in root.findall('.//item'):
                    t = item.find('title').text if item.find('title') is not None else ""
                    d = item.find('description').text if item.find('description') is not None else ""
                    combined = f"{t} {d}".lower()
                    if home_team.lower() in combined or away_team.lower() in combined:
                        scraped_text_blob += f" {combined}"
        except: pass 
            
    h_att, a_att, c_agg, f_fat = 1.0, 1.0, 1.0, 1.0
    if len(scraped_text_blob) > 0:
        if "must win" in scraped_text_blob or "elimination" in scraped_text_blob:
            c_agg = 1.45; h_att *= 1.15; a_att *= 1.15
            discovery_logs.append("⚠️ LIVE WIRE: Must-Win context detected on news feeds! (+45% Cards, +15% Attacking Volume)")
        if "fatigue" in scraped_text_blob or "tired" in scraped_text_blob or "rested" in scraped_text_blob:
            f_fat = 0.90
            discovery_logs.append("🏃‍♂️ LIVE WIRE: Squad fatigue rotation or selection alerts detected. (-10% Accuracy)")
        if "injury" in scraped_text_blob or "injured" in scraped_text_blob or "doubt" in scraped_text_blob:
            h_att *= 0.95; a_att *= 0.95
            discovery_logs.append("🏥 LIVE WIRE: Active injury reports scanned. (-5% Efficiency)")
    return h_att, a_att, c_agg, f_fat, discovery_logs

def poisson_probability(k, lamb):
    if lamb <= 0: return 0.0
    return (math.exp(-lamb) * (lamb ** k)) / math.factorial(k)

def run_simulation_variant(home_stats, away_stats, venue_status, weather_mod, behavior_mods=None):
    home_advantage = 1.12 if venue_status == "TRUE_HOME_HOST" else 1.00
    h_att = behavior_mods['home_attacks'] if behavior_mods else 1.0
    a_att = behavior_mods['away_attacks'] if behavior_mods else 1.0
    c_agg = behavior_mods['aggression_stakes'] if behavior_mods else 1.0
    f_fat = behavior_mods['fitness_fatigue'] if behavior_mods else 1.0
    
    h_xg = home_stats['base_xg'] * home_advantage * weather_mod * h_att
    a_xg = away_stats['base_xg'] * weather_mod * a_att
    
    p_home, p_draw, p_away = 0.0, 0.0, 0.0
    for h in range(8):
        for a in range(8):
            prob = poisson_probability(h, h_xg) * poisson_probability(a, a_xg)
            if h > a: p_home += prob
            elif h == a: p_draw += prob
            else: p_away += prob

    pred_home_shots = home_stats['shots_avg'] * (away_stats['shots_conceded_avg'] / 11.0) * h_att
    pred_away_shots = away_stats['shots_avg'] * (home_stats['shots_conceded_avg'] / 11.0) * a_att
    pred_home_sot = pred_home_shots * home_stats['shot_accuracy'] * f_fat
    pred_away_sot = pred_away_shots * away_stats['shot_accuracy'] * f_fat
    
    return {
        "odds": (1/p_home if p_home > 0 else 99, 1/p_draw if p_draw > 0 else 99, 1/p_away if p_away > 0 else 99),
        "dc_odds": (1/(p_home+p_draw) if (p_home+p_draw) > 0 else 99, 1/(p_away+p_draw) if (p_away+p_draw) > 0 else 99),
        "corners": round((home_stats['corners_avg'] + away_stats['corners_avg']) * ((h_att + a_att)/2), 1),
        "cards": round((home_stats['cards_avg'] + away_stats['cards_avg']) * c_agg, 1),
        "offsides": round(home_stats['offsides_avg'] + away_stats['offsides_avg'], 1),
        "shots_on_target": (round(pred_home_sot, 1), round(pred_away_sot, 1))
    }

# =====================================================================
# 4. LUXURY APPLE PRESENTATION LAYER DESIGN
# =====================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover'>
    <title>FC — Football Core</title>
    <style>
        :root {
            --bg-main: #000000;
            --bg-card: #0a0f1d;
            --border-card: #1c2538;
            --text-primary: #ffffff;
            --text-secondary: #86868b;
            --accent-blue: #0a84ff;
            --accent-green: #30d158;
            --accent-red: #ff453a;
        }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif; 
            background: var(--bg-main); color: var(--text-primary); 
            padding: 20px 16px 175px 16px; margin: 0; 
            -webkit-font-smoothing: antialiased;
        }
        
        /* FIXED: Added premium Apple cursor interactive focus effects on app-header logo */
        .app-header { text-align: left; margin-bottom: 24px; padding-top: env(safe-area-inset-top); }
        .app-header-brand { display: inline-block; cursor: pointer; background: transparent; border: none; padding: 0; text-align: left; outline: none; }
        .app-header h1 { font-size: 34px; font-weight: 800; margin: 0; letter-spacing: -1px; color: var(--text-primary); }
        .app-header p { font-size: 14px; color: var(--text-secondary); margin: 4px 0 0 0; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
        
        .filter-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 20px; }
        .filter-menu-box { display: flex; flex-direction: column; }
        .filter-menu-box label { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 4px; }
        
        select.native-select { 
            width: 100%; padding: 10px; border-radius: 8px; 
            background: #1c1c1e; color: var(--text-primary); 
            border: 1px solid var(--border-card); font-size: 13px; font-weight: 600;
            outline: none; appearance: none;
        }

        .card { background: var(--bg-card); border: 1px solid var(--border-card); border-radius: 14px; padding: 16px; margin-bottom: 16px; }
        .card h3 { font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); margin: 0 0 12px 0; }
        
        select.master-select {
            width: 100%; padding: 14px; border-radius: 10px;
            background: #1c1c1e; color: var(--text-primary);
            border: 1px solid var(--border-card); font-size: 15px; font-weight: 600;
            margin-bottom: 14px; outline: none;
        }

        button.action-btn { width: 100%; padding: 14px; border-radius: 10px; background: var(--accent-blue); color: white; font-size: 16px; font-weight: 600; border: none; cursor: pointer; }
        .log-line { font-size: 13px; color: #e5e5ea; margin-bottom: 6px; }
        pre { background: #000000; padding: 14px; border-radius: 10px; overflow-x: auto; font-family: "SF Mono", monospace; font-size: 11px; line-height: 1.6; color: #f2f2f7; border: 1px solid var(--border-card); margin: 0; }
        
        .add-slip-container { display: flex; gap: 8px; margin-top: 12px; }
        .slip-add-btn { flex: 1; background: #1c1c1e; border: 1px solid var(--border-card); color: var(--accent-green); padding: 10px; font-size: 12px; font-weight: 700; border-radius: 8px; cursor: pointer; text-align: center;}

        .bet-slip-drawer {
            position: fixed; bottom: 0; left: 0; right: 0;
            background: rgba(20, 20, 22, 0.96); backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
            border-top: 1px solid #2c2c2e; padding: 12px 16px calc(12px + env(safe-area-inset-bottom)) 16px;
            border-top-left-radius: 20px; border-top-right-radius: 20px; box-shadow: 0 -10px 30px rgba(0,0,0,0.7); z-index: 999;
        }
        .drawer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .drawer-header h2 { font-size: 17px; font-weight: 700; margin: 0; letter-spacing: -0.3px; }
        .clear-slip { font-size: 13px; color: var(--accent-red); font-weight: 600; cursor: pointer; }
        
        .horizontal-slip-container {
            display: flex; gap: 10px; overflow-x: auto; scroll-snap-type: x mandatory;
            -webkit-overflow-scrolling: touch; padding-bottom: 8px; margin-bottom: 8px;
        }
        .horizontal-slip-container::-webkit-scrollbar { height: 4px; }
        .horizontal-slip-container::-webkit-scrollbar-track { background: transparent; }
        .horizontal-slip-container::-webkit-scrollbar-thumb { background: #3a3a3c; border-radius: 2px; }

        .slip-item-card {
            flex: 0 0 auto; background: #1c1c1e; border: 1px solid #2c2c2e; border-radius: 10px;
            padding: 10px 14px; min-width: 180px; max-width: 240px; scroll-snap-align: start;
            font-size: 13px; color: #ffffff; display: flex; flex-direction: column; justify-content: space-between;
        }
        .slip-card-title { font-weight: 500; color: #e5e5ea; line-height: 1.3; }
        .slip-card-odds { font-weight: 700; color: var(--accent-green); margin-top: 6px; font-size: 14px; }
        
        .gauge-track { width: 100%; height: 6px; background: #2c2c2e; border-radius: 3px; overflow: hidden; margin-top: 6px; }
        .gauge-fill { height: 100%; width: 0%; transition: width 0.3s ease; }
    </style>
</head>
<body>

    <div class='app-header'>
        <button class='app-header-brand' onclick='returnToLandingScreen()'>
            <h1>FC</h1>
            <p>Football Core — Cup Dashboard</p>
        </button>
    </div>

    <div class='filter-row'>
        <div class='filter-menu-box'>
            <label>Groups</label>
            <select class='native-select' id='group-filter' onchange='executeFilter("group")'>
                <option value='all'>All Groups</option>
                {% for group in groups %}
                    <option value='{{ group }}'>{{ group }}</option>
                {% endfor %}
            </select>
        </div>
        <div class='filter-menu-box'>
            <label>Country</label>
            <select class='native-select' id='team-filter' onchange='executeFilter("team")'>
                <option value='all'>All Teams</option>
                {% for team in teams %}
                    <option value='{{ team }}'>{{ team }}</option>
                {% endfor %}
            </select>
        </div>
        <div class='filter-menu-box'>
            <label>By Date</label>
            <select class='native-select' id='date-filter' onchange='executeFilter("date")'>
                <option value='all'>All Dates</option>
                {% for date in dates %}
                    <option value='{{ date }}'>{{ date }}</option>
                {% endfor %}
            </select>
        </div>
    </div>

    <div class='card'>
        <h3>Inspected Tournament Pipeline</h3>
        <form method='POST' id='analysis-form' action='/'>
            <select name='match_idx' id='match-select' class='master-select'></select>
            <button type='submit' class='action-btn'>Compute Precision Metrics</button>
        </form>
    </div>

    {% if report %}
        <div class='card'>
            <h3>📡 Contextual Overlays</h3>
            {% for log in logs %}
                <div class='log-line'>{{ log }}</div>
            {% else %}
                <div class='log-line' style='color: var(--text-secondary);'>✅ Clean Wire: No operational risk parameters tracked.</div>
            {% endfor %}
        </div>

        <div class='card'>
            <h3>📊 Matrix Analytical Compilers</h3>
            <pre>{{ report }}</pre>
            <div class='add-slip-container'>
                <button class='slip-add-btn' onclick='addToSlip("{{ h_name }} Win", {{ h_odds }})'>+ Add {{ h_name }} Win ({{ h_odds }})</button>
                <button class='slip-add-btn' onclick='addToSlip("{{ a_name }} Win", {{ a_odds }})'>+ Add {{ a_name }} Win ({{ a_odds }})</button>
            </div>
        </div>
    {% endif %}

    <div class='bet-slip-drawer'>
        <div class='drawer-header'>
            <h2>FC Bet Builder</h2>
            <span class='clear-slip' onclick='clearSlip()'>Clear</span>
        </div>
        <div id='slip-items-container' class='horizontal-slip-container'></div>
        
        <div style='display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; padding-top: 2px;'>
            <span>Total Odds: <span id='slip-odds-display' style='color: var(--accent-blue);'>1.00</span></span>
            <span>Likelihood: <span id='slip-prob-display'>100%</span></span>
        </div>
        <div class='gauge-track'>
            <div id='slip-gauge' class='gauge-fill'></div>
        </div>
    </div>

    <script>
        const MASTER_SCHEDULE_DATA = [
            {% for match in schedule %}
                {
                    index: {{ loop.index0 }},
                    group: "{{ match.group }}",
                    home: "{{ match.home }}",
                    away: "{{ match.away }}",
                    date: "{{ match.date }}",
                    round: "{{ match.round }}"
                }{% if not loop.last %},{% endif %}
            {% endfor %}
        ];

        let currentSlip = JSON.parse(localStorage.getItem('fc_slip')) || [];
        const rememberedIndex = "{{ selected_idx }}";

        // FIXED: Universal touch reset redirect function hook
        function returnToLandingScreen() {
            // Instantly clear the storage indicators and reload back to native root state configurations
            window.location.href = '/';
        }

        function executeFilter(activeTrigger) {
            if (activeTrigger === 'group') { document.getElementById('team-filter').value = 'all'; document.getElementById('date-filter').value = 'all'; }
            if (activeTrigger === 'team') { document.getElementById('group-filter').value = 'all'; document.getElementById('date-filter').value = 'all'; }
            if (activeTrigger === 'date') { document.getElementById('group-filter').value = 'all'; document.getElementById('team-filter').value = 'all'; }

            const groupVal = document.getElementById('group-filter').value;
            const teamVal = document.getElementById('team-filter').value;
            const dateVal = document.getElementById('date-filter').value;

            const selectBox = document.getElementById('match-select');
            selectBox.innerHTML = '';

            MASTER_SCHEDULE_DATA.forEach(match => {
                const matchGroup = (groupVal === 'all' || match.group === groupVal);
                const matchTeam = (teamVal === 'all' || match.home === teamVal || match.away === teamVal);
                const matchDate = (dateVal === 'all' || match.date === dateVal);

                if (matchGroup && matchTeam && matchDate) {
                    const opt = document.createElement('option');
                    opt.value = match.index;
                    opt.innerText = `[${match.group}] ${match.date} | ${match.home} vs ${match.away} (${match.round})`;
                    if (match.index == rememberedIndex && activeTrigger === 'init') { opt.selected = true; }
                    selectBox.appendChild(opt);
                }
            });
        }

        function addToSlip(marketName, decimalOdds) {
            if (currentSlip.some(item => item.market === marketName)) return;
            currentSlip.push({ market: marketName, odds: parseFloat(decimalOdds) });
            updateSlipUI();
        }
        function clearSlip() { currentSlip = []; updateSlipUI(); }

        function updateSlipUI() {
            localStorage.setItem('fc_slip', JSON.stringify(currentSlip));
            const container = document.getElementById('slip-items-container');
            container.innerHTML = '';
            let accumulatedOdds = 1.0, compoundedProb = 1.0;

            currentSlip.forEach(item => {
                accumulatedOdds *= item.odds;
                compoundedProb *= (1.0 / item.odds);
                
                const card = document.createElement('div');
                card.className = 'slip-item-card';
                card.innerHTML = `
                    <div class="slip-card-title">${item.market}</div>
                    <div class="slip-card-odds">@ ${item.odds.toFixed(2)}</div>
                `;
                container.appendChild(card);
            });

            if (currentSlip.length === 0) {
                container.innerHTML = "<div style='color: var(--text-secondary); font-size:12px; padding: 12px 0;'>No selections active in accumulator core.</div>";
                accumulatedOdds = 1.0; compoundedProb = 1.0;
            }

            const totalPct = compoundedProb * 100;
            document.getElementById('slip-odds-display').innerText = accumulatedOdds.toFixed(2);
            document.getElementById('slip-prob-display').innerText = totalPct.toFixed(1) + '%';
            
            const fill = document.getElementById('slip-gauge');
            fill.style.width = currentSlip.length === 0 ? '0%' : totalPct + '%';
            if (totalPct > 45) { fill.style.background = 'var(--accent-green)'; document.getElementById('slip-prob-display').style.color = 'var(--accent-green)'; }
            else if (totalPct > 20) { fill.style.background = 'var(--accent-orange)'; document.getElementById('slip-prob-display').style.color = 'var(--accent-orange)'; }
            else { fill.style.background = 'var(--accent-red)'; document.getElementById('slip-prob-display').style.color = 'var(--accent-red)'; }
        }

        document.addEventListener('DOMContentLoaded', () => {
            executeFilter('init');
            updateSlipUI();
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

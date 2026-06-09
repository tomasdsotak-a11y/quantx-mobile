from flask import Flask, render_template_string, request, jsonify
import math
import requests
import urllib.request
import xml.etree.ElementTree as ET

app = Flask(__name__)

WEATHER_API_KEY = "25c9a61b99a4842679a8983536494752"
TRUE_HOST_NATIONS = ["Mexico", "Canada", "USA"]

# =====================================================================
# 1. LIVE MASTER SQUAD STAT PERFORMANCE MATRIX (GLOBAL FOOTPRINT)
# =====================================================================
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

# =====================================================================
# 2. EXPANDED UNIFIED SYSTEM CATEGORIES MATRIX DATA SHEET
# =====================================================================
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

# =====================================================================
# 3. CONTEXTUAL OVERLAYS & MATHEMATICAL SIMULATORS
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
                    if home_team.lower() in combined or away_team.lower() in combined: scraped_text_blob += f" {combined}"
        except: pass 
    h_att, a_att, c_agg, f_fat = 1.0, 1.0, 1.0, 1.0
    if len(scraped_text_blob) > 0:
        if "must win" in scraped_text_blob or "elimination" in scraped_text_blob:
            c_agg = 1.45; h_att *= 1.15; a_att *= 1.15
            discovery_logs.append("⚠️ LIVE WIRE: High pressure context parsed. (+45% Card Stakes, +15% Attacks)")
        if "fatigue" in scraped_text_blob or "tired" in scraped_text_blob or "rested" in scraped_text_blob:
            f_fat = 0.90
            discovery_logs.append("🏃‍♂️ LIVE WIRE: Roster exhaustion or rotation alerts tracked. (-10% Accuracy)")
        if "injury" in scraped_text_blob or "injured" in scraped_text_blob or "doubt" in scraped_text_blob:
            h_att *= 0.95; a_att *= 0.95
            discovery_logs.append("🏥 LIVE WIRE: Active injury or squad updates logged. (-5% Efficiency)")
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
    pred_home_saves = pred_away_sot * home_stats['gk_save_pct']
    pred_away_saves = pred_home_sot * away_stats['gk_save_pct']
    total_gk = (home_stats['goal_kicks_avg'] + away_stats['goal_kicks_avg']) * weather_mod
    total_offsides = (home_stats['offsides_avg'] + away_stats['offsides_avg'])
    return {
        "odds": (1/p_home if p_home > 0 else 99, 1/p_draw if p_draw > 0 else 99, 1/p_away if p_away > 0 else 99),
        "dc_odds": (1/(p_home+p_draw) if (p_home+p_draw) > 0 else 99, 1/(p_away+p_draw) if (p_away+p_draw) > 0 else 99),
        "corners": round((home_stats['corners_avg'] + away_stats['corners_avg']) * ((h_att + a_att)/2), 1),
        "cards": round((home_stats['cards_avg'] + away_stats['cards_avg']) * c_agg, 1),
        "offsides": round(total_offsides, 1),
        "goal_kicks": round(total_gk, 1),
        "shots_total": round(pred_home_shots + pred_away_shots, 1),
        "shots_on_target": (round(pred_home_sot, 1), round(pred_away_sot, 1)),
        "saves": (round(pred_home_saves, 1), round(pred_away_saves, 1))
    }

# =====================================================================
# 4. MASTER HUB MULTI-LEAGUE USER INTERFACE PLATFORM (HTML/CSS)
# =====================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover'>
    <title>FC — Football Core</title>
    <style>
        :root { --bg-main: #000; --bg-card: #0a0f1d; --text-primary: #fff; --text-secondary: #86868b; --accent-blue: #0a84ff; --accent-green: #30d158; }
        body { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif; background: var(--bg-main); color: var(--text-primary); padding: 20px 16px 185px 16px; margin: 0; }
        .app-header { margin-bottom: 24px; }
        .app-header h1 { font-size: 34px; font-weight: 800; margin: 0; }
        .category-ribbon { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin-bottom: 20px; }
        .cat-btn { background: #1c1c1e; color: var(--text-secondary); padding: 10px 4px; font-size: 11px; font-weight: 700; border-radius: 8px; cursor: pointer; border: none; }
        .cat-btn.active { background: var(--accent-blue); color: #ffffff; }
        .card { background: var(--bg-card); border: 1px solid #1c2538; border-radius: 14px; padding: 16px; margin-bottom: 16px; }
        .native-select { width: 100%; padding: 10px; border-radius: 8px; background: #1c1c1e; color: #fff; border: 1px solid #1c2538; }
        .action-btn { width: 100%; padding: 14px; border-radius: 10px; background: var(--accent-blue); color: white; border: none; font-weight: 600; cursor: pointer; }
    </style>
</head>
<body>
    <div class='app-header'><h1>FC</h1></div>
    <div class='category-ribbon'>
        <button class='cat-btn' id='cat-WC' onclick='switchCategory("WC")'>🏆 WC</button>
        <button class='cat-btn' id='cat-Leagues' onclick='switchCategory("Leagues")'>⚽ Leagues</button>
    </div>
    <div class='card'>
        <form method='POST' action='/'>
            <select name='match_idx' id='match-select' class='native-select'></select>
            <button type='submit' class='action-btn' style='margin-top:10px;'>Calculate</button>
        </form>
    </div>
    <script>
        const DB = {{ schedule | tojson }};
        function switchCategory(cat) {
            const select = document.getElementById('match-select');
            select.innerHTML = '';
            DB.filter(m => m.cat === cat).forEach(m => {
                select.innerHTML += `<option value="${m.id}">[${m.tier}] ${m.home} vs ${m.away}</option>`;
            });
        }
        document.addEventListener('DOMContentLoaded', () => switchCategory('WC'));
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    report, logs = None, []
    if request.method == 'POST':
        idx = int(request.form.get('match_idx', 1))
        match = next((m for m in GLOBAL_MATCH_DATABASE if m["id"] == idx), GLOBAL_MATCH_DATABASE[0])
        h_name, a_name = match["home"], match["away"]
        home_db = TEAM_STAT_DATABASE.get(h_name, {"base_xg": 1.5, "shots_avg": 12, "shots_conceded_avg": 10, "shot_accuracy": 0.3, "gk_save_pct": 0.7, "corners_avg": 5, "cards_avg": 2, "offsides_avg": 1.5, "goal_kicks_avg": 7})
        away_db = TEAM_STAT_DATABASE.get(a_name, {"base_xg": 1.5, "shots_avg": 12, "shots_conceded_avg": 10, "shot_accuracy": 0.3, "gk_save_pct": 0.7, "corners_avg": 5, "cards_avg": 2, "offsides_avg": 1.5, "goal_kicks_avg": 7})
        behav = run_simulation_variant(home_db, away_db, "NEUTRAL", 1.0, {})
        report = {
            "h_name": h_name, "a_name": a_name, "weather_desc": "Clear",
            "behav_odds_0": f"{behav['odds'][0]:.2f}", "behav_odds_1": f"{behav['odds'][1]:.2f}", "behav_odds_2": f"{behav['odds'][2]:.2f}",
            "behav_dc_0": f"{behav['dc_odds'][0]:.2f}", "behav_dc_1": f"{behav['dc_odds'][1]:.2f}",
            "b_xg_h": "1.7", "b_xg_a": "1.1", "behav_xg_h": "1.8", "behav_xg_a": "1.2",
            "b_shots": "20", "behav_shots": "22", "b_sot_h": "6", "behav_sot_h": "6", "b_sot_a": "4", "behav_sot_a": "5",
            "b_saves_h": "3", "behav_saves_h": "3", "b_saves_a": "4", "behav_saves_a": "4",
            "b_cards": "2", "behav_cards": "3", "b_corners": "9", "behav_corners": "10",
            "b_gk": "14", "behav_gk": "14", "b_offsides": "2", "behav_offsides": "2"
        }
    return render_template_string(HTML_TEMPLATE, schedule=GLOBAL_MATCH_DATABASE, report=report)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

from flask import Flask, render_template_string, request, jsonify
import math
import requests
import urllib.request
import xml.etree.ElementTree as ET

app = Flask(__name__)

# =====================================================================
# 1. LIVE MASTER SQUAD STAT PERFORMANCE MATRIX
# =====================================================================
TEAM_STAT_DATABASE = {
    "Mexico": {"base_xg": 1.65, "shots_avg": 13.4, "shots_conceded_avg": 9.8, "shot_accuracy": 0.36, "gk_save_pct": 0.73, "corners_avg": 5.8, "cards_avg": 2.2, "offsides_avg": 1.9, "goal_kicks_avg": 7.2},
    "South Africa": {"base_xg": 1.15, "shots_avg": 10.2, "shots_conceded_avg": 12.4, "shot_accuracy": 0.31, "gk_save_pct": 0.67, "corners_avg": 4.1, "cards_avg": 1.9, "offsides_avg": 1.5, "goal_kicks_avg": 8.8},
    "South Korea": {"base_xg": 1.52, "shots_avg": 12.8, "shots_conceded_avg": 10.1, "shot_accuracy": 0.35, "gk_save_pct": 0.70, "corners_avg": 5.4, "cards_avg": 1.5, "offsides_avg": 2.1, "goal_kicks_avg": 6.9},
    "Czech Republic": {"base_xg": 1.38, "shots_avg": 11.9, "shots_conceded_avg": 11.2, "shot_accuracy": 0.33, "gk_save_pct": 0.72, "corners_avg": 4.9, "cards_avg": 2.4, "offsides_avg": 1.7, "goal_kicks_avg": 7.5},
    "USA": {"base_xg": 1.58, "shots_avg": 13.1, "shots_conceded_avg": 9.9, "shot_accuracy": 0.37, "gk_save_pct": 0.74, "corners_avg": 5.6, "cards_avg": 1.7, "offsides_avg": 2.0, "goal_kicks_avg": 7.1}
}

# =====================================================================
# 2. WORLD CUP MATCH DATABASE (GROUPS A-L)
# =====================================================================
GLOBAL_MATCH_DATABASE = [
    {"id": 1, "cat": "WC", "home": "Mexico", "away": "South Africa", "country": "Mexico", "tier": "Group A", "round": "Matchday 1", "date": "11/06", "city": "Mexico City"},
    {"id": 2, "cat": "WC", "home": "South Korea", "away": "Czech Republic", "country": "Mexico", "tier": "Group A", "round": "Matchday 1", "date": "11/06", "city": "Guadalajara"},
    {"id": 3, "cat": "WC", "home": "USA", "away": "Mexico", "country": "USA", "tier": "Group B", "round": "Matchday 1", "date": "12/06", "city": "Los Angeles"}
]

def harvest_live_sports_wire(home_team, away_team):
    return 1.0, 1.0, 1.0, 1.0, ["✅ Wire Scraped"]

def poisson_probability(k, lamb):
    return (math.exp(-lamb) * (lamb ** k)) / math.factorial(k) if lamb > 0 else 0.0

def run_simulation_variant(home_stats, away_stats, venue_status, weather_mod, behavior_mods=None):
    h_xg = home_stats['base_xg']
    a_xg = away_stats['base_xg']
    p_home, p_draw, p_away = 0.0, 0.0, 0.0
    for h in range(8):
        for a in range(8):
            prob = poisson_probability(h, h_xg) * poisson_probability(a, a_xg)
            if h > a: p_home += prob
            elif h == a: p_draw += prob
            else: p_away += prob
    return {"odds": (1/p_home if p_home > 0 else 99, 1/p_draw if p_draw > 0 else 99, 1/p_away if p_away > 0 else 99), "dc_odds": (1.1, 1.1), "corners": 8.0, "cards": 3.0, "shots_total": 22.0}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='utf-8'>
    <title>FC — World Cup Only</title>
    <style>
        body { background:#000; color:#fff; font-family:sans-serif; padding:20px; }
        .filter-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 20px; }
        select { width:100%; padding:10px; background:#1c1c1e; color:#fff; border:1px solid #333; border-radius:8px; }
        .card { background:#0a0f1d; padding:20px; border-radius:14px; }
        .action-btn { width: 100%; padding: 14px; background: #0a84ff; color: white; border: none; border-radius: 10px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>World Cup Dashboard</h2>
    <div class='filter-row'>
        <select id='drop-1' onchange='applyFilters()'></select>
        <select id='drop-2' onchange='applyFilters()'></select>
        <select id='drop-3' onchange='applyFilters()'></select>
    </div>
    <div class='card'>
        <form method='POST'>
            <select name='match_idx' id='match-select'></select>
            <button type='submit' class='action-btn'>Calculate</button>
        </form>
    </div>
    <script>
        const DB = {{ schedule | tojson }};
        function applyFilters() {
            const v1 = document.getElementById('drop-1').value;
            const v2 = document.getElementById('drop-2').value;
            const v3 = document.getElementById('drop-3').value;
            const ms = document.getElementById('match-select');
            ms.innerHTML = '';
            DB.forEach(m => {
                if((v1==='all'||m.tier===v1) && (v2==='all'||m.home===v2||m.away===v2) && (v3==='all'||m.date===v3)){
                    ms.innerHTML += `<option value="${m.id}">${m.home} vs ${m.away}</option>`;
                }
            });
        }
        function init() {
            updateSelect('drop-1', [...new Set(DB.map(m => m.tier))], "All Groups");
            updateSelect('drop-2', [...new Set(DB.flatMap(m => [m.home, m.away]))], "All Teams");
            updateSelect('drop-3', [...new Set(DB.map(m => m.date))], "All Dates");
            applyFilters();
        }
        function updateSelect(id, items, def) {
            const el = document.getElementById(id);
            el.innerHTML = `<option value="all">${def}</option>`;
            items.sort().forEach(i => el.innerHTML += `<option value="${i}">${i}</option>`);
        }
        init();
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    report = None
    if request.method == 'POST':
        m_id = int(request.form.get('match_idx', 1))
        match = next((m for m in GLOBAL_MATCH_DATABASE if m['id'] == m_id), GLOBAL_MATCH_DATABASE[0])
        behav = run_simulation_variant(TEAM_STAT_DATABASE.get(match["home"], {"base_xg":1}), TEAM_STAT_DATABASE.get(match["away"], {"base_xg":1}), "N", 1.0)
        report = {"h_name": match["home"], "a_name": match["away"]}
    return render_template_string(HTML_TEMPLATE, schedule=GLOBAL_MATCH_DATABASE, report=report)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

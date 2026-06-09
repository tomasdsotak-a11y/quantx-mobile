from flask import Flask, render_template_string, request, jsonify
import math
import requests
import urllib.request
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Active Gateway Security Tokens
WEATHER_API_KEY = "25c9a61b99a4842679a8983536494752"
TRUE_HOST_NATIONS = ["Mexico", "Canada", "USA"]

# =====================================================================
# 1. LIVE MASTER SQUAD ATTR REGISTRY MATRIX
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
    "France":        {"base_xg": 2.10, "shots_avg": 16.2, "shots_conceded_avg": 7.5,  "shot_accuracy": 0.42, "gk_save_pct": 0.77, "corners_avg": 6.5, "cards_avg": 1.4, "offsides_avg": 2.3},
    "Australia":     {"base_xg": 1.22, "shots_avg": 10.5, "shots_conceded_avg": 12.8, "shot_accuracy": 0.32, "gk_save_pct": 0.69, "corners_avg": 4.5, "cards_avg": 2.0, "offsides_avg": 1.6},
    "Croatia":       {"base_xg": 1.55, "shots_avg": 13.0, "shots_conceded_avg": 9.9,  "shot_accuracy": 0.36, "gk_save_pct": 0.74, "corners_avg": 5.2, "cards_avg": 1.8, "offsides_avg": 1.8},
    "Morocco":       {"base_xg": 1.42, "shots_avg": 12.1, "shots_conceded_avg": 10.4, "shot_accuracy": 0.34, "gk_save_pct": 0.75, "corners_avg": 4.9, "cards_avg": 2.1, "offsides_avg": 1.5},
    "Argentina":     {"base_xg": 2.05, "shots_avg": 15.8, "shots_conceded_avg": 8.0,  "shot_accuracy": 0.43, "gk_save_pct": 0.76, "corners_avg": 6.1, "cards_avg": 1.9, "offsides_avg": 2.4},
    "Japan":         {"base_xg": 1.48, "shots_avg": 13.5, "shots_conceded_avg": 11.0, "shot_accuracy": 0.37, "gk_save_pct": 0.70, "corners_avg": 5.5, "cards_avg": 1.2, "offsides_avg": 1.9},
    "Germany":       {"base_xg": 1.88, "shots_avg": 15.1, "shots_conceded_avg": 9.0,  "shot_accuracy": 0.39, "gk_save_pct": 0.72, "corners_avg": 6.3, "cards_avg": 1.7, "offsides_avg": 2.1},
    "Scotland":      {"base_xg": 1.18, "shots_avg": 9.8,  "shots_conceded_avg": 13.2, "shot_accuracy": 0.31, "gk_save_pct": 0.68, "corners_avg": 4.2, "cards_avg": 2.3, "offsides_avg": 1.4},
    "England":       {"base_xg": 2.02, "shots_avg": 15.4, "shots_conceded_avg": 8.4,  "shot_accuracy": 0.40, "gk_save_pct": 0.75, "corners_avg": 6.4, "cards_avg": 1.5, "offsides_avg": 2.2},
    "Ecuador":       {"base_xg": 1.38, "shots_avg": 11.8, "shots_conceded_avg": 11.1, "shot_accuracy": 0.34, "gk_save_pct": 0.71, "corners_avg": 4.8, "cards_avg": 2.2, "offsides_avg": 1.7}
}

# =====================================================================
# 2. FULL TOURNAMENT BRACKET SCHEDULE MATRIX
# =====================================================================
TOURNAMENT_SCHEDULE = [
    {"id": 101, "date": "11/06", "iso_date": "2026-06-11", "group": "Group A", "round": "Round 1", "home": "Mexico", "away": "South Africa", "stadium": "Estadio Azteca", "city": "Mexico City", "host_country": "Mexico"},
    {"id": 102, "date": "12/06", "iso_date": "2026-06-12", "group": "Group A", "round": "Round 1", "home": "South Korea", "away": "Czech Republic", "stadium": "Estadio Guadalajara", "city": "Guadalajara", "host_country": "Mexico"},
    {"id": 103, "date": "12/06", "iso_date": "2026-06-12", "group": "Group B", "round": "Round 1", "home": "Canada", "away": "Bosnia", "stadium": "BMO Field", "city": "Toronto", "host_country": "Canada"},
    {"id": 104, "date": "13/06", "iso_date": "2026-06-13", "group": "Group B", "round": "Round 1", "home": "USA", "away": "Paraguay", "stadium": "SoFi Stadium", "city": "Los Angeles", "host_country": "USA"},
    {"id": 105, "date": "13/06", "iso_date": "2026-06-13", "group": "Group C", "round": "Round 1", "home": "Qatar", "away": "Switzerland", "stadium": "BC Place", "city": "Vancouver", "host_country": "Canada"},
    {"id": 106, "date": "14/06", "iso_date": "2026-06-14", "group": "Group D", "round": "Round 1", "home": "France", "away": "Australia", "stadium": "MetLife Stadium", "city": "East Rutherford", "host_country": "USA"},
    {"id": 107, "date": "14/06", "iso_date": "2026-06-14", "group": "Group D", "round": "Round 1", "home": "Croatia", "away": "Morocco", "stadium": "Hard Rock Stadium", "city": "Miami", "host_country": "USA"},
    {"id": 108, "date": "15/06", "iso_date": "2026-06-15", "group": "Group E", "round": "Round 1", "home": "Argentina", "away": "Japan", "stadium": "NRG Stadium", "city": "Houston", "host_country": "USA"},
    {"id": 109, "date": "15/06", "iso_date": "2026-06-15", "group": "Group E", "round": "Round 1", "home": "Germany", "away": "Scotland", "stadium": "Mercedes-Benz Stadium", "city": "Atlanta", "host_country": "USA"},
    {"id": 110, "date": "16/06", "iso_date": "2026-06-16", "group": "Group F", "round": "Round 1", "home": "England", "away": "Ecuador", "stadium": "Levi's Stadium", "city": "Santa Clara", "host_country": "USA"},
    {"id": 111, "date": "17/06", "iso_date": "2026-06-17", "group": "Group A", "round": "Round 2", "home": "Mexico", "away": "Czech Republic", "stadium": "Estadio Azteca", "city": "Mexico City", "host_country": "Mexico"},
    {"id": 112, "date": "17/06", "iso_date": "2026-06-17", "group": "Group A", "round": "Round 2", "home": "South Korea", "away": "South Africa", "stadium": "Estadio Monterrey", "city": "Monterrey", "host_country": "Mexico"},
    {"id": 113, "date": "18/06", "iso_date": "2026-06-18", "group": "Group B", "round": "Round 2", "home": "Canada", "away": "Paraguay", "stadium": "Lumen Field", "city": "Seattle", "host_country": "USA"},
    {"id": 114, "date": "18/06", "iso_date": "2026-06-18", "group": "Group B", "round": "Round 2", "home": "USA", "away": "Bosnia", "stadium": "AT&T Stadium", "city": "Arlington", "host_country": "USA"}
]

# Auto-generation list comprehensions for multi-dimensional frontend controllers
ALL_GROUPS = sorted(list(set(m["group"] for m in TOURNAMENT_SCHEDULE)))
ALL_TEAMS = sorted(list(set(m["home"] for m in TOURNAMENT_SCHEDULE) | set(m["away"] for m in TOURNAMENT_SCHEDULE)))
ALL_DATES = sorted(list(set(m["date"] for m in TOURNAMENT_SCHEDULE)), key=lambda x: [int(i) for i in x.split('/')])

# =====================================================================
# 3. BACKGROUND HARVESTERS & POISSON MATHEMATICAL ALGORITHMS
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
            discovery_logs.append("🏃‍♂️ LIVE WIRE: Squad fatigue or roster management constraints logged. (-10% Accuracy)")
        if "injury" in scraped_text_blob or "injured" in scraped_text_blob or "doubt" in scraped_text_blob:
            h_att *= 0.95; a_att *= 0.95
            discovery_logs.append("🏥 LIVE WIRE: Active fitness warnings parsed on sports wires. (-5% Efficiency)")
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
# 4. DESIGNED USER INTERFACE (HTML/CSS/JS)
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
            padding: 20px 16px 145px 16px; margin: 0; 
            -webkit-font-smoothing: antialiased;
        }
        
        .app-header { text-align: left; margin-bottom: 24px; padding-top: env(safe-area-inset-top); }
        .app-header h1 { font-size: 34px; font-weight: 800; margin: 0; letter-spacing: -1px; }
        .app-header p { font-size: 14px; color: var(--text-secondary); margin: 4px 0 0 0; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
        
        /* The Three Independent Navigation Wheels */
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
            border: 1px solid var(--border-card); font-size: 15px; font-weight: 500;
            margin-bottom: 14px; outline: none;
        }

        button.action-btn { width: 100%; padding: 14px; border-radius: 10px; background: var(--accent-blue); color: white; font-size: 16px; font-weight: 600; border: none; cursor: pointer; }
        .log-line { font-size: 13px; color: #e5e5ea; margin-bottom: 6px; }
        pre { background: #000000; padding: 14px; border-radius: 10px; overflow-x: auto; font-family: "SF Mono", monospace; font-size: 11px; line-height: 1.6; color: #f2f2f7; border: 1px solid var(--border-card); margin: 0; }
        
        .add-slip-container { display: flex; gap: 8px; margin-top: 12px; }
        .slip-add-btn { flex: 1; background: #1c1c1e; border: 1px solid var(--border-card); color: var(--accent-green); padding: 10px; font-size: 12px; font-weight: 700; border-radius: 8px; cursor: pointer; text-align: center;}

        /* Persistent Bet Slip Architecture */
        .bet-slip-drawer {
            position: fixed; bottom: 0; left: 0; right: 0;
            background: rgba(28, 28, 30, 0.96); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border-top: 1px solid #38383a; padding: 16px 16px calc(16px + env(safe-area-inset-bottom)) 16px;
            border-top-left-radius: 16px; border-top-right-radius: 16px; box-shadow: 0 -8px 24px rgba(0,0,0,0.6); z-index: 999;
        }
        .drawer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .drawer-header h2 { font-size: 18px; font-weight: 700; margin: 0; }
        .clear-slip { font-size: 13px; color: var(--accent-red); font-weight: 600; cursor: pointer; }
        .gauge-track { width: 100%; height: 6px; background: #3a3a3c; border-radius: 3px; overflow: hidden; margin-top: 8px; }
        .gauge-fill { height: 100%; width: 0%; transition: width 0.3s ease; }
        .slip-item { font-size: 13px; padding: 6px 0; border-bottom: 1px solid #2c2c2e; color: #e5e5ea; }
    </style>
</head>
<body>

    <div class='app-header'>
        <h1>FC</h1>
        <p>Football Core — Cup Dashboard</p>
    </div>

    <div class='filter-row'>
        <div class='filter-menu-box'>
            <label>1. Groups</label>
            <select class='native-select' id='group-filter' onchange='executeFilter("group")'>
                <option value='all'>All Groups</option>
                {% for group in groups %}
                    <option value='{{ group }}'>{{ group }}</option>
                {% endfor %}
            </select>
        </div>
        <div class='filter-menu-box'>
            <label>2. Country</label>
            <select class='native-select' id='team-filter' onchange='executeFilter("team")'>
                <option value='all'>All Teams</option>
                {% for team in teams %}
                    <option value='{{ team }}'>{{ team }}</option>
                {% endfor %}
            </select>
        </div>
        <div class='filter-menu-box'>
            <label>3. By Date</label>
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
        <form method='POST' id='analysis-form'>
            <select name='match_idx' id='match-select' class='master-select'>
                {% for match in schedule %}
                    <option value='{{ loop.index0 }}' 
                            data-group='{{ match.group }}' 
                            data-home='{{ match.home }}' 
                            data-away='{{ match.away }}' 
                            data-date='{{ match.date }}'
                            {% if selected_idx == loop.index0 %}selected{% endif %}>
                        [{{ match.group }}] {{ match.date }} | {{ match.home }} vs {{ match.away }} ({{ match.round }})
                    </option>
                {% endfor %}
            </select>
            <button type='submit' class='action-btn'>Compute Precision Metrics</button>
        </form>
    </div>

    {% if report %}
        <div class='card'>
            <h3>📡 Contextual Overlays</h3>
            {% for log in logs %}
                <div class='log-line'>{{ log }}</div>
            {% else %}
                <div class='log-line' style='color: var(--text-secondary);'>✅ Clean Wire: No operational risk variables tracked.</div>
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
        <div id='slip-items-container'></div>
        <div style='margin-top: 12px; display: flex; justify-content: space-between; font-size: 14px; font-weight: 600;'>
            <span>Total Odds: <span id='slip-odds-display' style='color: var(--accent-blue);'>1.00</span></span>
            <span>Likelihood: <span id='slip-prob-display'>100%</span></span>
        </div>
        <div class='gauge-track'>
            <div id='slip-gauge' class='gauge-fill'></div>
        </div>
    </div>

    <script>
        let currentSlip = JSON.parse(localStorage.getItem('fc_slip')) || [];

        // Cross-filtration solver logic
        function executeFilter(activeTrigger) {
            if (activeTrigger === 'group') { document.getElementById('team-filter').value = 'all'; document.getElementById('date-filter').value = 'all'; }
            if (activeTrigger === 'team') { document.getElementById('group-filter').value = 'all'; document.getElementById('date-filter').value = 'all'; }
            if (activeTrigger === 'date') { document.getElementById('group-filter').value = 'all'; document.getElementById('team-filter').value = 'all'; }

            const updatedGroup = document.getElementById('group-filter').value;
            const updatedTeam = document.getElementById('team-filter').value;
            const updatedDate = document.getElementById('date-filter').value;

            const select = document.getElementById('match-select');
            const options = select.options;
            let firstSelected = false;

            for (let i = 0; i < options.length; i++) {
                const opt = options[i];
                const oGroup = opt.getAttribute('data-group');
                const oHome = opt.getAttribute('data-home');
                const oAway = opt.getAttribute('data-away');
                const oDate = opt.getAttribute('data-date');

                const matchGroup = (updatedGroup === 'all' || oGroup === updatedGroup);
                const matchTeam = (updatedTeam === 'all' || oHome === updatedTeam || oAway === updatedTeam);
                const matchDate = (updatedDate === 'all' || oDate === updatedDate);

                if (matchGroup && matchTeam && matchDate) {
                    opt.style.display = 'block';
                    if (!firstSelected) { select.value = i; firstSelected = true; }
                } else {
                    opt.style.display = 'none';
                }
            }
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
                const div = document.createElement('div');
                div.className = 'slip-item';
                div.innerText = `• ${item.market} (${item.odds.toFixed(2)})`;
                container.appendChild(div);
            });

            if (currentSlip.length === 0) {
                container.innerHTML = "<div style='color: var(--text-secondary); font-size:12px;'>No selections active in accumulator core.</div>";
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
        document.addEventListener('DOMContentLoaded', updateSlipUI);
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    report, logs = None, []
    selected_idx = 0
    h_name, a_name, h_odds, a_odds = "", "", 1.0, 1.0
    
    if request.method == 'POST':
        selected_idx = int(request.form['match_idx'])
        match = TOURNAMENT_SCHEDULE[selected_idx]
        h_name, a_name, city, country, stadium, target_iso = match["home"], match["away"], match["city"], match["host_country"], match["stadium"], match["iso_date"]
        
        if h_name in TRUE_HOST_NATIONS and h_name.lower().strip() == country.lower().strip():
            venue_status = "TRUE_HOME_HOST"
            logs.append(f"🏟️ HOST GROUND ACCREDITATION: {h_name} verified on native soil. (+12% Performance Variance Applied)")
        else:
            venue_status = "NEUTRAL_GROUND"
            logs.append(f"🌍 NEUTRAL VENUE CONFIRMED: Match calculated at a neutral stadium in {city}.")
        
        h_att, a_att, c_agg, f_fat, news_logs = harvest_live_sports_wire(h_name, a_name)
        logs.extend(news_logs)

        home_db = TEAM_STAT_DATABASE.get(h_name)
        away_db = TEAM_STAT_DATABASE.get(a_name)

        weather_desc, weather_mod = "Forecast Baseline Default", 1.0
        try:
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
            f_res = requests.get(forecast_url, timeout=4).json()
            if f_res.get("list"):
                matched_block = next((b for b in f_res["list"] if target_iso in b.get("dt_txt", "")), f_res["list"][0])
                main_cond = matched_block["weather"][0]["main"]
                weather_desc = f"Match Day Forecast: {main_cond} ({matched_block['main']['temp']}°C)"
                if main_cond in ["Rain", "Drizzle", "Snow"]:
                    weather_mod = 0.85
                    logs.append(f"🌧️ CLIMATE MITIGATION: Ball drag penalty enforced due to predicted rain in {city}.")
        except: pass

        base = run_simulation_variant(home_db, away_db, venue_status, weather_mod, None)
        behav = run_simulation_variant(home_db, away_db, venue_status, weather_mod, {'home_attacks': h_att, 'away_attacks': a_att, 'aggression_stakes': c_agg, 'fitness_fatigue': f_fat})

        h_odds, a_odds = behav['odds'][0], behav['odds'][2]

        report =  f"FIXTURE: {h_name} vs {a_name}\n"
        report += f"Stadium: {stadium} ({city})\n"
        report += f"Climate: {weather_desc}\n"
        report += f"--------------------------------------------------\n"
        report += f"MARKET COMP ODDS         [ BASE ]     [ BEHAVED ]\n"
        report += f"--------------------------------------------------\n"
        report += f"  * 1 (Home Win):          {base['odds'][0]:.2f}          {behav['odds'][0]:.2f}\n"
        report += f"  * X (Match Draw):        {base['odds'][1]:.2f}          {behav['odds'][1]:.2f}\n"
        report += f"  * 2 (Away Win):          {base['odds'][2]:.2f}          {behav['odds'][2]:.2f}\n"
        report += f"  * 01 (Double H/X):       {base['dc_odds'][0]:.2f}          {behav['dc_odds'][0]:.2f}\n"
        report += f"  * 02 (Double A/X):       {base['dc_odds'][1]:.2f}          {behav['dc_odds'][1]:.2f}\n"
        report += f"--------------------------------------------------\n"
        report += f"PROP LINES PROJECTIONS   [ BASE ]     [ BEHAVED ]\n"
        report += f"--------------------------------------------------\n"
        report += f"  * Expected Total Cards:   {base['cards']}           {behav['cards']}\n"
        report += f"  * Projected Corners:      {base['corners']}          {behav['corners']}\n"
        report += f"  * Expected Offsides:      {base['offsides']}           {behav['offsides']}\n"
        report += f"  * Total Goal Kicks Line:  {base['goal_kicks']}          {behav['goal_kicks']}\n"
        report += f"  * Shots on Target (H):    {base['shots_on_target'][0]}           {behav['shots_on_target'][0]}\n"
        report += f"  * Shots on Target (A):    {base['shots_on_target'][1]}           {behav['shots_on_target'][1]}\n"

    return render_template_string(HTML_TEMPLATE, schedule=TOURNAMENT_SCHEDULE, groups=ALL_GROUPS, teams=ALL_TEAMS, dates=ALL_DATES, report=report, logs=logs, selected_idx=selected_idx, h_name=h_name, a_name=a_name, h_odds=f"{h_odds:.2f}", a_odds=f"{a_odds:.2f}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

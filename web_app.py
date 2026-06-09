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
    # International Nations
    "Mexico": {"base_xg": 1.65, "shots_avg": 13.4, "shots_conceded_avg": 9.8, "shot_accuracy": 0.36, "gk_save_pct": 0.73, "corners_avg": 5.8, "cards_avg": 2.2, "offsides_avg": 1.9, "goal_kicks_avg": 7.2},
    "South Africa": {"base_xg": 1.15, "shots_avg": 10.2, "shots_conceded_avg": 12.4, "shot_accuracy": 0.31, "gk_save_pct": 0.67, "corners_avg": 4.1, "cards_avg": 1.9, "offsides_avg": 1.5, "goal_kicks_avg": 8.8},
    "South Korea": {"base_xg": 1.52, "shots_avg": 12.8, "shots_conceded_avg": 10.1, "shot_accuracy": 0.35, "gk_save_pct": 0.70, "corners_avg": 5.4, "cards_avg": 1.5, "offsides_avg": 2.1, "goal_kicks_avg": 6.9},
    "Czech Republic": {"base_xg": 1.38, "shots_avg": 11.9, "shots_conceded_avg": 11.2, "shot_accuracy": 0.33, "gk_save_pct": 0.72, "corners_avg": 4.9, "cards_avg": 2.4, "offsides_avg": 1.7, "goal_kicks_avg": 7.5},
    "USA": {"base_xg": 1.58, "shots_avg": 13.1, "shots_conceded_avg": 9.9, "shot_accuracy": 0.37, "gk_save_pct": 0.74, "corners_avg": 5.6, "cards_avg": 1.7, "offsides_avg": 2.0, "goal_kicks_avg": 7.1},
    "England": {"base_xg": 2.04, "shots_avg": 15.8, "shots_conceded_avg": 8.3, "shot_accuracy": 0.40, "gk_save_pct": 0.75, "corners_avg": 6.3, "cards_avg": 1.4, "offsides_avg": 2.1, "goal_kicks_avg": 6.1},
    "France": {"base_xg": 2.12, "shots_avg": 16.6, "shots_conceded_avg": 7.9, "shot_accuracy": 0.42, "gk_save_pct": 0.77, "corners_avg": 6.6, "cards_avg": 1.5, "offsides_avg": 2.4, "goal_kicks_avg": 5.8},
    "Brazil": {"base_xg": 2.15, "shots_avg": 16.8, "shots_conceded_avg": 7.8, "shot_accuracy": 0.42, "gk_save_pct": 0.76, "corners_avg": 6.7, "cards_avg": 1.6, "offsides_avg": 2.2, "goal_kicks_avg": 6.0},
    
    # Domestic Clubs / Specific League Powerhouses
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
    # Category: World Cup (WC)
    {"id": 1, "cat": "WC", "home": "Mexico", "away": "South Africa", "country": "Mexico", "tier": "Group A", "round": "Matchday 1", "date": "11/06", "city": "Mexico City"},
    {"id": 2, "cat": "WC", "home": "South Korea", "away": "Czech Republic", "country": "Mexico", "tier": "Group A", "round": "Matchday 1", "date": "11/06", "city": "Guadalajara"},
    
    # Category: Leagues (Leagues)
    {"id": 3, "cat": "Leagues", "home": "Arsenal", "away": "Chelsea", "country": "England", "tier": "Premier League", "round": "Round 32", "date": "12/06", "city": "London"},
    {"id": 4, "cat": "Leagues", "home": "Slavia Prague", "away": "Sparta Prague", "country": "Czechia", "tier": "First League", "round": "Round 28", "date": "13/06", "city": "Prague"},
    
    # Category: Cup (Cup)
    {"id": 5, "cat": "Cup", "home": "Arsenal", "away": "Chelsea", "country": "England", "tier": "FA Cup", "round": "Semifinal", "date": "14/06", "city": "London"},
    
    # Category: Elite Competitions (Elite)
    {"id": 6, "cat": "Elite", "home": "Real Madrid", "away": "Arsenal", "country": "Europe", "tier": "Champions League", "round": "Group Week 1", "date": "15/06", "city": "Madrid"},
    {"id": 7, "cat": "Elite", "home": "Czech Republic", "away": "France", "country": "Europe", "tier": "Euro Nations", "round": "Matchday 1", "date": "16/06", "city": "Prague"},
    
    # Category: International Friendlies (International)
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
        :root {
            --bg-main: #000000;
            --bg-card: #0a0f1d;
            --border-card: #1c2538;
            --text-primary: #ffffff;
            --text-secondary: #86868b;
            --accent-blue: #0a84ff;
            --accent-green: #30d158;
            --accent-orange: #ff9f0a;
            --accent-red: #ff453a;
        }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif; 
            background: var(--bg-main); color: var(--text-primary); 
            padding: 20px 16px 185px 16px; margin: 0; 
            -webkit-font-smoothing: antialiased;
        }
        
        .app-header { text-align: left; margin-bottom: 24px; padding-top: env(safe-area-inset-top); }
        .app-header-brand { display: inline-block; cursor: pointer; background: transparent; border: none; padding: 0; text-align: left; outline: none; }
        .app-header h1 { font-size: 34px; font-weight: 800; margin: 0; letter-spacing: -1px; color: var(--text-primary); }
        .app-header p { font-size: 14px; color: var(--text-secondary); margin: 4px 0 0 0; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
        
        /* Fixed: Master Category Category Navigation Ribbon rows */
        .category-ribbon { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 4px; }
        .cat-btn {
            background: #1c1c1e; border: 1px solid var(--border-card); color: var(--text-secondary);
            padding: 10px 4px; font-size: 11px; font-weight: 700; border-radius: 8px; cursor: pointer; text-align: center;
            white-space: nowrap; transition: all 0.15s ease;
        }
        .cat-btn.active { background: var(--accent-blue); color: #ffffff; border-color: var(--accent-blue); }

        .filter-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 20px; }
        .filter-menu-box { display: flex; flex-direction: column; }
        .filter-menu-box label { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 4px; }
        
        select.native-select { 
            width: 100%; padding: 10px; border-radius: 8px; 
            background: #1c1c1e; color: var(--text-primary); 
            border: 1px solid var(--border-card); font-size: 13px; font-weight: 600; outline: none; appearance: none;
        }

        .card { background: var(--bg-card); border: 1px solid var(--border-card); border-radius: 14px; padding: 16px; margin-bottom: 16px; }
        .card h3 { font-size: 13px; font-weight: 700; text-transform: uppercase; color: var(--accent-blue); margin: 0 0 14px 0; letter-spacing: 0.5px; }
        
        select.master-select {
            width: 100%; padding: 14px; border-radius: 10px;
            background: #1c1c1e; color: var(--text-primary);
            border: 1px solid var(--border-card); font-size: 15px; font-weight: 600; margin-bottom: 14px; outline: none;
        }

        button.action-btn { width: 100%; padding: 14px; border-radius: 10px; background: var(--accent-blue); color: white; font-size: 16px; font-weight: 600; border: none; cursor: pointer; }
        .log-line { font-size: 13px; color: #e5e5ea; margin-bottom: 6px; }
        
        .meta-detail-row { display: flex; justify-content: space-between; font-size: 14px; color: var(--text-secondary); padding: 5px 0; }
        .meta-detail-row span:last-child { color: var(--text-primary); font-weight: 500; }
        .sheet-divider { height: 1px; background: rgba(255,255,255,0.06); margin: 12px 0; }
        
        .matrix-table { width: 100%; border-collapse: collapse; margin-top: 4px; font-size: 14px; }
        .matrix-hdr { font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; text-align: left; padding-bottom: 8px; }
        .matrix-row { border-bottom: 1px solid rgba(255,255,255,0.04); }
        .matrix-cell { padding: 10px 0; text-align: left; }
        .cell-label { font-weight: 500; color: #e5e5ea; }
        
        .odds-pill-btn {
            background: #1c1c1e; border: 1px solid var(--border-card); color: var(--accent-green);
            padding: 6px 12px; font-weight: 700; border-radius: 6px; cursor: pointer; font-size: 13px;
        }
        .builder-market-row { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
        .market-meta { flex: 1; }
        .market-title { font-size: 14px; font-weight: 600; color: #ffffff; }
        .market-sub { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
        
        .builder-controls { display: flex; align-items: center; gap: 6px; }
        .toggle-group { display: flex; background: #1c1c1e; padding: 2px; border-radius: 6px; border: 1px solid var(--border-card); }
        .toggle-btn { background: transparent; border: none; color: var(--text-secondary); font-size: 11px; font-weight: 700; text-transform: uppercase; padding: 5px 8px; border-radius: 4px; cursor: pointer; }
        .toggle-btn.selected { background: #3a3a3c; color: #ffffff; }
        
        select.builder-dropdown { background: #1c1c1e; color: #ffffff; border: 1px solid var(--border-card); padding: 5px 24px 5px 8px; font-size: 13px; font-weight: 600; border-radius: 6px; outline: none; }
        .builder-add-btn { background: var(--accent-blue); color: white; border: none; font-size: 12px; font-weight: 700; padding: 6px 10px; border-radius: 6px; cursor: pointer; }

        .ai-gen-container { display: flex; flex-direction: column; gap: 10px; margin-top: 8px; }
        .ai-risk-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
        .risk-pick-btn { 
            background: #1c1c1e; border: 1px solid var(--border-card); color: var(--text-secondary);
            padding: 12px; border-radius: 10px; font-size: 12px; font-weight: 700; cursor: pointer; text-align: center;
            transition: all 0.2s ease;
        }
        .risk-pick-btn.selected-low { border-color: var(--accent-green); color: var(--accent-green); background: rgba(48,209,88,0.05); }
        .risk-pick-btn.selected-mod { border-color: var(--accent-orange); color: var(--accent-orange); background: rgba(255,159,10,0.05); }
        .risk-pick-btn.selected-high { border-color: var(--accent-red); color: var(--accent-red); background: rgba(255,69,58,0.05); }
        .ai-submit-trigger { width: 100%; padding: 12px; border-radius: 10px; background: #ffffff; color: #000000; font-size: 14px; font-weight: 700; border: none; cursor: pointer; text-align: center; margin-top: 4px; }

        .bet-slip-drawer {
            position: fixed; bottom: 0; left: 0; right: 0;
            background: rgba(20, 20, 22, 0.96); backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
            border-top: 1px solid #2c2c2e; padding: 12px 16px calc(12px + env(safe-area-inset-bottom)) 16px;
            border-top-left-radius: 20px; border-top-right-radius: 20px; box-shadow: 0 -10px 30px rgba(0,0,0,0.7); z-index: 999;
        }
        .drawer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .drawer-header h2 { font-size: 17px; font-weight: 700; margin: 0; }
        .clear-slip { font-size: 13px; color: var(--accent-red); font-weight: 600; cursor: pointer; }
        .horizontal-slip-container { display: flex; gap: 10px; overflow-x: auto; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; padding-bottom: 8px; margin-bottom: 8px; }
        .horizontal-slip-container::-webkit-scrollbar { height: 4px; }
        .horizontal-slip-container::-webkit-scrollbar-thumb { background: #3a3a3c; border-radius: 2px; }
        .slip-item-card { flex: 0 0 auto; background: #1c1c1e; border: 1px solid #2c2c2e; border-radius: 10px; padding: 10px 14px; min-width: 190px; scroll-snap-align: start; font-size: 13px; color: #ffffff; }
        .slip-card-odds { font-weight: 700; color: var(--accent-green); margin-top: 4px; }
        .gauge-track { width: 100%; height: 6px; background: #2c2c2e; border-radius: 3px; overflow: hidden; margin-top: 6px; }
        .gauge-fill { height: 100%; width: 0%; transition: width 0.3s ease; }
    </style>
</head>
<body>

    <div class='app-header'>
        <button class='app-header-brand' onclick='returnToLandingScreen()'>
            <h1>FC</h1>
            <p>Football Core — Quant Platform</p>
        </button>
    </div>

    <div class='category-ribbon'>
        <button class='cat-btn active' id='cat-WC' onclick='switchAppScopeCategory("WC")'>🏆 Cup</button>
        <button class='cat-btn' id='cat-Leagues' onclick='switchAppScopeCategory("Leagues")'>⚽ Leagues</button>
        <button class='cat-btn' id='cat-Cup' onclick='switchAppScopeCategory("Cup")'>🛡️ Cups</button>
        <button class='cat-btn' id='cat-Elite' onclick='switchAppScopeCategory("Elite")'>✨ Elite</button>
        <button class='cat-btn' id='cat-International' onclick='switchAppScopeCategory("International")'>🌍 Int'l</button>
    </div>

    <div class='filter-row'>
        <div class='filter-menu-box'>
            <label id='lbl-drop-1'>Groups</label>
            <select class='native-select' id='drop-1-filter' onchange='executeUnifiedCrossFilter("drop1")'></select>
        </div>
        <div class='filter-menu-box'>
            <label id='lbl-drop-2'>Country</label>
            <select class='native-select' id='drop-2-filter' onchange='executeUnifiedCrossFilter("drop2")'></select>
        </div>
        <div class='filter-menu-box'>
            <label id='lbl-drop-3'>By Date</label>
            <select class='native-select' id='drop-3-filter' onchange='executeUnifiedCrossFilter("drop3")'></select>
        </div>
    </div>

    <div class='card'>
        <h3 id='game-core-title-label'>Game Core</h3>
        <form method='POST' id='analysis-form' action='/'>
            <select name='match_idx' id='match-select' class='master-select'></select>
            <button type='submit' class='action-btn'>Calculate</button>
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
            <h3>📊 1. Mathematical Telemetry Projections</h3>
            <div class='meta-detail-row'><span>Fixture Pair</span><span>{{ report.h_name }} vs {{ report.a_name }}</span></div>
            <div class='meta-detail-row'><span>Venue Climate</span><span>{{ report.weather_desc }}</span></div>
            <div class='sheet-divider'></div>
            
            <table class='matrix-table'>
                <thead>
                    <tr>
                        <th class='matrix-hdr' style='width: 50%;'>Statistical Parameter</th>
                        <th class='matrix-hdr' style='width: 25%;'>[ Base ]</th>
                        <th class='matrix-hdr' style='width: 25%; text-align: right;'>[ Behaved ]</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class='matrix-row'><td class='matrix-cell cell-label'>Expected Goals (xG)</td><td class='matrix-cell'>{{ report.b_xg_h }} - {{ report.b_xg_a }}</td><td class='matrix-cell' style='text-align: right; color: var(--accent-blue); font-weight:600;'>{{ report.behav_xg_h }} - {{ report.behav_xg_a }}</td></tr>
                    <tr class='matrix-row'><td class='matrix-cell cell-label'>Total Match Shots</td><td class='matrix-cell'>{{ report.b_shots }}</td><td class='matrix-cell' style='text-align: right;'>{{ report.behav_shots }}</td></tr>
                    <tr class='matrix-row'><td class='matrix-cell cell-label'>Shots on Target (SOT)</td><td class='matrix-cell'>{{ report.b_sot_h }} - {{ report.b_sot_a }}</td><td class='matrix-cell' style='text-align: right;'>{{ report.behav_sot_h }} - {{ report.behav_sot_a }}</td></tr>
                    <tr class='matrix-row'><td class='matrix-cell cell-label'>Goalkeeper Saves</td><td class='matrix-cell'>{{ report.b_saves_h }} - {{ report.b_saves_a }}</td><td class='matrix-cell' style='text-align: right;'>{{ report.behav_saves_h }} - {{ report.behav_saves_a }}</td></tr>
                    <tr class='matrix-row'><td class='matrix-cell cell-label'>Projected Match Corners</td><td class='matrix-cell'>{{ report.b_corners }}</td><td class='matrix-cell' style='text-align: right;'>{{ report.behav_corners }}</td></tr>
                    <tr class='matrix-row'><td class='matrix-cell cell-label'>Total Expected Cards</td><td class='matrix-cell'>{{ report.b_cards }}</td><td class='matrix-cell' style='text-align: right;'>{{ report.behav_cards }}</td></tr>
                    <tr class='matrix-row'><td class='matrix-cell cell-label'>Total Goal Kicks Line</td><td class='matrix-cell'>{{ report.b_gk }}</td><td class='matrix-cell' style='text-align: right;'>{{ report.behav_gk }}</td></tr>
                    <tr class='matrix-row'><td class='matrix-cell cell-label'>Expected Offsides</td><td class='matrix-cell'>{{ report.b_offsides }}</td><td class='matrix-cell' style='text-align: right;'>{{ report.behav_offsides }}</td></tr>
                </tbody>
            </table>
        </div>

        <div class='card'>
            <h3>🎟️ 2. bet365 Compliant Market Price Selector</h3>
            
            <div class='builder-market-row'>
                <div class='market-meta'><div class='market-title'>Match Result (1X2)</div><div class='market-sub'>Full-time outcome probability matching</div></div>
                <div class='builder-controls' style='gap:4px;'>
                    <button class='odds-pill-btn' onclick='addOutcomeToSlip("1", "{{ report.h_name }} Win", {{ report.behav_odds_0 }})'>1 @ {{ report.behav_odds_0 }}</button>
                    <button class='odds-pill-btn' onclick='addOutcomeToSlip("X", "Match Draw", {{ report.behav_odds_1 }})'>X @ {{ report.behav_odds_1 }}</button>
                    <button class='odds-pill-btn' onclick='addOutcomeToSlip("2", "{{ report.a_name }} Win", {{ report.behav_odds_2 }})'>2 @ {{ report.behav_odds_2 }}</button>
                </div>
            </div>
            
            <div class='builder-market-row'>
                <div class='market-meta'><div class='market-title'>Double Chance Market</div><div class='market-sub'>Two combined result path lines</div></div>
                <div class='builder-controls' style='gap:4px;'>
                    <button class='odds-pill-btn' onclick='addOutcomeToSlip("1X", "Double Chance: Home/Draw", {{ report.behav_dc_0 }})'>1X @ {{ report.behav_dc_0 }}</button>
                    <button class='odds-pill-btn' onclick='addOutcomeToSlip("2X", "Double Chance: Away/Draw", {{ report.behav_dc_1 }})'>2X @ {{ report.behav_dc_1 }}</button>
                </div>
            </div>

            {% set market_configs = [
                {"id": "corners", "title": "Total Match Corners", "sub": "Combined corners line spreads", "min": 5, "max": 14, "step": 1, "start": 8, "base_odds": 1.83},
                {"id": "cards", "title": "Total Match Cards", "sub": "Aggression booking criteria indexing", "min": 1, "max": 7, "step": 1, "start": 3, "base_odds": 1.90},
                {"id": "goalkicks", "title": "Total Goal Kicks", "sub": "Goal clearance target lines", "min": 10, "max": 24, "step": 1, "start": 15, "base_odds": 1.85},
                {"id": "offsides", "title": "Expected Offsides", "sub": "Tactical forward offside traps", "min": 1, "max": 6, "step": 1, "start": 3, "base_odds": 1.75},
                {"id": "shots", "title": "Total Match Shots", "sub": "Aggregated goal attempt spreads", "min": 16, "max": 32, "step": 2, "start": 22, "base_odds": 1.88},
                {"id": "sot_h", "title": "Shots on Target (" ~ report.h_name ~ ")", "sub": "Home target accuracy criteria", "min": 2, "max": 9, "step": 1, "start": 4, "base_odds": 1.80},
                {"id": "sot_a", "title": "Shots on Target (" ~ report.a_name ~ ")", "sub": "Away target accuracy criteria", "min": 2, "max": 9, "step": 1, "start": 4, "base_odds": 1.80}
            ] %}

            {% for m in market_configs %}
            <div class='builder-market-row'>
                <div class='market-meta'><div class='market-title'>{{ m.title }}</div><div class='market-sub'>{{ m.sub }}</div></div>
                <div class='builder-controls'>
                    <div class='toggle-group' id='toggle-{{ m.id }}'>
                        <button class='toggle-btn selected' onclick='setMarketDir("{{ m.id }}", "Over")'>Over</button>
                        <button class='toggle-btn' onclick='setMarketDir("{{ m.id }}", "Under")'>Under</button>
                    </div>
                    <select class='builder-dropdown' id='select-{{ m.id }}'>
                        {% for v in range(m.min, m.max + 1, m.step) %}
                            <option value='{{ v }}' {% if v == m.start %}selected{% endif %}>{{ v }}.5</option>
                        {% endfor %}
                    </select>
                    <button class='builder-add-btn' onclick='addThresholdToSlip("{{ m.id }}", "{{ m.title }}", {{ m.base_odds }})'>+</button>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class='card'>
            <h3>🧠 3. Automated AI Scout Slip Generator</h3>
            <div class='ai-gen-container'>
                <div class='ai-risk-row'>
                    <button class='risk-pick-btn' id='risk-low-btn' onclick='selectRiskTier("low")'>🟢 LOW RISK<br><span style="font-size:10px;font-weight:400;color:var(--text-secondary);">Safe Lines</span></button>
                    <button class='risk-pick-btn' id='risk-mod-btn' onclick='selectRiskTier("mod")'>🟡 MODERATE<br><span style="font-size:10px;font-weight:400;color:var(--text-secondary);">Value Edge</span></button>
                    <button class='risk-pick-btn' id='risk-high-btn' onclick='selectRiskTier("high")'>🔴 HIGH RISK<br><span style="font-size:10px;font-weight:400;color:var(--text-secondary);">Max Return</span></button>
                </div>
                <button class='ai-submit-trigger' onclick='triggerAIScoutCompilation()'>Generate Smart Slip</button>
            </div>
        </div>
    {% endif %}

    <div class='bet-slip-drawer'>
        <div class='drawer-header'><h2>FC Bet Builder</h2><span class='clear-slip' onclick='clearSlip()'>Clear</span></div>
        <div id='slip-items-container' class='horizontal-slip-container'></div>
        <div style='display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; padding-top: 2px;'>
            <span>Total Odds: <span id='slip-odds-display' style='color: var(--accent-blue);'>1.00</span></span>
            <span>Likelihood: <span id='slip-prob-display'>100%</span></span>
        </div>
        <div class='gauge-track'><div id='slip-gauge' class='gauge-fill'></div></div>
    </div>

    <script>
        // MASTER DYNAMIC DATA OBJECT ARRAY FOR ALL DOMESTIC PYRAMIDS
        const GLOBAL_PYRAMID_CONTEXT_DATA = [
            {% for match in schedule %}
                {
                    index: {{ loop.index0 }},
                    cat: "{{ match.cat }}",
                    home: "{{ match.home }}",
                    away: "{{ match.away }}",
                    country: "{{ match.country }}",
                    tier: "{{ match.tier }}",
                    round: "{{ match.round }}",
                    date: "{{ match.date }}",
                    city: "{{ match.city }}"
                }{% if not loop.last %},{% endif %}
            {% endfor %}
        ];

        let activeAppCategory = localStorage.getItem('fc_active_cat') || 'WC';
        let currentSlip = JSON.parse(localStorage.getItem('fc_slip')) || [];
        const rememberedIndex = "{{ selected_idx }}";
        const currentFixtureName = "{% if report %}{{ report.h_name }} vs {{ report.a_name }}{% endif %}";
        
        let marketDirections = { corners: "Over", cards: "Over", goalkicks: "Over", offsides: "Over", shots: "Over", sot_h: "Over", sot_a: "Over" };
        let selectedAIProfile = null;

        const dataPayloadContext = {
            homeTeam: "{% if report %}{{ report.h_name }}{% endif %}",
            awayTeam: "{% if report %}{{ report.a_name }}{% endif %}",
            hOdds: {% if report %}{{ report.behav_odds_0 }}{% else %}1.0{% endif %},
            aOdds: {% if report %}{{ report.behav_odds_2 }}{% else %}1.0{% endif %},
            dcHome: {% if report %}{{ report.behav_dc_0 }}{% else %}1.0{% endif %},
            dcAway: {% if report %}{{ report.behav_dc_1 }}{% else %}1.0{% endif %},
            avgCorners: {% if report %}{{ report.behav_corners }}{% else %}0.0{% endif %},
            avgCards: {% if report %}{{ report.behav_cards }}{% else %}0.0{% endif %}
        };

        function returnToLandingScreen() { window.location.href = '/'; }

        // FIXED: Universal Category Switch Routing Matrix that mutates labels instantly
        function switchAppScopeCategory(categoryKey) {
            activeAppCategory = categoryKey;
            localStorage.setItem('fc_active_cat', categoryKey);
            
            // Set dynamic button active state styles
            document.querySelectorAll('.cat-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(`cat-${categoryKey}`).classList.add('active');
            
            // Mutate dropdown structural labels as configured by user parameters
            const lbl1 = document.getElementById('lbl-drop-1');
            const lbl2 = document.getElementById('lbl-drop-2');
            const lbl3 = document.getElementById('lbl-drop-3');
            
            if (categoryKey === 'WC' || categoryKey === 'Elite') {
                lbl1.innerText = "Groups / Bracket"; lbl2.innerText = "Country Venue"; lbl3.innerText = "By Date";
            } else if (categoryKey === 'Leagues' || categoryKey === 'Cup') {
                lbl1.innerText = "Country"; lbl2.innerText = "League Tier / Cup"; lbl3.innerText = "Round Select";
            } else if (categoryKey === 'International') {
                lbl1.innerText = "Country Focus"; lbl2.innerText = "Match Type"; lbl3.innerText = "By Date";
            }
            
            repopulateDynamicDropdownOptions(categoryKey, 'init');
        }

        // FIXED: Re-engineered dynamic dropdown multi-cascading text injection loops
        function repopulateDynamicDropdownOptions(category, phase) {
            const d1 = document.getElementById('drop-1-filter');
            const d2 = document.getElementById('drop-2-filter');
            const d3 = document.getElementById('drop-3-filter');
            
            // Extract sorted distinct keys from active array elements
            let scopeMatches = GLOBAL_PYRAMID_CONTEXT_DATA.filter(m => m.cat === category);
            
            let set1 = new Set(), set2 = new Set(), set3 = new Set();
            scopeMatches.forEach(m => {
                if (category === 'Leagues' || category === 'Cup') {
                    set1.add(m.country); set2.add(m.tier); set3.add(m.round);
                } else {
                    set1.add(m.tier); set2.add(m.country); set3.add(m.date);
                }
            });

            // Rebuild Dropdown DOM channels instantly
            buildSelectOptions(d1, set1, "All options");
            buildSelectOptions(d2, set2, "All tiers");
            buildSelectOptions(d3, set3, "All lists");
            
            executeUnifiedCrossFilter('init');
        }

        function buildSelectOptions(element, dataSet, defaultLabel) {
            element.innerHTML = `<option value="all">${defaultLabel}</option>`;
            Array.from(dataSet).sort().forEach(v => {
                element.innerHTML += `<option value="${v}">${v}</option>`;
            });
        }

        // FIXED: Absolute clean option pruning script that builds the master selector
        function executeUnifiedCrossFilter(triggerSource) {
            const v1 = document.getElementById('drop-1-filter').value;
            const v2 = document.getElementById('drop-2-filter').value;
            const v3 = document.getElementById('drop-3-filter').value;
            const masterSelect = document.getElementById('match-select');
            
            masterSelect.innerHTML = '';
            let matchedCount = 0;

            GLOBAL_PYRAMID_CONTEXT_DATA.forEach(match => {
                if (match.cat !== activeAppCategory) return;
                
                let condition1 = false, condition2 = false, condition3 = false;
                if (activeAppCategory === 'Leagues' || activeAppCategory === 'Cup') {
                    condition1 = (v1 === 'all' || match.country === v1);
                    condition2 = (v2 === 'all' || match.tier === v2);
                    condition3 = (v3 === 'all' || match.round === v3);
                } else {
                    condition1 = (v1 === 'all' || match.tier === v1);
                    condition2 = (v2 === 'all' || match.country === v2);
                    condition3 = (v3 === 'all' || match.date === v3);
                }

                if (condition1 && condition2 && condition3) {
                    const opt = document.createElement('option');
                    opt.value = match.index;
                    opt.innerText = `[${match.tier}] ${match.date} | ${match.home} vs ${match.away} (${match.city})`;
                    if (match.index == rememberedIndex && triggerSource === 'init') opt.selected = true;
                    masterSelect.appendChild(opt);
                    matchedCount++;
                }
            });

            if (matchedCount === 0) {
                masterSelect.innerHTML = '<option value="-1">No scheduled games found in round</option>';
            }
        }

        function setMarketDir(marketId, direction) {
            marketDirections[marketId] = direction;
            const container = document.getElementById(`toggle-${marketId}`);
            const buttons = container.getElementsByTagName('button');
            if (direction === "Over") { buttons[0].className = 'toggle-btn selected'; buttons[1].className = 'toggle-btn'; } 
            else { buttons[0].className = 'toggle-btn'; buttons[1].className = 'toggle-btn selected'; }
        }

        function addOutcomeToSlip(codeKey, label, decimalOdds) {
            if (currentSlip.length >= 20) { alert("bet365 Rule Cap: Max 20 selections allowed."); return; }
            const marketID = `${currentFixtureName} - result_line`;
            if (currentSlip.some(item => item.id === marketID && item.val !== codeKey)) { alert("Contradiction Blocked: Conflicting match outcome choice detected."); return; }
            if (currentSlip.some(item => item.id === `${currentFixtureName} - ${label}`)) return;
            currentSlip.push({ id: `${currentFixtureName} - ${label}`, fixture: currentFixtureName, market: `${currentFixtureName} | ${label}`, odds: decimalOdds, category: "outcome", val: codeKey });
            updateSlipUI();
        }

        function addThresholdToSlip(marketId, marketTitle, targetBaseOdds) {
            if (currentSlip.length >= 20) { alert("bet365 Rule Cap: Max 20 selections allowed."); return; }
            const direction = marketDirections[marketId];
            const thresholdValue = document.getElementById(`select-${marketId}`).value + ".5";
            const marketKeyID = `${currentFixtureName} - ${marketId}`;
            
            const existingConflictingLine = currentSlip.find(item => item.id === marketKeyID);
            if (existingConflictingLine) {
                if (existingConflictingLine.dir !== direction || existingConflictingLine.lineVal !== thresholdValue) {
                    alert(`Contradiction Blocked: You have already designated a conflicting line index for ${marketTitle} on this ticket.`); return;
                }
                return;
            }

            let variableOddsModifier = parseFloat(targetBaseOdds);
            const selectedNumericValue = parseFloat(thresholdValue);
            if (direction === "Over" && selectedNumericValue > 6) variableOddsModifier += 0.45;
            if (direction === "Under" && selectedNumericValue < 4) variableOddsModifier += 0.35;

            currentSlip.push({ id: marketKeyID, fixture: currentFixtureName, market: `${currentFixtureName} | ${direction} ${thresholdValue} ${marketTitle.split(' (')[0]}`, odds: parseFloat(variableOddsModifier.toFixed(2)), category: marketId, dir: direction, lineVal: thresholdValue });
            updateSlipUI();
        }

        function selectRiskTier(tier) {
            selectedAIProfile = tier;
            document.getElementById('risk-low-btn').className = 'risk-pick-btn';
            document.getElementById('risk-mod-btn').className = 'risk-pick-btn';
            document.getElementById('risk-high-btn').className = 'risk-pick-btn';
            if (tier === 'low') document.getElementById('risk-low-btn').classList.add('selected-low');
            if (tier === 'mod') document.getElementById('risk-mod-btn').classList.add('selected-mod');
            if (tier === 'high') document.getElementById('risk-high-btn').classList.add('selected-high');
        }

        function triggerAIScoutCompilation() {
            if (!selectedAIProfile) { alert("Selection Required: Please pick a risk profile tier baseline first."); return; }
            clearSlip();
            const hName = dataPayloadContext.homeTeam; const aName = dataPayloadContext.awayTeam;

            if (selectedAIProfile === 'low') {
                const preferredDC = dataPayloadContext.hOdds <= dataPayloadContext.aOdds ? { code: "1X", label: `Double Chance: ${hName}/Draw`, odds: dataPayloadContext.dcHome } : { code: "2X", label: `Double Chance: ${aName}/Draw`, odds: dataPayloadContext.dcAway };
                addOutcomeToSlip(preferredDC.code, preferredDC.label, preferredDC.odds);
                const safeCornerThreshold = Math.ceil(dataPayloadContext.avgCorners + 3) + ".5";
                currentSlip.push({ id: `${currentFixtureName} - corners`, fixture: currentFixtureName, market: `${currentFixtureName} | Under ${safeCornerThreshold} Total Corners`, odds: 1.32, category: "corners", dir: "Under", lineVal: safeCornerThreshold });
            } 
            else if (selectedAIProfile === 'mod') {
                if (dataPayloadContext.hOdds !== dataPayloadContext.aOdds) {
                    const favorite = dataPayloadContext.hOdds < dataPayloadContext.aOdds ? { code: "1", label: `${hName} Win`, odds: dataPayloadContext.hOdds } : { code: "2", label: `${aName} Win`, odds: dataPayloadContext.aOdds };
                    addOutcomeToSlip(favorite.code, favorite.label, favorite.odds);
                } else { addOutcomeToSlip("X", "Match Draw", dataPayloadContext.hOdds); }
                const valueCornerThreshold = Math.floor(dataPayloadContext.avgCorners - 1) + ".5";
                currentSlip.push({ id: `${currentFixtureName} - corners`, fixture: currentFixtureName, market: `${currentFixtureName} | Over ${valueCornerThreshold} Total Corners`, odds: 1.68, category: "corners", dir: "Over", lineVal: valueCornerThreshold });
            } 
            else if (selectedAIProfile === 'high') {
                const underdog = dataPayloadContext.hOdds > dataPayloadContext.aOdds ? { code: "1", label: `${hName} Win (Underdog Boost)`, odds: dataPayloadContext.hOdds } : { code: "2", label: `${aName} Win (Underdog Boost)`, odds: dataPayloadContext.aOdds };
                addOutcomeToSlip(underdog.code, underdog.label, underdog.odds);
                const aggressiveCornerThreshold = Math.floor(dataPayloadContext.avgCorners + 1) + ".5";
                currentSlip.push({ id: `${currentFixtureName} - corners`, fixture: currentFixtureName, market: `${currentFixtureName} | Over ${aggressiveCornerThreshold} Total Corners`, odds: 2.35, category: "corners", dir: "Over", lineVal: aggressiveCornerThreshold });
            }
            updateSlipUI();
        }

        function removeSlipItem(index) { currentSlip.splice(index, 1); updateSlipUI(); }
        function clearSlip() { currentSlip = []; updateSlipUI(); }

        function updateSlipUI() {
            localStorage.setItem('fc_slip', JSON.stringify(currentSlip));
            const container = document.getElementById('slip-items-container'); container.innerHTML = '';
            let accumulatedOdds = 1.0, compoundedProb = 1.0;

            currentSlip.forEach((item, index) => {
                accumulatedOdds *= item.odds; compoundedProb *= (1.0 / item.odds);
                const card = document.createElement('div'); card.className = 'slip-item-card';
                card.onclick = () => removeSlipItem(index);
                card.innerHTML = `<div class="slip-card-title">${item.market}</div><div class="slip-card-odds">@ ${item.odds.toFixed(2)}</div>`;
                container.appendChild(card);
            });

            if (currentSlip.length === 0) { container.innerHTML = "<div style='color: var(--text-secondary); font-size:12px; padding: 12px 0;'>Select over/under threshold spreads to compile slip components.</div>"; accumulatedOdds = 1.0; compoundedProb = 1.0; }
            const totalPct = compoundedProb * 100;
            document.getElementById('slip-odds-display').innerText = accumulatedOdds.toFixed(2);
            document.getElementById('slip-prob-display').innerText = totalPct.toFixed(1) + '%';
            const fill = document.getElementById('slip-gauge'); fill.style.width = currentSlip.length === 0 ? '0%' : totalPct + '%';
            if (totalPct > 45) fill.style.background = 'var(--accent-green)'; else if (totalPct > 20) fill.style.background = 'var(--accent-orange)'; else fill.style.background = 'var(--accent-red)';
        }

        // Initialize boot lifecycle checks
        document.addEventListener('DOMContentLoaded', () => {
            switchAppScopeCategory(activeAppCategory);
            updateSlipUI();
        });
    </script>
</body>
</html>
"""

# =====================================================================
# 5. RESTORED MASTER BRAIN HOME GATEWAY GATE ROUTE
# =====================================================================
@app.route('/', methods=['GET', 'POST'])
def home():
    report, logs = None, []
    selected_idx = 0
    
    if request.method == 'POST':
        selected_idx = int(request.form['match_idx'])
        match = GLOBAL_MATCH_DATABASE[selected_idx]
        h_name, a_name, city, country, target_iso = match["home"], match["away"], match["city"], match["country"], "2026-06-12"
        
        if h_name in TRUE_HOST_NATIONS and h_name.lower().strip() == country.lower().strip():
            venue_status = "TRUE_HOME_HOST"
            logs.append(f"🏟️ HOST GROUND ACCREDITATION: {h_name} verified on native soil. (+12% Variance Imbalance)")
        else:
            venue_status = "NEUTRAL_GROUND"
            logs.append(f"🌍 NEUTRAL VENUE CONFIRMED: Match evaluated at a neutral stadium in {city}.")
        
        h_att, a_att, c_agg, f_fat, news_logs = harvest_live_sports_wire(h_name, a_name)
        logs.extend(news_logs)

        home_db = TEAM_STAT_DATABASE.get(h_name, {"base_xg": 1.35, "shots_avg": 11.5, "shots_conceded_avg": 11.5, "shot_accuracy": 0.33, "gk_save_pct": 0.70, "corners_avg": 4.8, "cards_avg": 2.0, "offsides_avg": 1.7, "goal_kicks_avg": 7.5})
        away_db = TEAM_STAT_DATABASE.get(a_name, {"base_xg": 1.35, "shots_avg": 11.5, "shots_conceded_avg": 11.5, "shot_accuracy": 0.33, "gk_save_pct": 0.70, "corners_avg": 4.8, "cards_avg": 2.0, "offsides_avg": 1.7, "goal_kicks_avg": 7.5})

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
                    logs.append(f"🌧️ CLIMATE MITIGATION: Friction scaling factor enforced due to weather parameters in {city}.")
        except: pass

        base = run_simulation_variant(home_db, away_db, venue_status, weather_mod, None)
        behav = run_simulation_variant(home_db, away_db, venue_status, weather_mod, {'home_attacks': h_att, 'away_attacks': a_att, 'aggression_stakes': c_agg, 'fitness_fatigue': f_fat})

        report = {
            "h_name": h_name, "a_name": a_name, "city": city, "weather_desc": weather_desc,
            "behav_odds_0": f"{behav['odds'][0]:.2f}", "behav_odds_1": f"{behav['odds'][1]:.2f}", "behav_odds_2": f"{behav['odds'][2]:.2f}",
            "behav_dc_0": f"{behav['dc_odds'][0]:.2f}", "behav_dc_1": f"{behav['dc_odds'][1]:.2f}",
            "b_xg_h": f"{base['odds'][0]*0.4:.2f}", "b_xg_a": f"{base['odds'][2]*0.3:.2f}",
            "behav_xg_h": f"{behav['odds'][0]*0.41:.2f}", "behav_xg_a": f"{behav['odds'][2]*0.32:.2f}",
            "b_shots": f"{base['shots_total']}", "behav_shots": f"{behav['shots_total']}",
            "b_sot_h": f"{base['shots_on_target'][0]}", "behav_sot_h": f"{behav['shots_on_target'][0]}",
            "b_sot_a": f"{base['shots_on_target'][1]}", "behav_sot_a": f"{behav['shots_on_target'][1]}",
            "b_saves_h": f"{base['saves'][0]}", "behav_saves_h": f"{behav['saves'][0]}",
            "b_saves_a": f"{base['saves'][1]}", "behav_saves_a": f"{behav['saves'][1]}",
            "b_cards": f"{base['cards']}", "behav_cards": f"{behav['cards']}",
            "b_corners": f"{base['corners']}", "behav_corners": f"{behav['corners']}",
            "b_gk": f"{base['goal_kicks']}", "behav_gk": f"{behav['goal_kicks']}",
            "b_offsides": f"{base['offsides']}", "behav_offsides": f"{behav['offsides']}"
        }

    return render_template_string(HTML_TEMPLATE, schedule=GLOBAL_MATCH_DATABASE, groups=ALL_GROUPS, teams=ALL_TEAMS, dates=ALL_DATES, report=report, logs=logs, selected_idx=selected_idx)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

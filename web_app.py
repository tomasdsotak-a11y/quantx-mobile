from flask import Flask, render_template_string, request
import math
import requests
import urllib.request
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Active Gateway Security Tokens
WEATHER_API_KEY = "25c9a61b99a4842679a8983536494752"

# =====================================================================
# 1. LIVE SQUAD REGISTRY MATRIX
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
    "Switzerland":   {"base_xg": 1.42, "shots_avg": 12.0, "shots_conceded_avg": 10.5, "shot_accuracy": 0.34, "gk_save_pct": 0.71, "corners_avg": 5.0, "cards_avg": 2.1, "offsides_avg": 1.7}
}

TOURNAMENT_SCHEDULE = [
    {"id": 101, "date": "11/06 — 19:00", "home": "Mexico", "away": "South Africa", "stadium": "Estadio Azteca", "city": "Mexico City", "host_country": "Mexico"},
    {"id": 102, "date": "12/06 — 02:00", "home": "South Korea", "away": "Czech Republic", "stadium": "Estadio Guadalajara", "city": "Guadalajara", "host_country": "Mexico"},
    {"id": 103, "date": "12/06 — 19:00", "home": "Canada", "away": "Bosnia", "stadium": "BMO Field", "city": "Toronto", "host_country": "Canada"},
    {"id": 104, "date": "13/06 — 01:00", "home": "USA", "away": "Paraguay", "stadium": "SoFi Stadium", "city": "Los Angeles", "host_country": "USA"},
    {"id": 105, "date": "13/06 — 19:00", "home": "Qatar", "away": "Switzerland", "stadium": "BC Place", "city": "Vancouver", "host_country": "Canada"}
]

# =====================================================================
# 2. REAL-TIME LIVE NEWS FEED SCRAPER (THE INTAKE ENGINE)
# =====================================================================
def harvest_live_sports_wire(home_team, away_team):
    scraped_text_blob = ""
    discovery_logs = []
    
    target_feeds = [
        "https://www.skysports.com/rss/feeds/12040.xml", 
        "https://www.independent.co.uk/sport/football/rss" 
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'}
    
    for feed_url in target_feeds:
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    desc = item.find('description').text if item.find('description') is not None else ""
                    combined = f"{title} {desc}".lower()
                    
                    if home_team.lower() in combined or away_team.lower() in combined:
                        scraped_text_blob += f" {combined}"
        except:
            pass 
            
    h_att, a_att, c_agg, f_fat = 1.0, 1.0, 1.0, 1.0
    
    if len(scraped_text_blob) > 0:
        if "must win" in scraped_text_blob or "elimination" in scraped_text_blob:
            c_agg = 1.45; h_att *= 1.15; a_att *= 1.15
            discovery_logs.append("⚠️ LIVE WIRE: Must-Win context detected on news feeds! (+45% Cards, +15% Attacking Volume)")
        if "fatigue" in scraped_text_blob or "tired" in scraped_text_blob or "rested" in scraped_text_blob:
            f_fat = 0.90
            discovery_logs.append("🏃‍♂️ LIVE WIRE: Squad fatigue or lineup rotation mentions found on wire. (-10% Accuracy)")
        if "injury" in scraped_text_blob or "injured" in scraped_text_blob or "doubt" in scraped_text_blob:
            h_att *= 0.95; a_att *= 0.95
            discovery_logs.append("🏥 LIVE WIRE: Active injury or squad fitness updates detected. (-5% Efficiency)")
            
    return h_att, a_att, c_agg, f_fat, discovery_logs

# =====================================================================
# 3. MATHEMATICAL PROBABILITY ENGINE
# =====================================================================
def poisson_probability(k, lamb):
    if lamb <= 0: return 0.0
    return (math.exp(-lamb) * (lamb ** k)) / math.factorial(k)

def run_simulation_variant(home_stats, away_stats, venue_status, weather_mod, behavior_mods=None):
    home_advantage = 1.12 if venue_status == "TRUE_HOME" else 1.00
    
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
    
    total_goal_kicks = 23.5 - ((pred_home_shots + pred_away_shots) * 0.42)

    return {
        "odds": (1/p_home if p_home > 0 else 99, 1/p_draw if p_draw > 0 else 99, 1/p_away if p_away > 0 else 99),
        "dc_odds": (1/(p_home+p_draw) if (p_home+p_draw) > 0 else 99, 1/(p_away+p_draw) if (p_away+p_draw) > 0 else 99),
        "corners": round((home_stats['corners_avg'] + away_stats['corners_avg']) * ((h_att + a_att)/2), 1),
        "cards": round((home_stats['cards_avg'] + away_stats['cards_avg']) * c_agg, 1),
        "offsides": round(home_stats['offsides_avg'] + away_stats['offsides_avg'], 1),
        "goal_kicks": round(total_goal_kicks, 1),
        "shots_on_target": (round(pred_home_sot, 1), round(pred_away_sot, 1)),
        "saves": (round(pred_home_saves, 1), round(pred_away_saves, 1))
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'>
    <title>QuantX Pro Live</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 16px; margin: 0; }
        h2 { color: #38bdf8; font-size: 20px; text-align: center; margin-bottom: 20px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
        h3 { font-size: 14px; color: #94a3b8; text-transform: uppercase; margin-top: 0; margin-bottom: 12px; letter-spacing: 1px; }
        .card { background: #1e293b; padding: 18px; border-radius: 16px; margin-bottom: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); border: 1px solid #334155; }
        label { font-size: 13px; font-weight: 600; color: #94a3b8; display: block; margin-bottom: 6px; }
        select { width: 100%; padding: 14px; border-radius: 12px; background: #334155; color: white; border: 1px solid #475569; font-size: 15px; font-weight: 500; appearance: none; margin-bottom: 4px; }
        button { width: 100%; padding: 14px; border-radius: 12px; background: #10b981; color: white; font-size: 15px; font-weight: 700; border: none; margin-top: 8px; }
        .log-box { background: #020617; padding: 12px; border-radius: 10px; border-left: 3px solid #38bdf8; margin-bottom: 16px; font-size: 12px; color: #cbd5e1; line-height: 1.5; }
        pre { background: #020617; padding: 14px; border-radius: 12px; overflow-x: auto; font-family: "Courier New", Courier, monospace; font-size: 11px; line-height: 1.6; color: #f8fafc; border: 1px solid #1e293b; margin: 0; }
    </style>
</head>
<body>
    <h2>🏆 QuantX Pro Live</h2>
    <div class='card'>
        <form method='POST'>
            <label>Select Scheduled World Cup Match:</label>
            <select name='match_idx'>
                {% for match in schedule %}
                    <option value='{{ loop.index0 }}' {% if selected_idx == loop.index0 %}selected{% endif %}>{{ match.date }} | {{ match.home }} vs {{ match.away }}</option>
                {% endfor %}
            </select>
            <button type='submit'>Scrape & Compute Metrics</button>
        </form>
    </div>

    {% if report %}
        <div class='card'>
            <h3>📡 Real-Time News Scraper Activity</h3>
            <div class='log-box'>
                {% for log in logs %}
                    • {{ log }}<br>
                {% else %}
                    ✅ Clean Wire: No breaking news warnings, injuries, or fatigue alerts located for these squads.
                {% endfor %}
            </div>
        </div>
        <div class='card'>
            <h3>📊 Analysis Matrix Results</h3>
            <pre>{{ report }}</pre>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    report = None
    logs = []
    selected_idx = 1
    
    if request.method == 'POST':
        selected_idx = int(request.form['match_idx'])
        match = TOURNAMENT_SCHEDULE[selected_idx]
        h_name, a_name, city, country, stadium = match["home"], match["away"], match["city"], match["host_country"], match["stadium"]
        
        venue_status = "TRUE_HOME" if h_name.lower().strip() == country.lower().strip() else "NEUTRAL_GROUND"
        
        # Pull live metrics directly from the internet news aggregator wires
        h_att, a_att, c_agg, f_fat, logs = harvest_live_sports_wire(h_name, a_name)

        home_db = TEAM_STAT_DATABASE.get(h_name, TEAM_STAT_DATABASE["Mexico"])
        away_db = TEAM_STAT_DATABASE.get(a_name, TEAM_STAT_DATABASE["South Africa"])

        # Weather Radar Fetch
        weather_desc, weather_mod = "Clear Conditions", 1.0
        try:
            w_res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric", timeout=4).json()
            if w_res.get("weather"):
                weather_desc = f"{w_res['weather'][0]['main']} ({w_res['main']['temp']}°C)"
                if "Rain" in w_res['weather'][0]['main'] or "Drizzle" in w_res['weather'][0]['main']: 
                    weather_mod = 0.85
        except: pass

        base = run_simulation_variant(home_db, away_db, venue_status, weather_mod, None)
        behav = run_simulation_variant(home_db, away_db, venue_status, weather_mod, {'home_attacks': h_att, 'away_attacks': a_att, 'aggression_stakes': c_agg, 'fitness_fatigue': f_fat})

        report =  f"FIXTURE: {h_name} vs {a_name}\n"
        report += f"Venue:   {stadium} ({city})\n"
        report += f"Weather: {weather_desc}\n"
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
        report += f"  * Goalie Saves (Home):    {base['saves'][0]}           {behav['saves'][0]}\n"
        report += f"  * Goalie Saves (Away):    {base['saves'][1]}           {behav['saves'][1]}\n"

    return render_template_string(HTML_TEMPLATE, schedule=TOURNAMENT_SCHEDULE, report=report, logs=logs, selected_idx=selected_idx)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

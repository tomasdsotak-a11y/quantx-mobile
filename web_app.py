from flask import Flask, render_template_string, request
import math

app = Flask(__name__)

# --- GLOBAL DATA REGISTRY ---
# Normalizing all entries with .setdefault() below prevents "KeyError" crashes
GLOBAL_MATCH_DATABASE = [
    {"id": 0, "cat": "WC", "home": "Mexico", "away": "South Africa", "country": "Mexico", "tier": "Group A", "round": "Matchday 1", "date": "11/06", "city": "Mexico City", "hours_to_kick": 4},
    {"id": 1, "cat": "Leagues", "home": "Arsenal", "away": "Chelsea", "country": "England", "tier": "Premier League", "round": "Round 36", "date": "12/06", "city": "London", "hours_to_kick": 14},
    {"id": 2, "cat": "Elite", "home": "Real Madrid", "away": "Arsenal", "country": "Europe", "tier": "Champions League", "round": "Matchday 1", "date": "15/06", "city": "Madrid", "hours_to_kick": 22}
]

for m in GLOBAL_MATCH_DATABASE:
    m.setdefault("country", "Unknown")
    m.setdefault("date", "TBD")
    m.setdefault("tier", "General")
    m.setdefault("round", "Regular")
    m.setdefault("city", "Unknown")

# --- HTML TEMPLATE WITH JS BRIDGE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; padding: 20px; }
        .cat-btn { background: #1c1c1e; color: #86868b; padding: 10px; border-radius: 8px; border: none; cursor: pointer; margin-right: 5px; }
        .cat-btn.active { background: #0a84ff; color: #fff; }
        .card { background: #0a0f1d; padding: 16px; border-radius: 14px; margin-top: 20px; }
    </style>
</head>
<body>
    <div style="display:flex; overflow-x:auto;">
        <button class="cat-btn active" id="cat-WC" onclick="filterData('WC')">World Cup</button>
        <button class="cat-btn" id="cat-Leagues" onclick="filterData('Leagues')">Leagues</button>
        <button class="cat-btn" id="cat-Upcoming" onclick="filterData('Upcoming')">Upcoming</button>
    </div>
    <div class="card">
        <form method="POST">
            <select name="match_idx" id="match-select" style="width:100%; padding:10px;"></select>
            <button type="submit" style="width:100%; margin-top:10px; padding:10px;">Calculate</button>
        </form>
    </div>
    <script>
        const DB = {{ schedule | tojson }};
        function filterData(cat) {
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('cat-' + cat).classList.add('active');
            const select = document.getElementById('match-select');
            select.innerHTML = '';
            DB.filter(m => cat === 'Upcoming' ? m.hours_to_kick <= 24 : m.cat === cat).forEach(m => {
                select.innerHTML += `<option value="${m.id}">[${m.tier}] ${m.home} vs ${m.away}</option>`;
            });
        }
        document.addEventListener('DOMContentLoaded', () => filterData('WC'));
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    report = None
    if request.method == 'POST':
        idx = int(request.form.get('match_idx', 0))
        report = next((m for m in GLOBAL_MATCH_DATABASE if m["id"] == idx), GLOBAL_MATCH_DATABASE[0])
    return render_template_string(HTML_TEMPLATE, schedule=GLOBAL_MATCH_DATABASE, report=report)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

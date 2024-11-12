
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import requests
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Use a secret key for session management

def find_servers(place_id, max_ping=None):
    url = f'https://games.roblox.com/v1/games/{place_id}/servers/0?sortOrder=2&excludeFullGames=true&limit=100'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {'error': f"Error fetching server data: {e}"}
    data = response.json()
    servers = data.get('data', [])
    if max_ping is not None:
        servers = [server for server in servers if server.get('ping', 0) <= max_ping]
    return sorted(servers, key=lambda s: s['ping'])

@app.route('/', methods=['GET', 'POST'])
def home():
    servers = []
    place_id = session.get('place_id', None)
    max_ping = session.get('max_ping', None)
    error = None
    random_choice = False

    if request.method == 'POST':
        place_id = request.form.get('placeId')
        max_ping = request.form.get('maxPing', type=int)
        random_choice = request.form.get('randomChoice') == 'on'

        if not place_id:
            error = 'Place ID is required.'
        else:
            session['place_id'] = place_id
            session['max_ping'] = max_ping
            servers = find_servers(place_id, max_ping)
            if 'error' in servers:
                error = servers['error']
                servers = []
            elif random_choice and servers:
                servers = [random.choice(servers)]

    return render_template('index.html', servers=servers, place_id=place_id, max_ping=max_ping, error=error)

@app.route('/launch', methods=['POST'])
def launch_roblox():
    place_id = request.json.get('placeId')
    game_instance_id = request.json.get('gameInstanceId')
    if not place_id or not game_instance_id:
        return jsonify({'error': 'Place ID and Game Instance ID are required'}), 400
    roblox_url = f"roblox://experiences/start?placeId={place_id}&gameInstanceId={game_instance_id}"
    return jsonify({'roblox_url': roblox_url})

@app.route('/invite')
def invite():
    place_id = request.args.get('placeid')
    game_instance_id = request.args.get('gameinstanceid')
    roblox_url = f"roblox://experiences/start?placeId={place_id}&gameInstanceId={game_instance_id}"
    return redirect(roblox_url)  # Immediately try to launch the game

if __name__ == '__main__':
    app.run(debug=True)

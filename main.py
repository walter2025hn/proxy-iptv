from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Reemplaza esto con el enlace RAW de tu lista de GitHub
GITHUB_M3U_URL = "https://bit.ly/4t9rqok"
# ---------------------

def parse_m3u():
    try:
        response = requests.get(GITHUB_M3U_URL)
        lines = response.text.splitlines()
    except:
        return []

    data = []
    current_item = {}
    
    for line in lines:
        if line.startswith("#EXTINF"):
            # Extraer el nombre (lo que va después de la última coma)
            name = line.split(',')[-1].strip()
            
            # Extraer el grupo (lo que está en group-title="")
            group = "General"
            group_match = re.search(r'group-title="([^"]+)"', line)
            if group_match:
                group = group_match.group(1)
            
            # Extraer el logo si existe
            logo = ""
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            if logo_match:
                logo = logo_match.group(1)

            current_item = {"name": name, "group": group, "logo": logo}
        elif line.startswith("http"):
            if current_item:
                current_item["url"] = line.strip()
                data.append(current_item)
                current_item = {}
    return data

@app.route('/player_api.php')
def player_api():
    username = request.args.get('username')
    password = request.args.get('password')
    action = request.args.get('action')

    # Credenciales para IPTV Smarters
    if username != "admin" or password != "master":
        return jsonify({"error": "Auth failed"}), 401

    if not action:
        return jsonify({
            "user_info": {"status": "Active", "auth": 1, "username": "admin"},
            "server_info": {"url": "Codigo Master TV", "port": "80", "server_protocol": "http"}
        })

    all_data = parse_m3u()

    # --- LÓGICA DE CANALES EN VIVO ---
    if action == "get_live_categories":
        return jsonify([{"category_id": "1", "category_name": "TV EN VIVO"}])
    
    if action == "get_live_streams":
        streams = []
        for i, item in enumerate(all_data):
            if "PELÍCULAS" not in item['group'].upper() and "SERIES" not in item['group'].upper():
                streams.append({
                    "num": i, "name": item['name'], "stream_id": i,
                    "stream_icon": item['logo'], "category_id": "1", "direct_source": item['url']
                })
        return jsonify(streams)

    # --- LÓGICA DE PELÍCULAS (VOD) ---
    if action == "get_vod_categories":
        return jsonify([{"category_id": "2", "category_name": "PELÍCULAS"}])

    if action == "get_vod_streams":
        vods = []
        for i, item in enumerate(all_data):
            if "PELÍCULAS" in item['group'].upper():
                vods.append({
                    "num": i, "name": item['name'], "stream_id": i,
                    "stream_icon": item['logo'], "category_id": "2", "direct_source": item['url'],
                    "container_extension": "mp4"
                })
        return jsonify(vods)

    # --- LÓGICA DE SERIES ---
    if action == "get_series_categories":
        return jsonify([{"category_id": "3", "category_name": "SERIES"}])

    if action == "get_series":
        series = []
        for i, item in enumerate(all_data):
            if "SERIES" in item['group'].upper():
                series.append({
                    "num": i, "name": item['name'], "series_id": i,
                    "cover": item['logo'], "category_id": "3", "last_modified": "1618524330"
                })
        return jsonify(series)

    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

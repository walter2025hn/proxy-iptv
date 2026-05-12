from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

GITHUB_M3U_URL = "https://bit.ly/4t9rqok"

def get_data():
    try:
        r = requests.get(GITHUB_M3U_URL, timeout=10)
        return r.text
    except:
        return ""

@app.route('/')
def index():
    return "Servidor Maestro Activo ✅"

@app.route('/player_api.php')
def player_api():
    user = request.args.get('username')
    pw = request.args.get('password')
    action = request.args.get('action')

    if user != "admin" or pw != "master":
        return jsonify({"error": "Auth failed"}), 401

    if not action:
        return jsonify({
            "user_info": {"status": "Active", "auth": 1},
            "server_info": {"url": "Codigo Master", "port": "80"}
        })

    m3u_content = get_data()
    
    # Respuesta para Canales en Vivo
    if action == "get_live_categories":
        return jsonify([{"category_id": "1", "category_name": "TV EN VIVO"}])
    
    if action == "get_live_streams":
        streams = []
        # Buscamos canales que NO sean películas
        matches = re.findall(r'#EXTINF:.*,(.*)\n(http.*)', m3u_content)
        for i, (name, url) in enumerate(matches):
            if "PELICULA" not in name.upper():
                streams.append({
                    "num": i, "name": name.strip(), "stream_id": i,
                    "category_id": "1", "direct_source": url.strip()
                })
        return jsonify(streams)

    # Respuesta para Películas
    if action == "get_vod_categories":
        return jsonify([{"category_id": "2", "category_name": "PELICULAS"}])
    
    if action == "get_vod_streams":
        vods = []
        matches = re.findall(r'#EXTINF:.*,(.*)\n(http.*)', m3u_content)
        for i, (name, url) in enumerate(matches):
            if "PELICULA" in name.upper():
                vods.append({
                    "num": i, "name": name.strip(), "stream_id": i + 1000,
                    "category_id": "2", "direct_source": url.strip(), "container_extension": "mp4"
                })
        return jsonify(vods)

    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

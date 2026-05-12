from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# CONFIGURACIÓN
GITHUB_M3U_URL = "https://bit.ly/4t9rqok"

@app.route('/')
def index():
    return "Servidor de Codigo Master TV Activo ✅"

@app.route('/player_api.php')
def player_api():
    username = request.args.get('username')
    password = request.args.get('password')
    action = request.args.get('action')

    # Credenciales
    if username != "admin" or password != "master":
        return jsonify({"error": "Auth failed"}), 401

    if not action:
        return jsonify({
            "user_info": {"status": "Active", "auth": 1, "username": "admin"},
            "server_info": {"url": "Codigo Master TV", "port": "80", "server_protocol": "http"}
        })

    # Simulación de respuesta para que la app conecte
    if action == "get_live_categories":
        return jsonify([{"category_id": "1", "category_name": "TV EN VIVO"}])
    
    if action == "get_vod_categories":
        return jsonify([{"category_id": "2", "category_name": "PELÍCULAS"}])

    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

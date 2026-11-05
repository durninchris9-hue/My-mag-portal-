import os
import requests
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

def fetch_and_parse_m3u(file_id):
    channels = []
    url = f"https://google.com{file_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return channels
        
        lines = response.text.splitlines()
        current_channel = {}
        for line in lines:
            line = line.strip()
            if line.startswith("#EXTINF:"):
                parts = line.split(',')
                current_channel['name'] = parts[-1] if parts else "Live Channel"
            elif line.startswith("http"):
                current_channel['url'] = line
                channels.append(current_channel)
                current_channel = {}
    except Exception as e:
        print(f"Error parsing M3U: {e}")
    return channels

@app.route('/portal.php')
def stalker_portal():
    req_type = request.args.get('type', '')
    action = request.args.get('action', '')
    drive_id = request.args.get('id', '')
    
    if req_type == 'stb':
        if action == 'handshake':
            return jsonify({
                "js": {
                    "token": "987654321ABC",
                    "status": 1,
                    "timezone": "Europe/London",
                    "results": True
                }
            })
            
        elif action == 'get_profile':
            return jsonify({
                "js": {
                    "name": "Custom IPTV Portal",
                    "password": "",
                    "logo": "",
                    "active": True,
                    "parent_password": "0000"
                }
            })
            
        elif action == 'get_localization':
            return jsonify({
                "js": {
                    "results": True,
                    "strings": {"all": "All"}
                }
            })

        elif action == 'get_modules':
            return jsonify({
                "js": {
                    "disabled": [],
                    "enabled": ["tv", "vclub"]
                }
            })

        elif action == 'get_categories':
            return jsonify({
                "js": [{"id": "1", "title": "All Channels"}]
            })
            
        elif action == 'get_ordered_iptv_all':
            raw_channels = fetch_and_parse_m3u(drive_id)
            stalker_channels = []
            for index, ch in enumerate(raw_channels, start=1):
                stalker_channels.append({
                    "id": str(index),
                    "name": ch.get('name', 'Live Channel'),
                    "cmd": f"ffmpeg {ch.get('url', '')}",
                    "tv_genre_id": "1",
                    "open": 1,
                    "status": 1
                })
            return jsonify({
                "js": {
                    "total_items": len(stalker_channels),
                    "max_page_items": 5000,
                    "data": stalker_channels
                }
            })

    response = make_response("Custom MAG Portal Server Active", 200)
    response.headers['Content-Type'] = 'text/plain'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
                                     


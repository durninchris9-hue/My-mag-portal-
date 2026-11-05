import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# PASTE YOUR DIRECT GOOGLE DRIVE DOWNLOAD LINK BETWEEN THE QUOTES
M3U_URL = "YOUR_DIRECT_GOOGLE_DRIVE_LINK_HERE"

def fetch_and_parse_m3u(url):
    channels = []
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
                current_channel['name'] = parts[-1] if parts else "Unknown Channel"
            elif line.startswith("http"):
                current_channel['url'] = line
                channels.append(current_channel)
                current_channel = {}
                
    except Exception as e:
        print(f"Error parsing M3U: {e}")
    return channels

@app.route('/portal.php')
def stalker_portal():
    action = request.args.get('action', '')
    mac = request.args.get('mac', 'Unknown')
    
    raw_channels = fetch_and_parse_m3u(M3U_URL)
    
    if action == 'handshake':
        return jsonify({
            "js": {
                "token": "session-token-12345",
                "user_id": "1"
            }
        })
    
    elif action == 'get_categories':
        return jsonify({
            "js": [{"id": "1", "title": "All Channels"}]
        })
    
    elif action == 'get_ordered_iptv_all':
        stalker_channels = []
        for index, ch in enumerate(raw_channels, start=1):
            stalker_channels.append({
                "id": str(index),
                "name": ch.get('name', 'Live Channel'),
                "cmd": f"ffmpeg {ch.get('url', '')}",
                "tv_genre_id": "1"
            })
        return jsonify({"js": {"data": stalker_channels}})
    
    return jsonify({"js": True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


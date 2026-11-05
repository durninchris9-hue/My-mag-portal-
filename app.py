import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# This dictionary holds all your different Google Drive File IDs
# You can add as many as you want here!
PLAYLISTS = {
    "trex": "13N_0_BCJc9f20jicT3A4QkOb2mrgTVU7",
    "backup": "YOUR_OTHER_FILE_ID_HERE",
    "kids": "ANOTHER_FILE_ID_HERE"
}

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
    
    # This reads the custom name you type into your MAG box URL!
    list_name = request.args.get('list', 'trex').lower()
    file_id = PLAYLISTS.get(list_name, PLAYLISTS['trex'])
    
    raw_channels = fetch_and_parse_m3u(file_id)
    
    if action == 'handshake':
        return jsonify({"js": {"token": "session-token-12345", "user_id": "1"}})
    elif action == 'get_categories':
        return jsonify({"js": [{"id": "1", "title": "All Channels"}]})
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
    


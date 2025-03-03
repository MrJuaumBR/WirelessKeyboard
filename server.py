"""
Use your browser from your cellphone as your remote wireless keyboard
"""

from flask import render_template, Flask, request, jsonify
import jinja2.filters
from werkzeug.serving import get_interface_ip
import keyboard, jinja2
from socket import AF_INET
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoInitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Filters
jinja2.filters.FILTERS['rnd0'] = lambda x: round(x, 0)

# Load Application
app = Flask(__name__)
app.template_folder = './data/pages/'
app.static_folder = './data/static/'

# Objects
class configdata:
    volume:float = 1.0
    def key(self, data:dict):
        shift, control, alt = data['shift'] or False, data['control'] or False, data['alt'] or False
        key = data['key'] or None
        if key:
            if shift:
                key = 'shift+' + key
            if control:
                key = 'ctrl+' + key
            if alt:
                key = 'alt+' + key
            try:
                keyboard.press_and_release(key)
            except Exception as e: print(e)
    
cdata = configdata()
# Pages
@app.route('/')
def index():
    
    return render_template('index.html',data=cdata)

# Api
@app.route('/api/key', methods=['POST'])
def key():
    data = request.get_json()
    print(data)
    cdata.key(data)
    return jsonify({'success': True})

@app.route('/api/update_volume', methods=['POST'])
def update_volume():
    data = request.get_json()
    volume = data['volume']
    cdata.volume = float(volume)/100
    return jsonify({'success': True})

# Run Server
def run():
    app.run(host='0.0.0.0', port=3000, debug=True)
    
run()
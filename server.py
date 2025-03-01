from flask import render_template, Flask, request, redirect, url_for, jsonify
import os, keyboard
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoInitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from jinja2 import filters

app = Flask(__name__)
app.template_folder = './data/html/'
app.static_folder = './data/static/'

filters.FILTERS['rnd0'] = lambda x: round(x, 0)

keyslines:list[list[str,]] = [
    ['F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12'],
    ['1','2','3','4','5','6','7','8','9','0','-','='],
    ['q','w','e','r','t','y','u','i','o','p','[',']'],
    ['a','s','d','f','g','h','j','k','l',';','\'','\\'],
    ['z','x','c','v','b','n','m',',','.','/']
]

def get_volume() -> cast:
    try:
        CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        c = cast(interface, POINTER(IAudioEndpointVolume))
        return c
    except Exception as e:
        print(e)
        return None
def get_volume_level() -> float:
    try:
        volume = get_volume()
        return volume.GetMasterVolumeLevelScalar()
    except Exception as e:
        print(e)
        return 0

class KeyControl:
    def __init__(self):
        self.control = False
        self.shift = False
        self.alt = False
        
    def event(self,data:dict):
        self.control = data['control'] or False
        self.shift = data['shift'] or False
        self.alt =  data['alt'] or False
        key = data['key'] or None
        self.run_key(key)
        
    def run_key(self, key:str):
        try:
            key = key.lower()
            if self.control:
                key = 'ctrl+' + key
            if self.shift:
                key = 'shift+' + key
            if self.alt:
                key = 'alt+' + key
            if key:
                keyboard.press_and_release(key)
        except Exception as e: print(e)
        
        
KCL = KeyControl()
        
@app.route('/')
def index():
    # if request.method == 'POST':
        # KCL.event(request.form)
        
    return render_template('home.html',keysline=keyslines,volume=get_volume_level())

@app.route('/key', methods=['POST'])
def key():
    data = request.get_json()
    KCL.event(data)
    return jsonify({'success': True})

@app.route('/update_volume', methods=['POST'])
def update_volume():
    data = request.get_json()
    volume = data['volume']
    v = get_volume()
    v.SetMasterVolumeLevelScalar(int(volume)/100, None)
    return jsonify({'success': True})

def run():
    app.run(host='0.0.0.0', port=3000, debug=True)
    
if __name__ == '__main__':
    run()
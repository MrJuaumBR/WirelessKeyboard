"""
Use your browser from your cellphone as your remote wireless keyboard
"""

from flask import render_template, Flask, request, jsonify
import jinja2.filters
from socket import AF_INET
from werkzeug.serving import get_interface_ip
import keyboard, jinja2, os,json, sys, threading
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoInitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Args
AUTORUN:bool = False
if len(sys.argv) > 1:
    if '--startup' in sys.argv:
        AUTORUN:bool = True


# Filters
jinja2.filters.FILTERS['rnd0'] = lambda x: round(x, 0)

# Load Application
app = Flask(__name__)
app.template_folder = './data/pages/'
app.static_folder = './data/static/'
path_root = os.path.dirname(os.path.realpath(__file__))

# Objects
class configdata:
    volume:float = 1.0
    port:int = 3000
    startup:bool = False
    autoopen:bool = False
    def __init__(self):
        self.volume:float = 1.0
        self.port:int = 3000
        self.startup:bool = False
        self.autoopen:bool = False
        self.path_root = path_root
        self.try_load()
        self.detect_volume()
    
    def generate_auto_run_file(self):
        if not AUTORUN:
            try:
                with open(f'{path_root}/data/autostart.bat','w+') as f:
                    f.writelines([
                        '@echo off\n',
                        'echo Starting Internal Server...\n',
                        f'python {path_root}\server.py --startup\n'
                        ])
                    f.close()
            except: pass
    
    def try_load(self):
        if os.path.exists(f'{path_root}/data/config.json'):
            with open(f'{path_root}/data/config.json','rb') as f:
                data = json.loads(f.read())
            for key in data.keys():
                self.__dict__[key] = data[key]
        else:
            data = {}
            for key in self.__dict__.keys():
                data[key] = self.__dict__[key]
            with open(f'{path_root}/data/config.json','w+') as f:
                f.write(json.dumps(data,sort_keys=True, indent=2))
                f.close()
                
        if self.startup:
            self.update_startup(self.startup)
    
    def update_startup(self, value:bool):
        self.generate_auto_run_file()
        dest = os.path.expanduser(r'~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\autostart.bat')
        if value:
            try:
                os.rename(f'{path_root}/data/autostart.bat',dest)
                self.auto_run_file = str(dest)
            except Exception as e: print(e)
        else:
            try:
                if os.path.exists(dest):
                    os.remove(dest)
                self.auto_run_file = 'Disabled'
            except Exception as e: print(e)
    
    def set(self, key:str, value:any):
        if key in self.__dict__.keys():
            if key == 'volume':
                value = float(value)
            elif key == 'port':
                value = int(value)
            elif key == 'startup':
                value = bool(value)
                self.update_startup(value)
            elif key == 'autoopen':
                value = bool(value)
            self.__dict__[key] = value
            self.update_config()
    
    def update_config(self):
        data = {}
        for key in self.__dict__.keys():
            data[key] = self.__dict__[key]
        with open(f'{path_root}/data/config.json','w+') as f:
            f.write(json.dumps(data,sort_keys=True, indent=2))
            f.close()
        
    def detect_volume(self):
        CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.volume = volume.GetMasterVolumeLevelScalar()
        
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
    

@app.route('/config')
def config():
    return render_template('config.html',data=cdata)

# Api
@app.route('/api/update_config', methods=['POST'])
def update_config():
    data = request.get_json()
    try:
        cdata.set(data['keyname'], data['keyvalue'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
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
    # Update device volume
    CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(cdata.volume, None)
    return jsonify({'success': True})

# Run Server

def openit():
    url = f'http://{get_interface_ip(AF_INET)}:{cdata.port}'
    if cdata.autoopen: os.system(f'start {url}')
def run():
    if __name__ == '__main__':
        threading.Timer(1, function=openit).start()
        app.run(host='0.0.0.0', port=cdata.port, debug=True)
    
    
run()
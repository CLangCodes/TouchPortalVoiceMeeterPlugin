import socket
import threading
import json
import time
import ctypes
import os
import sys

# --- Voicemeeter API Setup ---
def get_voicemeeter_dll_path():
    # Try to find Voicemeeter install path from registry (Windows only)
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Voicemeeter {17359A74-1236-5467}") as key:
            install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
            if sys.maxsize > 2**32:
                dll = os.path.join(install_path, "VoicemeeterRemote64.dll")
            else:
                dll = os.path.join(install_path, "VoicemeeterRemote.dll")
            return dll
    except Exception as e:
        print("Could not find Voicemeeter install path:", e)
        return None

dll_path = get_voicemeeter_dll_path()
if not dll_path or not os.path.exists(dll_path):
    raise RuntimeError("VoicemeeterRemote DLL not found. Is Voicemeeter installed?")

vmr = ctypes.CDLL(dll_path)

# Function prototypes
vmr.VBVMR_Login.restype = ctypes.c_long
vmr.VBVMR_Logout.restype = ctypes.c_long
vmr.VBVMR_GetParameterFloat.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_float)]
vmr.VBVMR_GetParameterFloat.restype = ctypes.c_long

def voicemeeter_login():
    return vmr.VBVMR_Login()

def voicemeeter_logout():
    return vmr.VBVMR_Logout()

def get_strip0_b1():
    value = ctypes.c_float()
    param = b"Strip[0].B1"
    res = vmr.VBVMR_GetParameterFloat(param, ctypes.byref(value))
    if res == 0:
        return value.value
    else:
        return None

# --- Touch Portal Socket Server ---
class TouchPortalPlugin:
    def __init__(self, host='127.0.0.1', port=12136):
        self.host = host
        self.port = port
        self.sock = None
        self.client = None
        self.running = True
        self.last_b1 = None

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f"Listening for Touch Portal on {self.host}:{self.port}")
        self.client, addr = self.sock.accept()
        print(f"Connected to Touch Portal: {addr}")
        threading.Thread(target=self.poll_voicemeeter, daemon=True).start()
        self.listen()

    def listen(self):
        while self.running:
            try:
                if self.client is None:
                    print("No client connected, stopping listen loop.")
                    break
                data = self.client.recv(4096)
                if not data:
                    break
                # Handle incoming messages if needed
                print("Received:", data.decode('utf-8').strip())
            except Exception as e:
                print("Socket error:", e)
                break
    def send_state(self, state):
        if self.client is None:
            print("No client connected, cannot send state.")
            return
        msg = {
            "type": "stateUpdate",
            "id": "voicemeeter_strip0_b1",
            "value": state
        }
        try:
            self.client.sendall((json.dumps(msg) + "\n").encode('utf-8'))
        except Exception as e:
            print("Send error:", e)

    def poll_voicemeeter(self):
        voicemeeter_login()
        try:
            while self.running:
                b1 = get_strip0_b1()
                if b1 is not None:
                    state = "on" if b1 >= 1.0 else "off"
                    if state != self.last_b1:
                        self.send_state(state)
                        self.last_b1 = state
                time.sleep(0.5)
        finally:
            voicemeeter_logout()

if __name__ == "__main__":
    plugin = TouchPortalPlugin()
    plugin.start() 
# TouchPortalVoiceMeeterPlugin

A Touch Portal plugin (mod) in Python to interface with Voicemeeter Banana via its Remote API. This plugin polls the status of `Strip[0].B1` every 500ms and reports its state (on/off) to Touch Portal.

## Features
- Polls Voicemeeter Banana's `Strip[0].B1` parameter every 500ms
- Communicates with Touch Portal using the official socket/JSON protocol
- Ready for further expansion (add more Voicemeeter controls or Touch Portal actions)

## Requirements
- Windows OS
- [Voicemeeter Banana](https://www.vb-audio.com/Voicemeeter/banana.htm) installed and running
- Python 3.8+
- `pywin32` (for registry access)

## Setup
1. Ensure Voicemeeter Banana is installed and running.
2. Place this plugin in a directory of your choice.
3. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the plugin:
   ```sh
   python plugin.py
   ```
5. Configure Touch Portal to connect to the plugin (default port: 12136).

## Customization
- You can change the polling interval or add more Voicemeeter parameters in `plugin.py`.

## License
MIT 
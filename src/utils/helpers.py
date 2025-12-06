import json
from pathlib import Path

def load_tickers(config_path="src/config/tickers.json"):

    with open(config_path) as f:
        data=json.load(f)
        
    return data.get("tickers",[])

import sys
import yfinance as yf
import pandas as pd
from pathlib import Path
from src.utils.helpers import load_tickers


def extract(start_date, end_date, output_dir="data/raw"):

    tickers = load_tickers()

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for t in tickers:
        
        print(f"Baixando dados de: {t}...")
        df = yf.download(t + ".SA", start=start_date, end=end_date)

        if df.empty:
            print(f"Nenhum dado retornado para {t}.")
            continue

        df.reset_index(inplace=True)
        output_path = f"{output_dir}/{t}.parquet"
        df.to_parquet(output_path, index=False)

        print(f"Arquivo salvo: {output_path}")


if __name__ == "__main__":

    # Se chamou sem argumentos: mostra instrução
    if len(sys.argv) != 3:
        print("Uso correto:")
        print("   python extract_yfinance.py 2025-11-01 2025-12-06")
        sys.exit(1)

    start = sys.argv[1]
    end = sys.argv[2]

    extract(start, end)

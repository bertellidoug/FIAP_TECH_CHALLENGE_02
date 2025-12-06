import sys
import yfinance as yf
import pandas as pd
from pathlib import Path
from src.utils.helpers import load_tickers


def extract(start_date, end_date, output_dir="data/raw"):

    # O nome da pasta base onde a partição se inicia
    base_output_dir = Path(output_dir)
    base_output_dir.mkdir(parents=True, exist_ok=True)

    tickers = load_tickers()

    for t in tickers:
        
        print(f"Baixando dados de: {t} de {start_date} a {end_date}...")
        
        # 1. Baixa o bloco completo (Data é o Index)
        df_full = yf.download(t + ".SA", start=start_date, end=end_date)

        if df_full.empty:
            print(f"Nenhum dado retornado para {t}.")
            continue

        # 2. Reseta o Index para ter a coluna 'Date' para particionar
        df_full.reset_index(inplace=True)
        
        # 3. Itera sobre CADA DIA presente no DataFrame
        #    Agrupa o DataFrame completo pela coluna 'Date'
        for date, df_day in df_full.groupby('Date'):
            
            # Converte a data (Timestamp) para string no formato YYYY-MM-DD
            date_str = date.strftime('%Y-%m-%d')
            
            # Constrói o caminho de partição, simulando o S3:
            # {output_dir}/ticker=PETR4/date=2025-12-05/file.parquet
            
            # Estrutura completa: data/raw/ticker=PETR4/date=2025-12-05/
            partition_path = base_output_dir / f"ticker={t}" / f"date={date_str}"
            
            # Garante que o diretório de saída existe (data/raw/ticker=X/date=Y/)
            partition_path.mkdir(parents=True, exist_ok=True)
            
            # Define o nome do arquivo final
            output_file_name = f"{t}_{date_str}.parquet"
            output_path = partition_path / output_file_name
            
            # Salva o DataFrame que contém APENAS os dados daquele dia
            df_day.to_parquet(output_path, index=False)

            print(f"-> Salvo: {output_path}")

        print(f"Concluído o download e salvamento particionado para o ticker: {t}")


if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("Uso correto:")
        print("    python extract_yfinance.py 2025-11-01 2025-12-06")
        sys.exit(1)

    start = sys.argv[1]
    end = sys.argv[2]
    
    # Executa a função modificada
    extract(start, end)
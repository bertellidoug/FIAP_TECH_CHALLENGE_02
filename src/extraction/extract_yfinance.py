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

        df_full['ticker'] = t

        new_columns = []
        for col in df_full.columns:

            if isinstance(col, tuple):

                # Pega o primeiro item ('Close'), ignora o ticker, e joga para minúsculo
                clean_col = col[0].lower().strip()

                # Correção específica para caso o reset_index tenha gerado ('Date', '')
                if clean_col == 'date': 
                    clean_col = 'date'

                new_columns.append(clean_col)
            else:
                new_columns.append(str(col).lower().strip())
        
        df_full.columns = new_columns

        if 'date' in df_full.columns:
            df_full['date'] = df_full['date'].astype('datetime64[us]')        
        
        # 3. Itera sobre CADA DIA presente no DataFrame
        #    Agrupa o DataFrame completo pela coluna 'Date'
        for date, df_day in df_full.groupby('date'):
            
            # Converte a data (Timestamp) para string no formato YYYY-MM-DD
            date_str = date.strftime('%Y-%m-%d')
            
           
            # Estrutura completa: data/raw/ticker=PETR4/date=2025-12-05/
            partition_path = base_output_dir / f"ticker={t}" / f"date={date_str}"
            
            # Garante que o diretório de saída existe (data/raw/ticker=X/date=Y/)
            partition_path.mkdir(parents=True, exist_ok=True)
            
            # Define o nome do arquivo final
            output_file_name = f"{t}_{date_str}.parquet"
            output_path = partition_path / output_file_name

            df_final = df_day.copy()

            if 'date' in df_final.columns:
                df_final.rename(columns={'date': 'data_pregao'}, inplace=True)

            if 'data_pregao' in df_final.columns:
                df_final['data_pregao'] = df_final['data_pregao'].astype(str)
            
            # Salva o DataFrame que contém APENAS os dados daquele dia
            df_final.to_parquet(output_path, allow_truncated_timestamps=True, 
                              coerce_timestamps='us',
                              index=False)

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
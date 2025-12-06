# B3 Batch Pipeline – Tech Challenge FIAP

Projeto para construção de um pipeline batch completo utilizando:

- AWS S3
- AWS Glue
- AWS Lambda
- AWS Athena
- Python + yfinance

Arquitetura:

1. Extração de dados de ações da B3 (granularidade diária)
2. Salvamento em parquet particionado
3. Upload para S3 (raw zone)
4. Disparo automático de Lambda ao novo arquivo
5. Lambda inicia Job AWS Glue
6. Glue aplica transformações e salva no S3 (refined zone)
7. Glue Catalog cria tabela automaticamente
8. Consulta via SQL no Athena

b3_pipeline/
│
├── README.md
├── requirements.txt
│
├── src/
│   ├── extraction/
│   │   └── extract_yfinance.py
│   │
│   ├── utils/
│   │   └── helpers.py
│   │
│   └── config/
│       └── tickers.json
│
├── data/
│   └── raw/         -> (onde cairão os parquet locais para teste)
│
└── notebooks/
    └── exploration.ipynb

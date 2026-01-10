# Tech Challenge 02 - Ingestão e Arquitetura de Dados Bovespa

## 1. Introdução
Este projeto apresenta uma solução completa de engenharia de dados para o processamento em lote (batch) de ativos da B3. O objetivo principal é extrair dados brutos, processá-los seguindo as melhores práticas de Data Lakehouse e disponibilizá-los para análise via SQL, utilizando a stack tecnológica da AWS.

## 2. Arquitetura da Solução

O pipeline foi desenhado para ser totalmente orientado a eventos (Event-Driven):

1.  **Extraction Layer:** Script Python local utilizando `yfinance`.
2.  **Storage Layer (Raw):** AWS S3 armazenando dados brutos em Parquet com particionamento Hive-Style.
3.  **Compute Layer:** AWS Lambda atuando como trigger para o AWS Glue.
4.  **ETL Layer:** AWS Glue realizando transformações Spark (SQL, Rename e Aggregation).
5.  **Serving Layer:** Amazon Athena para consultas analíticas via SQL.

---

## 3. Estrutura do Projeto

A organização do código segue princípios de modularidade:

```text
├── data/
│   └── raw/                # Arquivos Parquet locais gerados pelo extrator
├── src/
│   ├── config/
│   │   └── tickers.json    # Configuração dos ativos a serem monitorados
│   ├── extraction/
│   │   └── extract_yfinance.py  # Script de extração e particionamento
│   └── utils/
│       └── helpers.py      # Funções auxiliares (carregamento de tickers)
├── README.md
```

## 4. Detalhes da Implementação
Extração de Dados (extract_yfinance.py)
Diferente de uma extração simples, o motor de extração foi desenvolvido para preparar o dado para a nuvem:

Tratamento de Cabeçalhos: Limpeza de colunas MultiIndex geradas pelo yfinance.

Particionamento Manual: O script quebra o DataFrame original em arquivos diários, organizados por pastas no formato ticker=X/date=Y. Isso garante que o Glue e o Athena leiam apenas os dados necessários.

Tipagem Estrita: Conversão de colunas de data para datetime64[us] e posterior string para evitar incompatibilidade de tipos no S3 Select/Glue.

Transformações Obrigatórias (AWS Glue)
Dentro do Job Glue, foram aplicadas as seguintes lógicas:

A - Agrupamento: Sumarização do volume transacionado agrupado por ativo e data.

B - Rename: Padronização das colunas (ex: close para preco_fechamento).

C - Cálculo Temporal: Implementação de uma Window Function em SQL para calcular a média móvel de 7 dias:

```
AVG(preco_fechamento) OVER (PARTITION BY ticker ORDER BY data_pregao ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
```

## 5. Como Executar o Pipeline
Passo 1: Extração Local
Certifique-se de configurar os ativos desejados no tickers.json e execute:

```
python extract_yfinance.py 2025-11-01 2025-12-06
```

Passo 2: Sincronização S3
Envie a pasta data/raw para o seu bucket S3:

```
aws s3 sync data/raw s3://seu-bucket-fiap/raw/
```

Passo 3: Consulta Athena
Após o processamento automático, os dados estarão disponíveis no banco de dados default:

```
SELECT * FROM "default"."tbl_bovespa_refined" LIMIT 10;
```

## 6. Checklist de Requisitos (Status)
[x] Requisito 1: Scrap de dados da B3 (yfinance).
[x] Requisito 2: Ingestão S3 em formato Parquet com partição diária.
[x] Requisito 3 & 4: Lambda acionando o Glue Job via Trigger S3.
[x] Requisito 5: Job ETL com Agrupamento, Rename e Média Móvel.
[x] Requisito 6: Dados salvos na pasta /refined em Parquet.
[x] Requisito 7: Catalogação automática no Glue Catalog.
[x] Requisito 8: Consultas SQL disponíveis via Athena.
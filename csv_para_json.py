import pandas as pd

# === Caminho do CSV original ===
csv_path = "livros.csv"

# === Caminho de saída do JSON ===
json_path = "livros_corrigidos.json"

# === Leitura do CSV ===
df = pd.read_csv(
    csv_path,
    quotechar='"',            # respeita campos entre aspas
    skip_blank_lines=True,
    encoding="utf-8",         # ajuste se necessário
)

# === Limpeza dos campos esperados ===
for col in ['TITULO', 'AUTOR', 'ARMARIO', 'PRATILEIRA']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    else:
        print(f"⚠️ Atenção: coluna '{col}' não encontrada no CSV!")

# === Exportação para JSON ===
df[['TITULO', 'AUTOR', 'ARMARIO', 'PRATILEIRA']].to_json(
    json_path,
    orient="records",
    force_ascii=False,
    indent=2
    
)

print(f"✅ JSON gerado com sucesso: {json_path}")

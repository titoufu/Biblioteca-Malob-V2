import mysql.connector
import subprocess
import csv
import pandas as pd
import os

# === CONFIGURAÇÕES ===
mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
sql_file = r"C:\Users\jribe\Biblioteca-Malob-V2\livro.sql"
csv_output = r"C:\Users\jribe\Biblioteca-Malob-V2\livros.csv"
json_output = r"C:\Users\jribe\Biblioteca-Malob-V2\livros_corrigidos.json"
host = "localhost"
user = "root"
password = "Tito1k58!"
database = "biblioteca"

# === ETAPA 1: Recriar banco de dados ===
print("[1/4] Recriando banco...")
cmd1 = f'"{mysql_path}" -u {user} -p"{password}" -e "DROP DATABASE IF EXISTS {database}; CREATE DATABASE {database} CHARACTER SET latin1 COLLATE latin1_general_ci;"'
subprocess.run(cmd1, shell=True, check=True)

# === ETAPA 2: Importar arquivo SQL ===
print("[2/4] Importando arquivo SQL...")
cmd2 = f'cmd.exe /c "type \"{sql_file}\" | \"{mysql_path}\" --default-character-set=latin1 -u {user} -p{password} {database}"'
subprocess.run(cmd2, shell=True, check=True)

# === ETAPA 3: Exportar tabela para CSV ===
print("[3/4] Exportando para CSV...")
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

cursor = conn.cursor()
cursor.execute("SELECT TITULO, AUTOR, ARMARIO, PRATILEIRA FROM livro")

with open(csv_output, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['TITULO', 'AUTOR', 'ARMARIO', 'PRATILEIRA'])
    for row in cursor.fetchall():
        writer.writerow(row)

cursor.close()
conn.close()

# === ETAPA 4: Gerar JSON a partir do CSV ===
print("[4/4] Convertendo CSV para JSON corrigido...")
df = pd.read_csv(csv_output, quotechar='"', skip_blank_lines=True, encoding="utf-8")

for col in ['TITULO', 'AUTOR', 'ARMARIO', 'PRATILEIRA']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

df[['TITULO', 'AUTOR', 'ARMARIO', 'PRATILEIRA']].to_json(
    json_output,
    orient="records",
    force_ascii=False,
    indent=2
)

print(f"✅ Processo completo concluído com sucesso!")
print(f"📄 CSV gerado: {csv_output}")
print(f"📄 JSON gerado: {json_output}")

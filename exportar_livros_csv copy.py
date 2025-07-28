import mysql.connector
import subprocess
import csv

# === CONFIGURAÇÕES ===
mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
sql_file = r"C:\Users\jribe\Biblioteca-Malob-V2\livro.sql"
csv_output = r"C:\Users\jribe\Biblioteca-Malob-V2\livros.csv"
host = "localhost"
user = "root"
password = "Tito1k58!"
database = "biblioteca"

# === ETAPA 1: Recriar banco de dados ===
print("[1/3] Recriando banco...")
cmd1 = f'"{mysql_path}" -u {user} -p"{password}" -e "DROP DATABASE IF EXISTS {database}; CREATE DATABASE {database} CHARACTER SET latin1 COLLATE latin1_general_ci;"'
subprocess.run(cmd1, shell=True, check=True)

# === ETAPA 2: Importar arquivo SQL (modo latin1, com cmd.exe + pipe)
print("[2/3] Importando arquivo SQL como latin1...")
cmd2 = rf'''cmd.exe /c "type "{sql_file}" | "{mysql_path}" -u {user} -p{password} {database}"'''
subprocess.run(cmd2, shell=True, check=True)


# === ETAPA 3: Exportar para CSV ===
print("[3/3] Exportando livros.csv...")
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

cursor = conn.cursor()
cursor.execute("SELECT TITULO, AUTOR, ARMARIO, PRATILEIRA FROM livro")

with open(csv_output, mode='w', newline='', encoding='utf-8') as file:  # ou 'latin1'
    writer = csv.writer(file)
    writer.writerow(['TITULO', 'AUTOR', 'ARMARIO', 'PRATILEIRA'])
    for row in cursor.fetchall():
        writer.writerow(row)

cursor.close()
conn.close()
print(f"✅ Exportação concluída: {csv_output}")

import mysql.connector
import subprocess
import csv

# === CONFIGURAÇÕES ===
mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
sql_file = r"F:\TitoDocumentos\Doutrina\MariaLobato\BancoDeDadosBiblioteca\BancoLibraryMalob.sql"
csv_output = r"F:\TitoDocumentos\Doutrina\MariaLobato\BancoDeDadosBiblioteca\livros.csv"
host = "localhost"
user = "root"
password = "Tito1k58!"
database = "biblioteca"

# === ETAPA 1: Recriar banco de dados ===
print("[1/3] Recriando banco...")
cmd1 = f'"{mysql_path}" -u {user} -p"{password}" -e "DROP DATABASE IF EXISTS {database}; CREATE DATABASE {database};"'
subprocess.run(cmd1, shell=True, check=True)

# === ETAPA 2: Importar arquivo SQL ===
print("[2/3] Importando arquivo SQL...")
cmd2 = f'"{mysql_path}" -u {user} -p"{password}" {database} -e "source \"{sql_file}\""'
subprocess.run(cmd2, shell=True, check=True)

# === ETAPA 3: Conectar e exportar para CSV ===
print("[3/3] Exportando livros.csv...")
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

print(f"✅ Exportação concluída: {csv_output}")

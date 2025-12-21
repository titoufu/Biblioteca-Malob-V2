import mysql.connector
import subprocess
import csv
import pandas as pd
import json
import re
import unicodedata
from pathlib import Path

# ================== CONFIGURAÇÕES ==================
mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

# Diretório onde serão salvos CSV/JSON e o SQL normalizado
out_dir = r"F:\TitoDocumentos\Doutrina\MariaLobato\BancoDeDadosBiblioteca"
Path(out_dir).mkdir(parents=True, exist_ok=True)

# Saídas
sql_normalizado = str(Path(out_dir) / "livro_normalizado.sql")
csv_output      = str(Path(out_dir) / "livros.csv")
json_records    = str(Path(out_dir) / "livros.json")
json_index      = str(Path(out_dir) / "livros_index.json")

# MySQL
host     = "localhost"
user     = "root"
password = "Tito1k58!"   # ⚠️ troque isso depois (senha apareceu no chat)
database = "biblioteca"

# Query
QUERY = "SELECT TITULO, AUTOR, ARMARIO, PRATILEIRA FROM livro"

# Índice por prefixo (para busca rápida no front)
PREFIX_MIN = 2
PREFIX_MAX = 5
MAX_IDS_PER_PREFIX = 5000


# ================== PROMPT: ARQUIVO SQL ORIGINAL ==================
sql_original = input(
    "Informe o CAMINHO COMPLETO + NOME do arquivo SQL original (ex: F:\\pasta\\arquivo.sql): "
).strip().strip('"')

sql_original = str(Path(sql_original))

if not Path(sql_original).is_file():
    raise FileNotFoundError(f"Arquivo SQL não encontrado: {sql_original}")

print(f"📄 Arquivo SQL selecionado: {sql_original}")


# ================== FUNÇÕES ==================
def normalize_text(s: str) -> str:
    """Normaliza texto para busca (minúsculas, sem acento, só letras/números/espaço)."""
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def add_prefixes(index_map: dict, text_norm: str, item_id: int):
    """Indexa por prefixos do texto (2..5 letras por padrão)."""
    if not text_norm:
        return

    # prefixos do texto inteiro
    for L in range(PREFIX_MIN, min(PREFIX_MAX, len(text_norm)) + 1):
        pref = text_norm[:L]
        lst = index_map.setdefault(pref, [])
        if (not lst or lst[-1] != item_id) and len(lst) < MAX_IDS_PER_PREFIX:
            lst.append(item_id)

    # prefixos do primeiro token (ajuda em autor)
    first = text_norm.split(" ", 1)[0]
    if first and first != text_norm:
        for L in range(PREFIX_MIN, min(PREFIX_MAX, len(first)) + 1):
            pref = first[:L]
            lst = index_map.setdefault(pref, [])
            if (not lst or lst[-1] != item_id) and len(lst) < MAX_IDS_PER_PREFIX:
                lst.append(item_id)


def gerar_sql_normalizado(sql_in: str, sql_out: str):
    """
    Lê o SQL original (tenta utf-8; se falhar, latin1) e grava uma versão em UTF-8,
    ajustando:
      - SET NAMES latin1/utf8/utf8mb3 -> SET NAMES utf8mb4
      - DEFAULT CHARSET=latin1/utf8/utf8mb3 -> DEFAULT CHARSET=utf8mb4
      - CHARSET=latin1/utf8 -> CHARSET=utf8mb4
      - SUBTITULO (no CREATE TABLE livro) -> VARCHAR(512)  (evita ERROR 1406)
    """
    p_in = Path(sql_in)

    try:
        raw = p_in.read_text(encoding="utf-8")
        origem = "utf-8"
    except UnicodeDecodeError:
        raw = p_in.read_text(encoding="latin1")
        origem = "latin1"

    txt = raw

    # SET NAMES (inclui variações com /*!40101 ... */;)
    txt = re.sub(r"(?i)SET\s+NAMES\s+latin1\s*;", "SET NAMES utf8mb4;", txt)
    txt = re.sub(r"(?i)SET\s+NAMES\s+utf8\s*;", "SET NAMES utf8mb4;", txt)
    txt = re.sub(r"(?i)SET\s+NAMES\s+utf8mb3\s*;", "SET NAMES utf8mb4;", txt)

    txt = re.sub(r"(?i)/\*!\s*\d+\s+SET\s+NAMES\s+latin1\s*\*/\s*;", "SET NAMES utf8mb4;", txt)
    txt = re.sub(r"(?i)/\*!\s*\d+\s+SET\s+NAMES\s+utf8\s*\*/\s*;", "SET NAMES utf8mb4;", txt)
    txt = re.sub(r"(?i)/\*!\s*\d+\s+SET\s+NAMES\s+utf8mb3\s*\*/\s*;", "SET NAMES utf8mb4;", txt)

    # DEFAULT CHARSET / CHARSET
    txt = re.sub(r"(?i)DEFAULT\s+CHARSET\s*=\s*latin1", "DEFAULT CHARSET=utf8mb4", txt)
    txt = re.sub(r"(?i)DEFAULT\s+CHARSET\s*=\s*utf8mb3", "DEFAULT CHARSET=utf8mb4", txt)
    txt = re.sub(r"(?i)DEFAULT\s+CHARSET\s*=\s*utf8\b", "DEFAULT CHARSET=utf8mb4", txt)

    txt = re.sub(r"(?i)\bCHARSET\s*=\s*latin1\b", "CHARSET=utf8mb4", txt)
    txt = re.sub(r"(?i)\bCHARSET\s*=\s*utf8\b", "CHARSET=utf8mb4", txt)

    # ✅ Ajuste automático: SUBTITULO -> VARCHAR(512) (na definição do campo)
    # Troca algo como: `SUBTITULO` varchar(70) ...  por  `SUBTITULO` VARCHAR(512) ...
    txt = re.sub(
        r"(?im)^(\s*`SUBTITULO`\s+)varchar\s*\(\s*\d+\s*\)",
        r"\1VARCHAR(512)",
        txt
    )

    Path(sql_out).write_text(txt, encoding="utf-8")
    print(f"✅ SQL normalizado gerado: {sql_out} (lido como {origem} e salvo em utf-8)")


def ajustar_subtitulo_pos_import():
    """Garantia extra: após importar, reforça o tamanho do SUBTITULO."""
    conn = mysql.connector.connect(
        host=host, user=user, password=password, database=database,
        charset="utf8mb4", use_unicode=True
    )
    cur = conn.cursor()
    cur.execute("SET NAMES utf8mb4")
    try:
        cur.execute("ALTER TABLE livro MODIFY SUBTITULO VARCHAR(512);")
        conn.commit()
        print("✅ SUBTITULO garantido como VARCHAR(512).")
    except mysql.connector.Error as e:
        print(f"ℹ️ Não foi possível ajustar SUBTITULO (talvez não exista): {e.msg}")
    finally:
        cur.close()
        conn.close()


def main():
    # 0) Normalizar SQL
    print("[0/4] Normalizando SQL para UTF-8/utf8mb4...")
    gerar_sql_normalizado(sql_original, sql_normalizado)

    # 1) Recriar banco (utf8mb4)
    print("[1/4] Recriando banco (utf8mb4)...")
    cmd1 = (
        f'"{mysql_path}" -u {user} -p"{password}" '
        f'-e "DROP DATABASE IF EXISTS {database}; '
        f'CREATE DATABASE {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"'
    )
    subprocess.run(cmd1, shell=True, check=True)

    # 2) Importar SQL normalizado (utf8mb4 + sql_mode relax para 0000-00-00)
    print("[2/4] Importando SQL normalizado (utf8mb4 + sql_mode)...")

    init_cmd = (
        "SET NAMES utf8mb4; "
        "SET SESSION sql_mode = "
        "REPLACE(REPLACE(REPLACE(@@SESSION.sql_mode,'NO_ZERO_DATE',''),'NO_ZERO_IN_DATE',''),'STRICT_TRANS_TABLES','');"
    )

    # Usamos cmd.exe /c para garantir que o redirecionamento < funcione sempre no Windows
    cmd2 = (
        f'cmd.exe /c ""{mysql_path}" --default-character-set=utf8mb4 '
        f'--init-command="{init_cmd}" '
        f'-u {user} -p"{password}" {database} < "{sql_normalizado}""'
    )
    subprocess.run(cmd2, shell=True, check=True)

    # Garantia extra para SUBTITULO (não atrapalha mesmo se já estiver ok)
    ajustar_subtitulo_pos_import()

    # 3) Exportar CSV
    print("[3/4] Exportando para CSV (utf-8-sig)...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        use_unicode=True,
    )
    cur = conn.cursor()
    cur.execute("SET NAMES utf8mb4")
    cur.execute(QUERY)

    with open(csv_output, mode="w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["TITULO", "AUTOR", "ARMARIO", "PRATILEIRA"])
        for row in cur.fetchall():
            w.writerow(row)

    cur.close()
    conn.close()

    # 4) Gerar JSON otimizado
    print("[4/4] Gerando JSON (records + index de busca)...")
    df = pd.read_csv(csv_output, encoding="utf-8-sig", skip_blank_lines=True)

    cols = ["TITULO", "AUTOR", "ARMARIO", "PRATILEIRA"]
    df = df[cols].copy()
    for c in cols:
        df[c] = df[c].fillna("").astype(str).str.strip()

    df["TITULO_NORM"] = df["TITULO"].apply(normalize_text)
    df["AUTOR_NORM"]  = df["AUTOR"].apply(normalize_text)

    records = df[["TITULO", "AUTOR", "ARMARIO", "PRATILEIRA", "TITULO_NORM", "AUTOR_NORM"]].to_dict("records")
    with open(json_records, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    items = []
    by_title_prefix = {}
    by_author_prefix = {}

    for i, r in enumerate(records):
        items.append([
            r["TITULO"], r["AUTOR"], r["ARMARIO"], r["PRATILEIRA"],
            r["TITULO_NORM"], r["AUTOR_NORM"]
        ])
        add_prefixes(by_title_prefix, r["TITULO_NORM"], i)
        add_prefixes(by_author_prefix, r["AUTOR_NORM"], i)

    index_payload = {
        "meta": {
            "count": len(items),
            "fields": ["titulo", "autor", "armario", "pratileira", "titulo_norm", "autor_norm"],
            "prefix_min": PREFIX_MIN,
            "prefix_max": PREFIX_MAX,
        },
        "items": items,
        "by_title_prefix": by_title_prefix,
        "by_author_prefix": by_author_prefix,
    }

    with open(json_index, "w", encoding="utf-8") as f:
        json.dump(index_payload, f, ensure_ascii=False)

    print("✅ Processo completo concluído com sucesso!")
    print(f"📄 SQL normalizado: {sql_normalizado}")
    print(f"📄 CSV:            {csv_output}")
    print(f"📄 JSON records:   {json_records}")
    print(f"📄 JSON index:     {json_index}")


if __name__ == "__main__":
    main()

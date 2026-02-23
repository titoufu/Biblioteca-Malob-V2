#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def converter_encoding_sql():
    """
    Converte arquivo SQL de encoding Western (ISO-8859-1/Latin1) para UTF-8
    """
    
    print("=" * 60)
    print("CONVERSOR DE ENCODING DE ARQUIVOS SQL")
    print("=" * 60)
    
    # Solicitar caminho do arquivo de entrada
    arquivo_entrada = input("\n📂 Caminho completo do arquivo SQL de entrada: ").strip()
    
    # Remover aspas se o usuário colou com aspas
    arquivo_entrada = arquivo_entrada.strip('"\'')
    
    # Verificar se arquivo existe
    if not os.path.exists(arquivo_entrada):
        print(f"\n❌ ERRO: Arquivo '{arquivo_entrada}' não encontrado!")
        return
    
    # Sugerir nome para arquivo de saída
    dir_name = os.path.dirname(arquivo_entrada)
    base_name = os.path.basename(arquivo_entrada)
    name_without_ext = os.path.splitext(base_name)[0]
    
    saida_padrao = os.path.join(dir_name, f"{name_without_ext}_UTF8.sql")
    
    print(f"\n📝 Nome sugerido para arquivo de saída: {saida_padrao}")
    arquivo_saida = input("✏️  Nome do arquivo de saída (Enter para aceitar sugerido): ").strip()
    
    if not arquivo_saida:
        arquivo_saida = saida_padrao
    
    # Remover aspas se houver
    arquivo_saida = arquivo_saida.strip('"\'')
    
    try:
        # Estatísticas
        linhas_lidas = 0
        linhas_escritas = 0
        
        print(f"\n⏳ Convertendo arquivo...")
        print(f"   De: Western (ISO-8859-1/Latin1)")
        print(f"   Para: UTF-8")
        print(f"   Aguarde...")
        
        # Ler arquivo com encoding Western (Latin1)
        with open(arquivo_entrada, 'r', encoding='latin-1') as f_entrada:
            conteudo = f_entrada.read()
            linhas_lidas = len(conteudo.splitlines())
            
            # Opcional: Mostrar preview antes da conversão
            print(f"\n📋 Preview das primeiras 5 linhas (encoding ORIGINAL):")
            preview_linhas = conteudo.splitlines()[:5]
            for i, linha in enumerate(preview_linhas, 1):
                print(f"   {i}: {linha[:100]}{'...' if len(linha) > 100 else ''}")
        
        # Escrever arquivo com encoding UTF-8
        with open(arquivo_saida, 'w', encoding='utf-8') as f_saida:
            f_saida.write(conteudo)
            linhas_escritas = len(conteudo.splitlines())
        
        print(f"\n✅ CONVERSÃO CONCLUÍDA COM SUCESSO!")
        print(f"   📊 Linhas lidas: {linhas_lidas}")
        print(f"   📊 Linhas escritas: {linhas_escritas}")
        print(f"   📁 Arquivo original: {arquivo_entrada}")
        print(f"   📁 Arquivo convertido: {arquivo_saida}")
        print(f"   💾 Tamanho do arquivo convertido: {os.path.getsize(arquivo_saida):,} bytes")
        
        # Mostrar preview do arquivo convertido
        print(f"\n📋 Preview das primeiras 5 linhas (encoding CONVERTIDO - UTF-8):")
        with open(arquivo_saida, 'r', encoding='utf-8') as f:
            preview_linhas = [next(f) for _ in range(5)]
            for i, linha in enumerate(preview_linhas, 1):
                print(f"   {i}: {linha[:100]}{'...' if len(linha) > 100 else ''}")
        
        # Perguntar se quer substituir SET NAMES no arquivo
        print(f"\n🔧 Deseja ajustar os comandos de encoding no arquivo SQL?")
        print(f"   1 - Sim, substituir 'latin1' por 'utf8' nos comandos SET NAMES")
        print(f"   2 - Sim, substituir 'latin1' por 'utf8mb4' (recomendado para Unicode completo)")
        print(f"   3 - Não, manter como está")
        
        opcao = input("Escolha (1/2/3): ").strip()
        
        if opcao in ['1', '2']:
            novo_encoding = 'utf8' if opcao == '1' else 'utf8mb4'
            
            with open(arquivo_saida, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Substituir SET NAMES
            conteudo_modificado = conteudo.replace("SET NAMES latin1", f"SET NAMES {novo_encoding}")
            conteudo_modificado = conteudo_modificado.replace("/*!40101 SET NAMES latin1 */", f"/*!40101 SET NAMES {novo_encoding} */")
            
            # Substituir CHARSET nas tabelas
            conteudo_modificado = conteudo_modificado.replace("CHARSET=latin1", f"CHARSET={novo_encoding}")
            
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                f.write(conteudo_modificado)
            
            print(f"✅ Comandos de encoding atualizados para '{novo_encoding}' no arquivo!")
        
    except Exception as e:
        print(f"\n❌ ERRO durante a conversão: {e}")
        return
    
    print(f"\n" + "=" * 60)
    print("✅ PROCESSO FINALIZADO!")

def converter_rapido(arquivo_entrada, arquivo_saida=None):
    """
    Função para uso rápido em scripts
    """
    if not arquivo_saida:
        base, ext = os.path.splitext(arquivo_entrada)
        arquivo_saida = f"{base}_UTF8{ext}"
    
    with open(arquivo_entrada, 'r', encoding='latin-1') as f:
        conteudo = f.read()
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    return arquivo_saida

if __name__ == "__main__":
    # Verificar se recebeu argumentos de linha de comando
    if len(sys.argv) > 1:
        arquivo_entrada = sys.argv[1]
        arquivo_saida = sys.argv[2] if len(sys.argv) > 2 else None
        arquivo_convertido = converter_rapido(arquivo_entrada, arquivo_saida)
        print(f"✅ Arquivo convertido: {arquivo_convertido}")
    else:
        # Modo interativo
        converter_encoding_sql()
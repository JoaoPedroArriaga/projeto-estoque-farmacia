#!/usr/bin/env python
"""
Script para criar o banco de dados e as tabelas
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path CORRETAMENTE
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

def criar_banco():
    """Cria o banco de dados se não existir"""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_name = os.getenv('DB_NAME', 'estoque_farmacia')
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Banco '{db_name}' criado")
        else:
            print(f"ℹ️ Banco '{db_name}' já existe")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")
        return False

def criar_tabelas():
    """Cria as tabelas no banco"""
    from src.config.database import db
    
    script_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    if not os.path.exists(script_path):
        print(f"❌ Arquivo schema.sql não encontrado em {script_path}")
        return False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    try:
        db.connect()
        db.execute(sql)
        print("✅ Tabelas criadas com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False
    finally:
        db.close()

def inserir_dados_exemplo():
    """Insere dados de exemplo para teste"""
    from src.config.database import db
    from src.models.medicamento import Medicamento
    from src.models.lote import Lote
    
    try:
        db.connect()
        
        # Verificar se já tem dados
        medicamentos = Medicamento.listar_todos()
        if medicamentos:
            print("ℹ️ Dados de exemplo já existem")
            return True
        
        # Inserir medicamentos
        print("📦 Inserindo medicamentos de exemplo...")
        Medicamento.criar(789123, 'AMOXICILINA 500MG')
        Medicamento.criar(456789, 'DIPIRONA 500MG')
        Medicamento.criar(111222, 'PARACETAMOL 750MG')
        Medicamento.criar(333444, 'IBUPROFENO 600MG')
        
        # Inserir lotes
        print("📦 Inserindo lotes de exemplo...")
        from datetime import date
        Lote.criar(789123, 'LOTE123', date(2025, 12, 31), 100, 15.50)
        Lote.criar(789123, 'LOTE456', date(2025, 6, 30), 50, 15.50)
        Lote.criar(456789, 'LOTE789', date(2025, 12, 31), 200, 8.20)
        Lote.criar(111222, 'LOTEABC', date(2025, 3, 31), 75, 12.00)
        
        print("✅ Dados de exemplo inseridos")
        return True
    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=== INICIANDO SETUP DO BANCO ===\n")
    
    if criar_banco():
        if criar_tabelas():
            inserir_dados_exemplo()
    
    print("\n=== SETUP CONCLUÍDO ===")
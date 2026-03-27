#!/usr/bin/env python
"""
Script para criar o banco de dados e as tabelas
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

def criar_banco():
    """Cria o banco de dados se não existir"""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_name = os.getenv('DB_NAME', 'Interoperabilidade')
    
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
    from src.models.lote import Lote
    
    try:
        db.connect()
        
        # Verificar se já tem medicamentos
        medicamentos = db.execute("SELECT COUNT(*) as total FROM medicamentos", fetch_one=True)
        if medicamentos and medicamentos['total'] > 0:
            print("ℹ️ Dados de exemplo já existem")
            return True
        
        print("\n📦 Inserindo medicamentos de exemplo...")
        
        # Medicamentos com unidades corretas
        medicamentos_data = [
            (789123, 'AMOXICILINA', '500mg', 'CAIXA', 15.50),
            (456789, 'DIPIRONA', '500mg', 'CAIXA', 8.20),
            (111222, 'PARACETAMOL', '750mg', 'CAIXA', 12.00),
            (333444, 'IBUPROFENO', '600mg', 'AMPOLA', 18.50),
        ]
        
        for codigo, nome, concentracao, unidade, preco in medicamentos_data:
            db.execute(
                """INSERT INTO medicamentos (codigo, nome, concentracao, unidade, preco_venda) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (codigo, nome, concentracao, unidade, preco)
            )
            print(f"   ✅ {nome} {concentracao} ({unidade}) - R$ {preco:.2f}")
        
        print("\n📦 Inserindo lotes de exemplo...")
        from datetime import date
        
        lotes_data = [
            (789123, 'LOTE123', date(2027, 12, 31), 100, 15.50),
            (789123, 'LOTE456', date(2027, 6, 30), 50, 15.50),
            (456789, 'LOTE789', date(2027, 12, 31), 200, 8.20),
            (111222, 'LOTEABC', date(2027, 3, 31), 75, 12.00),
            (333444, 'LOTEIBU', date(2027, 12, 31), 50, 18.50),
        ]
        
        for codigo, lote, validade, qtd, preco in lotes_data:
            Lote.criar(codigo, lote, validade, qtd, preco)
            print(f"   ✅ Lote {lote}: {qtd} unidades - R$ {preco:.2f}")
        
        print("\n✅ Dados de exemplo inseridos com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")
        return False
    finally:
        db.close()

def mostrar_status():
    """Mostra status após inicialização"""
    from src.config.database import db
    
    try:
        db.connect()
        
        medicamentos = db.execute("SELECT COUNT(*) as total FROM medicamentos", fetch_one=True)
        lotes = db.execute("SELECT COUNT(*) as total FROM lotes", fetch_all=True)
        
        print("\n" + "=" * 50)
        print("📊 STATUS DO BANCO")
        print("=" * 50)
        print(f"   Medicamentos: {medicamentos['total']}")
        print(f"   Lotes: {len(lotes)}")
        print("=" * 50)
        
        # Mostrar medicamentos
        print("\n💊 MEDICAMENTOS:")
        meds = db.execute("SELECT codigo, nome, unidade, preco_venda FROM medicamentos ORDER BY codigo", fetch_all=True)
        for m in meds:
            print(f"   - {m['codigo']}: {m['nome']} ({m['unidade']}) - R$ {m['preco_venda']:.2f}")
        
        # Mostrar lotes
        print("\n📦 LOTES:")
        lotes_list = db.execute("""
            SELECT l.numero_lote, m.nome, l.quantidade_atual, m.unidade, l.data_validade
            FROM lotes l
            JOIN medicamentos m ON m.codigo = l.codigo_medicamento
            ORDER BY l.numero_lote
        """, fetch_all=True)
        for lote in lotes_list:
            print(f"   - {lote['numero_lote']}: {lote['nome']} | {lote['quantidade_atual']} {lote['unidade']} | Validade: {lote['data_validade']}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO SETUP DO BANCO")
    print("=" * 60)
    
    if criar_banco():
        if criar_tabelas():
            inserir_dados_exemplo()
            mostrar_status()
    
    print("\n" + "=" * 60)
    print("✅ SETUP CONCLUÍDO")
    print("=" * 60)
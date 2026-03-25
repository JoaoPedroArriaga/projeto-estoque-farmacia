#!/usr/bin/env python
"""
Script para testar o fluxo completo do sistema
Cria arquivos de exemplo e processa
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.database import db
from src.processors.consulta_processor import ConsultaProcessor
from src.processors.reserva_processor import ReservaProcessor
from src.processors.baixa_processor import BaixaProcessor
from src.processors.consumo_generator import ConsumoGenerator
from src.utils.csv_utils import escrever_csv

def criar_arquivo_consulta():
    """Cria um arquivo de consulta de exemplo"""
    dados = [
        {
            'id_prescricao': '123456',
            'cpf_paciente': '12345678901',
            'codigo_medicamento': '789123',
            'quantidade': '2'
        }
    ]
    
    caminho = 'data/entrada/consultas/CONSULTA_TESTE_001.csv'
    campos = ['id_prescricao', 'cpf_paciente', 'codigo_medicamento', 'quantidade']
    escrever_csv(caminho, campos, dados)
    print(f"✅ Arquivo de consulta criado: {caminho}")
    return caminho

def criar_arquivo_reserva():
    """Cria um arquivo de reserva de exemplo"""
    dados = [
        {
            'id_prescricao': '123456',
            'cpf_paciente': '12345678901',
            'codigo_medicamento': '789123',
            'quantidade': '2',
            'lote': 'LOTE123'
        }
    ]
    
    caminho = 'data/entrada/reservas/RESERVA_TESTE_001.csv'
    campos = ['id_prescricao', 'cpf_paciente', 'codigo_medicamento', 'quantidade', 'lote']
    escrever_csv(caminho, campos, dados)
    print(f"✅ Arquivo de reserva criado: {caminho}")
    return caminho

def criar_arquivo_baixa():
    """Cria um arquivo de baixa de exemplo"""
    dados = [
        {
            'id_prescricao': '123456',
            'cpf_paciente': '12345678901',
            'codigo_medicamento': '789123',
            'quantidade': '2',
            'lote': 'LOTE123',
            'data_uso': '240320'
        }
    ]
    
    caminho = 'data/entrada/baixas/BAIXA_TESTE_001.csv'
    campos = ['id_prescricao', 'cpf_paciente', 'codigo_medicamento', 
              'quantidade', 'lote', 'data_uso']
    escrever_csv(caminho, campos, dados)
    print(f"✅ Arquivo de baixa criado: {caminho}")
    return caminho

def main():
    print("=== TESTE DO SISTEMA DE ESTOQUE E FARMÁCIA ===\n")
    
    # Conectar ao banco
    db.connect()
    
    # Criar arquivos de teste
    print("1. Criando arquivos de teste...")
    arquivo_consulta = criar_arquivo_consulta()
    arquivo_reserva = criar_arquivo_reserva()
    arquivo_baixa = criar_arquivo_baixa()
    
    # Processar consulta
    print("\n2. Processando consulta...")
    ConsultaProcessor.processar(arquivo_consulta)
    
    # Processar reserva
    print("\n3. Processando reserva...")
    ReservaProcessor.processar(arquivo_reserva)
    
    # Processar baixa
    print("\n4. Processando baixa...")
    BaixaProcessor.processar(arquivo_baixa)
    
    # Gerar consumo
    print("\n5. Gerando relatório de consumo...")
    from datetime import date
    ConsumoGenerator.gerar(date.today())
    
    # Mostrar resultados
    print("\n6. Resultados no banco:")
    
    lotes = db.execute("SELECT * FROM lotes ORDER BY numero_lote", fetch_all=True)
    print(f"   Lotes: {len(lotes)}")
    for l in lotes:
        print(f"     - {l['numero_lote']}: {l['quantidade_atual']} unidades")
    
    itens = db.execute("SELECT * FROM itens_consumo", fetch_all=True)
    print(f"   Itens de consumo: {len(itens)}")
    for i in itens:
        print(f"     - {i['id_prescricao']}: {i['quantidade']} x R$ {i['preco_total']}")
    
    # Mostrar pastas
    print("\n7. Verificando arquivos gerados:")
    
    if os.path.exists('data/saida/respostas'):
        respostas = os.listdir('data/saida/respostas')
        print(f"   Respostas: {len(respostas)} arquivo(s)")
        for r in respostas:
            print(f"     - {r}")
    
    if os.path.exists('data/saida/consumos'):
        consumos = os.listdir('data/saida/consumos')
        print(f"   Consumos: {len(consumos)} arquivo(s)")
        for c in consumos:
            print(f"     - {c}")
    
    if os.path.exists('data/processados'):
        for pasta in ['consultas', 'reservas', 'baixas']:
            caminho = f'data/processados/{pasta}'
            if os.path.exists(caminho):
                arquivos = os.listdir(caminho)
                print(f"   Processados/{pasta}: {len(arquivos)} arquivo(s)")
    
    print("\n✅ Teste concluído!")
    db.close()

if __name__ == "__main__":
    main()
#!/usr/bin/env python
"""
Script de teste completo para apresentação
"""
import os
import sys
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.database import db
from src.processors.consulta_processor import ConsultaProcessor
from src.processors.reserva_processor import ReservaProcessor
from src.processors.baixa_processor import BaixaProcessor
from src.processors.consumo_generator import ConsumoGenerator
from src.utils.csv_utils import escrever_csv, gerar_nome_arquivo

def limpar_dados():
    """Limpa dados anteriores - mantém conexão aberta"""
    print("\n🧹 LIMPANDO DADOS ANTERIORES...")
    
    db.execute("TRUNCATE TABLE itens_consumo CASCADE")
    db.execute("TRUNCATE TABLE movimentacoes CASCADE")
    db.execute("TRUNCATE TABLE logs_consultas CASCADE")
    db.execute("TRUNCATE TABLE logs_reservas CASCADE")
    db.execute("TRUNCATE TABLE logs_baixas CASCADE")
    db.execute("TRUNCATE TABLE logs_consumos CASCADE")
    db.execute("TRUNCATE TABLE reservas_ativas CASCADE")
    db.execute("UPDATE lotes SET quantidade_atual = quantidade_inicial")
    print("   ✅ Limpeza concluída!")

def mostrar_estoque_inicial():
    """Mostra estoque antes do teste"""
    print("\n📦 ESTOQUE INICIAL:")
    print("-" * 60)
    
    lotes = db.execute("""
        SELECT l.numero_lote, m.nome, l.quantidade_atual, m.unidade, l.data_validade
        FROM lotes l
        JOIN medicamentos m ON m.codigo = l.codigo_medicamento
        ORDER BY l.numero_lote
    """, fetch_all=True)
    
    for lote in lotes:
        validade = lote['data_validade']
        dias_restantes = (validade - date.today()).days
        status = "✅" if dias_restantes > 0 else "⚠️ VENCIDO"
        print(f"   {lote['numero_lote']}: {lote['nome']} | {lote['quantidade_atual']:.0f} {lote['unidade']} | Validade: {validade} {status}")

def mostrar_estoque_final():
    """Mostra estoque após o teste"""
    print("\n📦 ESTOQUE FINAL:")
    print("-" * 60)
    
    lotes = db.execute("""
        SELECT l.numero_lote, m.nome, l.quantidade_atual, m.unidade, l.data_validade,
               l.quantidade_inicial - l.quantidade_atual as consumido
        FROM lotes l
        JOIN medicamentos m ON m.codigo = l.codigo_medicamento
        ORDER BY l.numero_lote
    """, fetch_all=True)
    
    for lote in lotes:
        if lote['consumido'] > 0:
            print(f"   {lote['numero_lote']}: {lote['nome']} | {lote['quantidade_atual']:.0f} {lote['unidade']} (consumido: {lote['consumido']:.0f})")
        else:
            print(f"   {lote['numero_lote']}: {lote['nome']} | {lote['quantidade_atual']:.0f} {lote['unidade']}")

def criar_arquivo(tipo, id_prescricao, dados):
    """Cria um arquivo de teste"""
    if tipo == 'CONSULTA':
        campos = ['id_prescricao', 'cpf_paciente', 'codigo_medicamento', 'quantidade']
    elif tipo == 'RESERVA':
        campos = ['id_prescricao', 'cpf_paciente', 'codigo_medicamento', 'quantidade']
    elif tipo == 'BAIXA':
        campos = ['id_prescricao', 'cpf_paciente', 'codigo_medicamento', 'quantidade', 'lote', 'data_uso']
    else:
        return None
    
    nome_arquivo = gerar_nome_arquivo(tipo, str(id_prescricao))
    caminho = os.path.join('data', 'entrada', f"{tipo.lower()}s", nome_arquivo)
    escrever_csv(caminho, campos, dados)
    return caminho

def main():
    print("=" * 70)
    print("🎬 TESTE COMPLETO - SISTEMA DE ESTOQUE E FARMÁCIA")
    print("=" * 70)
    
    # 1. Conectar ao banco (uma única vez para todo o teste)
    db.connect()
    
    # 2. Limpar dados anteriores
    limpar_dados()
    mostrar_estoque_inicial()
    
    # 3. Definir CPFs para os pacientes
    cpfs = {
        'PACIENTE_A': '11122233344',
        'PACIENTE_B': '55566677788',
        'PACIENTE_C': '99988877766',
        'PACIENTE_D': '12345678901',
        'PACIENTE_E': '98765432100'
    }
    
    # 4. Definir os testes
    testes = [
        {'descricao': 'PACIENTE A - PARACETAMOL 1 CAIXA', 'medicamento': 111222, 'quantidade': 1, 'cpf': cpfs['PACIENTE_A'], 'lote_esperado': 'LOTEABC'},
        {'descricao': 'PACIENTE B - PARACETAMOL 1 CAIXA', 'medicamento': 111222, 'quantidade': 1, 'cpf': cpfs['PACIENTE_B'], 'lote_esperado': 'LOTEABC'},
        {'descricao': 'PACIENTE C - AMOXICILINA 2 CAIXAS', 'medicamento': 789123, 'quantidade': 2, 'cpf': cpfs['PACIENTE_C'], 'lote_esperado': 'LOTE456'},
        {'descricao': 'PACIENTE D - AMOXICILINA 3 CAIXAS', 'medicamento': 789123, 'quantidade': 3, 'cpf': cpfs['PACIENTE_D'], 'lote_esperado': 'LOTE456'},
        {'descricao': 'PACIENTE E - IBUPROFENO 2 AMPOLAS', 'medicamento': 333444, 'quantidade': 2, 'cpf': cpfs['PACIENTE_E'], 'lote_esperado': 'LOTEIBU'},
        {'descricao': 'PACIENTE A - AMOXICILINA 1 CAIXA', 'medicamento': 789123, 'quantidade': 1, 'cpf': cpfs['PACIENTE_A'], 'lote_esperado': 'LOTE456'},
    ]
    
    print("\n" + "=" * 70)
    print("📋 EXECUTANDO TESTES")
    print("=" * 70)
    
    reservas_realizadas = []
    
    for i, teste in enumerate(testes, 1):
        print(f"\n{'='*60}")
        print(f"🔹 TESTE {i}: {teste['descricao']}")
        print(f"{'='*60}")
        
        id_prescricao = int(f"{datetime.now().strftime('%H%M%S')}{i:03d}")
        
        # 1. CONSULTA
        print("   [1/3] CONSULTA...")
        consulta_dados = [{
            'id_prescricao': str(id_prescricao),
            'cpf_paciente': teste['cpf'],
            'codigo_medicamento': str(teste['medicamento']),
            'quantidade': str(teste['quantidade'])
        }]
        arquivo_consulta = criar_arquivo('CONSULTA', id_prescricao, consulta_dados)
        ConsultaProcessor.processar(arquivo_consulta)
        
        # 2. RESERVA
        print("   [2/3] RESERVA...")
        reserva_dados = [{
            'id_prescricao': str(id_prescricao),
            'cpf_paciente': teste['cpf'],
            'codigo_medicamento': str(teste['medicamento']),
            'quantidade': str(teste['quantidade'])
        }]
        arquivo_reserva = criar_arquivo('RESERVA', id_prescricao, reserva_dados)
        ReservaProcessor.processar(arquivo_reserva)
        
        reservas_realizadas.append({
            'id_prescricao': id_prescricao,
            'cpf': teste['cpf'],
            'medicamento': teste['medicamento'],
            'quantidade': teste['quantidade'],
            'lote_esperado': teste['lote_esperado']
        })
        
        print(f"   ✅ Teste {i} concluído!")
    
    # 5. BAIXAS
    print("\n" + "=" * 70)
    print("✅ REGISTRANDO BAIXAS")
    print("=" * 70)
    
    data_uso = datetime.now().strftime('%y%m%d')
    
    for i, reserva in enumerate(reservas_realizadas, 1):
        print(f"\n🔹 BAIXA {i}: Prescrição {reserva['id_prescricao']}")
        
        baixa_dados = [{
            'id_prescricao': str(reserva['id_prescricao']),
            'cpf_paciente': reserva['cpf'],
            'codigo_medicamento': str(reserva['medicamento']),
            'quantidade': str(reserva['quantidade']),
            'lote': reserva['lote_esperado'],
            'data_uso': data_uso
        }]
        arquivo_baixa = criar_arquivo('BAIXA', reserva['id_prescricao'], baixa_dados)
        BaixaProcessor.processar(arquivo_baixa)
    
    # 6. GERAR RELATÓRIO DE CONSUMO
    print("\n" + "=" * 70)
    print("📊 GERANDO RELATÓRIO DE CONSUMO")
    print("=" * 70)
    
    ConsumoGenerator.gerar(date.today())
    
    # 7. MOSTRAR RESULTADOS
    print("\n" + "=" * 70)
    print("📈 RESULTADOS FINAIS")
    print("=" * 70)
    
    mostrar_estoque_final()
    
    # Mostrar relatório de consumo gerado
    print("\n📄 RELATÓRIO DE CONSUMO GERADO:")
    print("-" * 60)
    
    data_dir = os.getenv('DATA_DIR', 'data')
    pasta_consumos = os.getenv('PASTA_CONSUMOS', 'saida/consumos')
    caminho_consumo = os.path.join(data_dir, pasta_consumos, f"CONSUMO_{date.today().strftime('%y%m%d')}.csv")
    
    if os.path.exists(caminho_consumo):
        with open(caminho_consumo, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("   Arquivo não encontrado")
    
    # Mostrar estatísticas
    print("\n📊 ESTATÍSTICAS:")
    print("-" * 60)
    
    consultas = db.execute("SELECT COUNT(*) as total FROM logs_consultas", fetch_one=True)
    print(f"   Total de consultas: {consultas['total']}")
    
    reservas = db.execute("SELECT COUNT(*) as total FROM logs_reservas WHERE status = 'PROCESSADO'", fetch_one=True)
    print(f"   Total de reservas: {reservas['total']}")
    
    baixas = db.execute("SELECT COUNT(*) as total FROM logs_baixas WHERE status = 'PROCESSADO'", fetch_one=True)
    print(f"   Total de baixas: {baixas['total']}")
    
    consumo = db.execute("SELECT SUM(preco_total) as total FROM itens_consumo", fetch_one=True)
    print(f"   Valor total faturado: R$ {consumo['total']:.2f}")
    
    # Fechar conexão
    db.close()
    
    print("\n" + "=" * 70)
    print("✅ TESTE COMPLETO CONCLUÍDO COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    main()
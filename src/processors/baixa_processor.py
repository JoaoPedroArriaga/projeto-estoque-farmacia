import os
from src.utils.csv_utils import ler_csv, mover_para_processados
from src.models.logs import LogBaixa
from src.models.lote import Lote
from src.config.database import db

class BaixaProcessor:
    
    @staticmethod
    def processar(caminho_arquivo):
        """Processa um arquivo de baixa"""
        print(f"📄 Processando baixa: {caminho_arquivo}")
        
        # 1. Ler CSV
        dados = ler_csv(caminho_arquivo)
        if not dados:
            return False
        
        # 2. Iniciar transação
        db.begin()
        
        try:
            for row in dados:
                id_prescricao = int(row['id_prescricao'])
                cpf_paciente = int(row['cpf_paciente'])
                codigo_medicamento = int(row['codigo_medicamento'])
                quantidade = float(row['quantidade'])
                lote_numero = row['lote']
                data_uso = int(row['data_uso'])
                
                # Busca lote
                lote = Lote.buscar_por_lote(codigo_medicamento, lote_numero)
                
                if not lote:
                    LogBaixa.registrar(
                        os.path.basename(caminho_arquivo), 
                        id_prescricao, cpf_paciente, codigo_medicamento,
                        quantidade, lote_numero, data_uso, None, 
                        'ERRO', 'Lote não encontrado'
                    )
                    continue
                
                # Converter para float
                quantidade_atual = float(lote['quantidade_atual'])
                
                if quantidade_atual < quantidade:
                    LogBaixa.registrar(
                        os.path.basename(caminho_arquivo), 
                        id_prescricao, cpf_paciente, codigo_medicamento,
                        quantidade, lote_numero, data_uso, lote['id_lote'],
                        'ERRO', 'Estoque insuficiente'
                    )
                    continue
                
                # Atualiza estoque
                nova_quantidade = quantidade_atual - quantidade
                Lote.atualizar_estoque(lote['id_lote'], nova_quantidade)
                
                # Registra log da baixa
                log = LogBaixa.registrar(
                    os.path.basename(caminho_arquivo), 
                    id_prescricao, cpf_paciente, codigo_medicamento,
                    quantidade, lote_numero, data_uso, lote['id_lote'],
                    'PROCESSADO', 'Baixa realizada'
                )
                
                # Registra movimentação
                db.execute(
                    """INSERT INTO movimentacoes 
                       (id_lote, tipo, quantidade, quantidade_anterior, 
                        quantidade_nova, referencia_id, referencia_tabela)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (lote['id_lote'], 'BAIXA', quantidade,
                     quantidade_atual, nova_quantidade,
                     log['id_log'], 'logs_baixas')
                )
                
                # Registra item de consumo
                db.execute(
                    """INSERT INTO itens_consumo 
                       (id_prescricao, cpf_paciente, codigo_medicamento,
                        quantidade, preco_total, data_uso, lote, id_lote, id_baixa_log)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (id_prescricao, cpf_paciente, codigo_medicamento,
                     quantidade, quantidade * float(lote['preco_venda']), data_uso,
                     lote_numero, lote['id_lote'], log['id_log'])
                )
            
            # Confirma transação
            db.commit()
            
            # Mover arquivo para processados
            mover_para_processados(caminho_arquivo, 'baixas')
            
            print(f"✅ Baixa {os.path.basename(caminho_arquivo)} processada")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ Erro ao processar baixa: {e}")
            return False
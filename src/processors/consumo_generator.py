import os
from datetime import date
from src.utils.csv_utils import escrever_csv, gerar_nome_arquivo
from src.config.database import db
from dotenv import load_dotenv

load_dotenv()

class ConsumoGenerator:
    
    @staticmethod
    def gerar(p_data=None):
        """Gera o relatório de consumo do dia"""
        if p_data is None:
            p_data = date.today()
        
        print(f"📊 Gerando relatório de consumo para {p_data}")
        
        # Buscar itens de consumo
        itens = db.execute(
            """SELECT id_prescricao, cpf_paciente, codigo_medicamento,
                      lote, quantidade, unidade, preco_total, data_uso
               FROM itens_consumo
               WHERE consolidado_em = %s AND enviado_para_g1 = FALSE""",
            (p_data,),
            fetch_all=True
        )
        
        if not itens:
            print(f"   Nenhum item para consolidar em {p_data}")
            return False
        
        # Gerar arquivo CSV
        nome_arquivo = gerar_nome_arquivo('CONSUMO')
        
        data_dir = os.getenv('DATA_DIR', 'data')
        pasta_consumos = os.getenv('PASTA_CONSUMOS', 'saida/consumos')
        caminho = os.path.join(data_dir, pasta_consumos, nome_arquivo)
        
        # Campos do relatório
        campos = [
            'id_prescricao',
            'cpf_paciente',
            'codigo_medicamento',
            'lote',
            'quantidade',
            'unidade',
            'preco_total',
            'data_uso'
        ]
        
        escrever_csv(caminho, campos, itens)
        
        # Marcar como enviados
        db.execute(
            """UPDATE itens_consumo 
               SET enviado_para_g1 = TRUE, enviado_em = CURRENT_TIMESTAMP
               WHERE consolidado_em = %s AND enviado_para_g1 = FALSE""",
            (p_data,)
        )
        
        # Registrar no log
        total_itens = len(itens)
        total_valor = sum(float(i['preco_total']) for i in itens)
        
        db.execute(
            """INSERT INTO logs_consumos 
               (arquivo_nome, data_consumo, total_itens, total_valor)
               VALUES (%s, %s, %s, %s)""",
            (nome_arquivo, p_data, total_itens, total_valor)
        )
        
        print(f"✅ Relatório gerado: {caminho}")
        print(f"   Total de itens: {total_itens}")
        print(f"   Valor total: R$ {total_valor:.2f}")
        
        return True
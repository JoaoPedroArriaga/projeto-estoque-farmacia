import os
from src.utils.csv_utils import ler_csv, escrever_csv, gerar_nome_arquivo, mover_para_processados
from src.models.logs import LogConsulta
from src.services.estoque_service import EstoqueService
from dotenv import load_dotenv

load_dotenv()

class ConsultaProcessor:
    
    @staticmethod
    def processar(caminho_arquivo):
        """Processa um arquivo de consulta"""
        print(f"📄 Processando consulta: {caminho_arquivo}")
        
        # 1. Ler CSV
        dados = ler_csv(caminho_arquivo)
        if not dados:
            return False
        
        # 2. Processar cada linha
        respostas = []
        for row in dados:
            id_prescricao = int(row['id_prescricao'])           # <-- INT
            cpf_paciente = int(row['cpf_paciente'])             # <-- INT
            codigo_medicamento = int(row['codigo_medicamento']) # <-- INT
            quantidade = float(row['quantidade'])               # <-- FLOAT
            
            # Verifica disponibilidade
            resultado = EstoqueService.verificar_disponibilidade(
                codigo_medicamento, quantidade
            )
            
            # Registra no log
            LogConsulta.registrar(
                os.path.basename(caminho_arquivo), 
                id_prescricao, 
                cpf_paciente, 
                codigo_medicamento,
                quantidade, 
                resultado['disponivel'], 
                resultado['lote'],
                resultado['validade'], 
                'Disponível' if resultado['disponivel'] else 'Estoque insuficiente'
            )
            
            # Monta resposta
            respostas.append({
                'codigo_medicamento': codigo_medicamento,
                'disponivel': 'SIM' if resultado['disponivel'] else 'NAO',
                'lote_sugerido': resultado['lote'] or '',
                'validade': resultado['validade'] or '',
                'motivo': '' if resultado['disponivel'] else 'Estoque insuficiente'
            })
        
        # 3. Gerar arquivo de resposta
        nome_resposta = gerar_nome_arquivo('RESPOSTA')
        
        data_dir = os.getenv('DATA_DIR', 'data')
        pasta_respostas = os.getenv('PASTA_RESPOSTAS', 'saida/respostas')
        caminho_resposta = os.path.join(data_dir, pasta_respostas, nome_resposta)
        
        campos = ['codigo_medicamento', 'disponivel', 'lote_sugerido', 'validade', 'motivo']
        escrever_csv(caminho_resposta, campos, respostas)
        
        # 4. Mover arquivo original para processados
        mover_para_processados(caminho_arquivo, 'consultas')
        
        print(f"✅ Consulta {os.path.basename(caminho_arquivo)} processada")
        print(f"   Resposta gerada: {caminho_resposta}")
        
        return True
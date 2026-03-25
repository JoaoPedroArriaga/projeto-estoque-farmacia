import os
from src.utils.csv_utils import ler_csv, mover_para_processados
from src.models.logs import LogReserva
from src.services.estoque_service import EstoqueService

class ReservaProcessor:
    
    @staticmethod
    def processar(caminho_arquivo):
        """Processa um arquivo de reserva"""
        print(f"📄 Processando reserva: {caminho_arquivo}")
        
        # 1. Ler CSV
        dados = ler_csv(caminho_arquivo)
        if not dados:
            return False
        
        # 2. Processar cada linha
        for row in dados:
            id_prescricao = int(row['id_prescricao'])           # <-- INT
            cpf_paciente = int(row['cpf_paciente'])             # <-- INT
            codigo_medicamento = int(row['codigo_medicamento']) # <-- INT
            quantidade = float(row['quantidade'])               # <-- FLOAT
            lote_numero = row['lote']
            
            # Valida a reserva
            resultado = EstoqueService.reservar_lote(
                codigo_medicamento, quantidade, lote_numero
            )
            
            # Registra no log
            if resultado['success']:
                LogReserva.registrar(
                    os.path.basename(caminho_arquivo),
                    id_prescricao, cpf_paciente, codigo_medicamento,
                    quantidade, lote_numero, resultado['id_lote'],
                    'PROCESSADO', 'Reserva realizada'
                )
            else:
                LogReserva.registrar(
                    os.path.basename(caminho_arquivo),
                    id_prescricao, cpf_paciente, codigo_medicamento,
                    quantidade, lote_numero, None,
                    'ERRO', resultado['error']
                )
        
        # 3. Mover arquivo original para processados
        mover_para_processados(caminho_arquivo, 'reservas')
        
        print(f"✅ Reserva {os.path.basename(caminho_arquivo)} processada")
        return True
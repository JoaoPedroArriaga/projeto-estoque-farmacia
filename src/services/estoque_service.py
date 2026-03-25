from src.models.lote import Lote

class EstoqueService:
    
    @staticmethod
    def verificar_disponibilidade(codigo_medicamento, quantidade):
        """Verifica se tem lote disponível (FEFO)"""
        lote = Lote.buscar_disponivel(codigo_medicamento, quantidade)
        
        if lote:
            return {
                'disponivel': True,
                'lote': lote['numero_lote'],
                'validade': lote['data_validade'],
                'preco': lote['preco_venda']
            }
        return {
            'disponivel': False,
            'lote': None,
            'validade': None,
            'preco': None
        }
    
    @staticmethod
    def reservar_lote(codigo_medicamento, quantidade, lote_numero):
        """Reserva um lote (não altera estoque, só valida)"""
        lote = Lote.buscar_por_lote(codigo_medicamento, lote_numero)
        
        if not lote:
            return {'success': False, 'error': 'Lote não encontrado'}
        
        if lote['quantidade_atual'] < quantidade:
            return {'success': False, 'error': 'Estoque insuficiente'}
        
        # Verificar validade
        from datetime import date
        if lote['data_validade'] < date.today():
            return {'success': False, 'error': 'Lote vencido'}
        
        return {'success': True, 'id_lote': lote['id_lote']}
    
    @staticmethod
    def dar_baixa(codigo_medicamento, quantidade, lote_numero):
        """Dá baixa no estoque (diminui quantidade)"""
        from src.config.database import db
        
        # Busca o lote
        lote = Lote.buscar_por_lote(codigo_medicamento, lote_numero)
        
        if not lote:
            return {'success': False, 'error': 'Lote não encontrado'}
        
        if lote['quantidade_atual'] < quantidade:
            return {'success': False, 'error': 'Estoque insuficiente'}
        
        # Atualiza estoque
        nova_quantidade = lote['quantidade_atual'] - quantidade
        Lote.atualizar_estoque(lote['id_lote'], nova_quantidade)
        
        return {
            'success': True,
            'id_lote': lote['id_lote'],
            'preco_venda': lote['preco_venda']
        }
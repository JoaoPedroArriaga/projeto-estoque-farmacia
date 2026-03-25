from src.config.database import db

class Lote:
    @staticmethod
    def listar_todos():
        return db.execute(
            """SELECT * FROM lotes 
               ORDER BY data_validade ASC""",
            fetch_all=True
        )
    
    @staticmethod
    def listar_por_medicamento(codigo_medicamento):
        return db.execute(
            """SELECT * FROM lotes 
               WHERE codigo_medicamento = %s 
               ORDER BY data_validade ASC""",
            (codigo_medicamento,),
            fetch_all=True
        )
    
    @staticmethod
    def buscar_disponivel(codigo_medicamento, quantidade):
        """Busca lote disponível seguindo FEFO"""
        return db.execute(
            """SELECT * FROM lotes 
               WHERE codigo_medicamento = %s 
                 AND quantidade_atual >= %s 
                 AND data_validade >= CURRENT_DATE 
               ORDER BY data_validade ASC 
               LIMIT 1""",
            (codigo_medicamento, quantidade),
            fetch_one=True
        )
    
    @staticmethod
    def buscar_por_lote(codigo_medicamento, numero_lote):
        return db.execute(
            """SELECT * FROM lotes 
               WHERE codigo_medicamento = %s 
                 AND numero_lote = %s""",
            (codigo_medicamento, numero_lote),
            fetch_one=True
        )
    
    @staticmethod
    def buscar_com_lock(id_lote):
        return db.execute(
            "SELECT * FROM lotes WHERE id_lote = %s FOR UPDATE",
            (id_lote,),
            fetch_one=True
        )
    
    @staticmethod
    def atualizar_estoque(id_lote, nova_quantidade):
        return db.execute(
            "UPDATE lotes SET quantidade_atual = %s WHERE id_lote = %s",
            (nova_quantidade, id_lote)
        )
    
    @staticmethod
    def criar(codigo_medicamento, numero_lote, data_validade, 
              quantidade_inicial, preco_venda):
        return db.execute(
            """INSERT INTO lotes 
               (codigo_medicamento, numero_lote, data_validade, 
                quantidade_inicial, quantidade_atual, preco_venda)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (codigo_medicamento, numero_lote, data_validade,
             quantidade_inicial, quantidade_inicial, preco_venda)
        )
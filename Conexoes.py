import sqlite3 as sql
from datetime import datetime, timedelta
import uuid

class Banco:
    # Método construtor do banco
    ### Utilizado para definir a rota do banco e qual a tabela utilizada (já que nesse projeto cada banco possui apenas uma)
    # Também são definidas algumas variáveis para operações no banco
    def __init__(self, rotaBanco, tabela):
        self.tabela = tabela
        self.rota = rotaBanco
        self.conn = None
        self.cur = None
        self.connected = False

    # Aqui são utilizados métodos SQLite3 para gerar uma conexão que depois é feita de cursor
    def connect(self):
        self.conn = sql.connect(self.rota)
        self.cur = self.conn.cursor()
        self.connected = True

    # Método utilizado para fechar a conexão
    def disconnect(self):
        self.conn.close()
        self.connected = False

    # Cancela alterações feitas (chamado em caso de erros)
    def rollback(self):
        if self.connected:
            self.conn.rollback()

    # Executa comando SQL + parâmetros se existentes
    def execute(self, sql, parms=None):
        if self.connected:
            if parms is None:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, parms)
            return True
        else:
            return False


    # Salvar mudanças no banco
    def persist(self):
        if self.connected:
            self.conn.commit()
            return True
        else:
            return False
    
    # Cria o banco de Logs caso não exista
    def initDBLogs(self):
        self.connect()
        self.execute(f"CREATE TABLE IF NOT EXISTS {self.tabela} (id INTEGER PRIMARY KEY AUTOINCREMENT, Operacao_realizada TEXT (50), Data_hora_operacao TEXT);")
        self.persist()
        self.disconnect()
    
    # Deleta os Logs anteriores a 2 dias
    def deletarLogs(self):
        logs = self.read()
        try:
            for _log in logs:
                dataLog = datetime.strptime(_log[2], '%d-%m-%Y %H:%M:%S')
                if datetime.now() - dataLog > timedelta(days=2):
                    self.delete(_log[0])
            return logs
        except Exception as e:
            return f'Erro deleção de logs{str(e)}'

    # Insere um novo log com a operação e a data.
    def novoLog(self, operacao, ):
        self.initDBLogs()
        self.deletarLogs()
        self.connect()
        horaAtual = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        try:
            self.execute(f"Insert into {self.tabela} VALUES (NULL, ?, ?);", (operacao, horaAtual))
            self.persist()
            self.disconnect()
            return "Log realizado"
        except:
            self.rollback()
            return 'Erro Log'

    # Operação insert (executável através da instância BancoDestino)
    def insert(self, Nome, RG, CPF, Data_admissao, CEP, endereco, bairro, cidade):
        self.connect()
        horaAtual = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        try:
            novoId = self.gerar_id_unico()
            self.execute(f"INSERT INTO {self.tabela} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (str(novoId), Nome, RG, CPF, Data_admissao, horaAtual, CEP, endereco, bairro, cidade))
            self.persist()
            self.disconnect()
        except sql.IntegrityError as e:
            self.rollback()

    # Operação select (executável através de qualquer instância)
    def read(self): 
        self.connect()
        try:
            self.execute(f"SELECT * FROM {self.tabela};")
            rows = self.cur.fetchall()
            self.disconnect()
            return rows
        except:
            return "Erro leitura"

    # Operação buscar pelo ID (executável através de qualquer instância)
    def search(self, id, ):
        self.connect()
        try:
            self.execute(f"SELECT * FROM {self.tabela} WHERE ID = ?", (id, ))
            rows = self.cur.fetchall()
            self.disconnect()
            return rows
        except Exception as e:
            return f"Erro busca: {str(e)}"

    # Operação select (executável através de qualquer instância)
    def delete(self, id, ):
        self.connect()
        try:
            self.execute(f"DELETE FROM {self.tabela} WHERE ID = ?", (id, ))
            self.persist()
            self.disconnect()
            return "Sucesso delete"
        except:
            self.rollback()
            return "Erro delete"

    # Operação de update (executável através da instância banco destino apenas)
    def update(self, id, Nome, RG, CPF, Data_admissao, CEP, endereco, bairro, cidade):
        self.connect()
        horaAtual = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        try:
            self.execute(f"UPDATE {self.tabela} SET Nome = ?, RG = ?, CPF = ?, Data_admissao = ?, Data_hora_alteracao_do_registro = ?, CEP = ?, endereco = ?, bairro = ?, cidade = ? WHERE ID = ?", (Nome, RG, CPF, Data_admissao, horaAtual, CEP, endereco, bairro, cidade, id))
            self.persist()
            self.disconnect()
            return "Sucesso update"
        except:
            self.rollback()
            return "Erro update"
    
    # Método exclusivo para carregar funcionários do BD01 para o BD02 utilizando seu ID, e gerando um novo ID aleatório e único
    def carregarDados(self, id, Nome, RG, CPF, Data_admissao, CEP, endereco, bairro, cidade):
        self.connect()
        horaAtual = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        novoId = self.gerar_id_unico()
        try:
            self.execute(f"UPDATE {self.tabela} SET ID = ?, Nome = ?, RG = ?, CPF = ?, Data_admissao = ?, Data_hora_alteracao_do_registro = ?, CEP = ?, endereco = ?, bairro = ?, cidade = ? WHERE ID = ?", (str(novoId), Nome, RG, CPF, Data_admissao, horaAtual, CEP, endereco, bairro, cidade, id))
            self.persist()
            self.disconnect()
            return "Sucesso update"
        except Exception as e:
            self.rollback()
            return f"Erro update {str(e)}"

    def gerar_id_unico(self):
        while True:
            novo_id = uuid.uuid4()
            # Verificar se o UUID já existe no banco de dados
            self.execute(f"SELECT ID FROM {self.tabela} WHERE ID=?", (str(novo_id), ))
            resultado = self.cur.fetchone()
            if resultado is None:
                return novo_id



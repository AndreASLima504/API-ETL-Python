import sqlite3 as sql
from datetime import datetime, timedelta

class Banco:
    def __init__(self, rotaBanco, tabela):
        self.tabela = tabela
        self.database = rotaBanco
        self.conn = None
        self.cur = None
        self.connected = False

    def connect(self):
        self.conn = sql.connect(self.database)
        self.cur = self.conn.cursor()
        self.connected = True

    def disconnect(self):
        self.conn.close()
        self.connected = False

    def rollback(self):
        if self.connected:
            self.conn.rollback()

    def execute(self, sql, parms=None):
        if self.connected:
            if parms is None:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, parms)
            return True
        else:
            return False

    def fetchall(self):
        return self.cur.fetchall()

    def persist(self):
        if self.connected:
            self.conn.commit()
            return True
        else:
            return False
    
    def initDBLogs(self):
        self.connect()
        self.execute(f"CREATE TABLE IF NOT EXISTS {self.tabela} (id INTEGER PRIMARY KEY AUTOINCREMENT, Operacao_realizada TEXT (50), Data_hora_operacao TEXT);")
        self.persist()
        self.disconnect()
    
    def deletarLogs(self):
        logs = self.read()
        try:
            for log in logs:
                if datetime.now() - datetime.strptime(log[2], '%d-%m-%Y %H:%M:%S') > timedelta(days=2):
                    self.delete(log[0])
            return logs
        except Exception as e:
            return f'Erro deleção de logs{str(e)}'

    
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

    def insert(self, Nome, RG, CPF, Data_admissao, CEP, endereco, bairro, cidade):
        self.connect()
        horaAtual = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        try:
            self.execute(f"INSERT INTO {self.tabela} VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (Nome, RG, CPF, Data_admissao, horaAtual, CEP, endereco, bairro, cidade))
            self.persist()
            self.disconnect()
        except sql.IntegrityError as e:
            self.rollback()

    def read(self): 
        self.connect()
        try:
            self.execute(f"SELECT * FROM {self.tabela};")
            rows = self.fetchall()
            self.disconnect()
            return rows
        except:
            return "Erro leitura"

    def search(self, id, ):
        self.connect()
        try:
            self.execute(f"SELECT * FROM {self.tabela} WHERE ID = ?", (id, ))
            rows = self.fetchall()
            self.disconnect()
            return rows
        except Exception as e:
            return f"Erro busca: {str(e)}"

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





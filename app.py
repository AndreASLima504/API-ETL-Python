from flask import Flask, request, jsonify
import Conexoes as Cons
from datetime import datetime
import requests



BancoOrigem = Cons.Banco("Banco1", "funcionarios")
BancoDestino = Cons.Banco("Banco2", "funcionarios_fabrica")
Logs = Cons.Banco("Logs.db", "Logs")

app = Flask(__name__)

# Ler todos os Logs
@app.route('/logs', methods=['GET'])
def mostrar_logs():
    Logs.initDBLogs()
    _logs = Logs.read()
    return _logs

# Atualizar dados do BD02 com dados do BD01 através do ID, incluindo endereço através do viacep
@app.route('/atualizar_dados', methods=['PUT'])
def copy_data():
    dadosOrigem = get_origem()
    for i in dadosOrigem:
        enderecoCompleto = requests.get(f'https://viacep.com.br/ws/{i[6]}/json/').json()
        horaAtual = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        dadosUpdate = {
            "ID": i[0],
            "Nome": i[1],
            "RG": i[2],
            "CPF": i[3],
            "Data_admissao": i[4],
            "Data_alteracao_do_registro": horaAtual,
            "CEP": i[6],
            "endereco": enderecoCompleto['logradouro'],
            "bairro": enderecoCompleto['bairro'],
            "cidade": enderecoCompleto['localidade']
        }
        print(dadosUpdate)
        try:
            BancoDestino.update(dadosUpdate['ID'], dadosUpdate['Nome'], dadosUpdate['RG'], dadosUpdate['CPF'], dadosUpdate['Data_admissao'], dadosUpdate['Data_alteracao_do_registro'], dadosUpdate['CEP'], dadosUpdate['endereco'], dadosUpdate['bairro'], dadosUpdate['cidade'])
            Logs.novoLog('Dados do BD02 atualizados com os do BD01', horaAtual)
        except:
            return "Erro na atualização de dados"
    return BancoDestino.read()

# Ler todos os dados do banco de origem (BD01)
@app.route('/dados_origem', methods=['GET'])
def get_origem():
    dadosOrigem = BancoOrigem.read()
    return dadosOrigem

# Ler todos os dados do banco de destino (BD02)
@app.route('/dados_destino', methods=['GET'])
def get_destino():
    dadosDestino = BancoDestino.read()
    return dadosDestino

### Para atualizar, deve-se enviar um json contendo: id original, novos dados para nome, RG, CPF, data_admissao, CEP, endereco, bairro e cidade
@app.route('/dados_destino', methods=['PUT'])
def update_target_data():
    horaAtual = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    try:
        requisicao = request.get_json()
        try:
            BancoDestino.update(requisicao[0], requisicao[1], requisicao[2], requisicao[3], requisicao[4], horaAtual, requisicao[5], requisicao[6], requisicao[7], requisicao[8])
            try:
                Logs.novoLog(f"Dados do funcionário de id: {requisicao[0]} alterados", horaAtual)
                return BancoDestino.search(str(requisicao[0]))
            except:return "Erro de Log"
        except Exception as e:return f"Erro update{str(e)}"
    except: return "Erro de arquivo json"
    
### Para cadastrar um novo funcionario, deve-se enviar um json contendo: novos dados para nome, RG, CPF, data_admissao, CEP
@app.route('/dados_destino', methods=['POST'])
def insert_destino():
    horaAtual = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    try:
        requisicao = request.get_json()
        viacep = requests.get(f'https://viacep.com.br/ws/{requisicao[4]}/json/').json()
        BancoDestino.insert(requisicao[0], requisicao[1], requisicao[2], requisicao[3], horaAtual, requisicao[4], viacep['logradouro'], viacep['bairro'], viacep['localidade'])
        Logs.novoLog(f"Novo funcionário inserido: {requisicao}", horaAtual)
        return "sucesso"
    except Exception as e:
        return f"Erro: {str(e)}"

### Método para deletar linha do BD02; Requer json informando o id
@app.route('/dados_destino', methods=['DELETE'])
def delete_target_data():
    horaAtual = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    try:
        requisicao = request.get_json()
        deletado = BancoDestino.search(str(requisicao[0]))
        BancoDestino.delete(requisicao[0])
        Logs.novoLog(f"Funcionário excluído: {deletado}", horaAtual)
        return BancoDestino.read()
    except Exception as e:
        return f"erro: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)

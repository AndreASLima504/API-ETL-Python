from flask import Flask, request, jsonify
import Conexoes as Cons
from datetime import datetime
import requests



BancoOrigem = Cons.Banco("Banco1", "funcionarios")
BancoDestino = Cons.Banco("Banco2", "funcionarios_fabrica")
Logs = Cons.Banco("Logs.db", "Logs")

app = Flask(__name__)

@app.route('/<id>', methods=['GET'])
def teste(id):
    print(type(id))
    return BancoDestino.search(id)

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


@app.route('/dados_origem', methods=['GET'])
def get_origem():
    dadosOrigem = BancoOrigem.read()
    return dadosOrigem


@app.route('/dados_destino', methods=['GET'])
def get_destino():
    dadosDestino = BancoDestino.read()
    return dadosDestino

@app.route('/dados_destino/', methods=['PUT'])
def update_target_data():
    requisicao = request.get_json()
    BancoDestino.update(requisicao[0], requisicao[1], requisicao[2], requisicao[3], requisicao[4], requisicao[5], requisicao[6], requisicao[7], requisicao[8], requisicao[9])
    Logs
    return BancoDestino.search(str(requisicao[0]))

@app.route('/dados_destino/<id>, ', methods=['POST'])
def insert_destino():
    dadosDestino = BancoDestino.insert()
    return dadosDestino


@app.route('/dados_destino/<id>', methods=['DELETE'])
def delete_target_data(id):
    BancoDestino.delete(id)
    pass


if __name__ == '__main__':
    app.run(debug=True)

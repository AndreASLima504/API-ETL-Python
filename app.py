from flask import Flask, request, jsonify
import Conexoes as Cons
from datetime import datetime
import requests
import json



BancoOrigem = Cons.Banco("Banco1", "funcionarios")
BancoDestino = Cons.Banco("Banco2", "funcionarios_fabrica")

app = Flask(__name__)

@app.route('/', methods=['GET'])
def teste():
    data = datetime.now().strftime('Hora: %H:%M:%S  Data: %d-%m-%Y')
    return data

@app.route('/copiar_dados', methods=['GET'])
def copy_data():
    dadosOrigem = get_origem()
    for i in dadosOrigem:
        enderecoCompleto = requests.get(f'https://viacep.com.br/ws/{i[6]}/json/').json()
        dadosInsert = {
            "ID": i[0],
            "Nome": i[1],
            # "RG": i[2],
            # "CPF": i[3],
            # "Data_admissao": i[4],
            # "Data_alteracao_do_registro": datetime.now().strftime('Hora: %H:%M:%S  Data: %d-%m-%Y'),
            # "CEP": i[6],
            # "endereco": enderecoCompleto['logradouro'],
            # "bairro": enderecoCompleto['bairro'],
            # "cidade": enderecoCompleto['localidade']
        }
        # print(dadosInsert)
        # BancoDestino.insert[dadosInsert['ID'], dadosInsert['Nome'], dadosInsert['RG'], dadosInsert['CPF'], dadosInsert['Data_admissao'], dadosInsert['Data_alteracao_do_registro'], dadosInsert['CEP'], dadosInsert['endereco'], dadosInsert['bairro'], dadosInsert['cidade']]
        BancoDestino.insert[dadosInsert['ID']]
    return 'hello world'


@app.route('/dados_origem', methods=['GET'])
def get_origem():
    dadosOrigem = BancoOrigem.read()
    return dadosOrigem


@app.route('/dados_destino', methods=['GET'])
def get_destino():
    dadosDestino = BancoDestino.read()
    return dadosDestino

@app.route('/dados_destino/<id>', methods=['PUT'])
def update_target_data(id):
    BancoOrigem.update(id, )
    return BancoOrigem.search(id)


@app.route('/target_data/<id>', methods=['DELETE'])
def delete_target_data(id):
    BancoDestino.delete(id)
    pass


if __name__ == '__main__':
    app.run(debug=True)

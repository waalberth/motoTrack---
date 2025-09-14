from flask import Flask, request, jsonify
from flask_cors import CORS

# Inicializa a aplicação Flask
app = Flask(__name__)
# Habilita o CORS para toda a aplicação.
CORS(app)

# Banco de dados de usuários fictício para simular a autenticação.
USERS = {
    "teste@mototrack.com": "123456",
    "usuario@mototrack.com": "senha123"
}

# Lista temporária para armazenar os abastecimentos.
# Em um projeto real, isso seria um banco de dados de verdade.
ABASTECIMENTOS = []

@app.route("/login", methods=["POST"])
def login():
    """
    Rota para processar a autenticação do usuário.
    """
    if not request.is_json:
        return jsonify({"success": False, "message": "Requisição inválida."}), 400

    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if not email or not password:
        return jsonify({"success": False, "message": "E-mail ou senha ausentes."}), 400

    if email in USERS and USERS[email] == password:
        return jsonify({"success": True, "message": "Login bem-sucedido!"}), 200
    else:
        return jsonify({"success": False, "message": "Credenciais inválidas."}), 401

@app.route("/abastecimentos/cadastrar", methods=["POST"])
def cadastrar_abastecimento():
    """
    Nova rota para cadastrar um abastecimento.
    Recebe os dados do formulário e os adiciona à nossa lista temporária.
    """
    if not request.is_json:
        return jsonify({"success": False, "message": "Requisição inválida."}), 400
    
    # Extrai os dados do corpo da requisição JSON
    data_abastecimento = request.json.get("data")
    quilometragem = request.json.get("quilometragem")
    litros = request.json.get("litros")
    preco = request.json.get("preco")
    combustivel = request.json.get("combustivel")
    valor_total = litros * preco

    # Validação simples dos dados recebidos
    if not all([data_abastecimento, quilometragem, litros, preco, combustivel]):
        return jsonify({"success": False, "message": "Todos os campos são obrigatórios."}), 400
        
    # Cria um dicionário com os dados do abastecimento
    abastecimento = {
        "id": len(ABASTECIMENTOS) + 1,
        "data": data_abastecimento,
        "quilometragem": quilometragem,
        "litros": litros,
        "preco": preco,
        "combustivel": combustivel,
        "valor_total": valor_total
    }
    
    # Adiciona o abastecimento à lista temporária
    ABASTECIMENTOS.append(abastecimento)
    
    print(f"Novo abastecimento cadastrado: {abastecimento}")
    print(f"Total de abastecimentos: {len(ABASTECIMENTOS)}")
    
    return jsonify({"success": True, "message": "Abastecimento cadastrado com sucesso!"}), 200


if __name__ == "__main__":
    # Inicia o servidor Flask em modo de desenvolvimento na porta 5001
    app.run(debug=True, port=5001)

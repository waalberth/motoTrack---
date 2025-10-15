from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# Inicializa a aplicação Flask
app = Flask(__name__)
# Habilita o CORS para toda a aplicação.
CORS(app)

# Define o nome do arquivo do banco de dados
DATABASE = 'mototrack.db'

# Banco de dados de usuários fictício (manteremos isso por enquanto)
USERS = {
    "teste@mototrack.com": "123456",
    "usuario@mototrack.com": "senha123"
}

def get_db_connection():
    """
    Função para estabelecer a conexão com o banco de dados.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

def init_db():
    """
    Função para inicializar o banco de dados, criando a tabela se ela não existir.
    """
    conn = get_db_connection()
    # Usa um bloco with para garantir que a conexão será fechada automaticamente
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS abastecimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                quilometragem REAL NOT NULL,
                litros REAL NOT NULL,
                preco REAL NOT NULL,
                combustivel TEXT NOT NULL,
                valor_total REAL NOT NULL
            );
        """)
    conn.close()

# Chama a função para inicializar o banco de dados antes de iniciar o servidor
init_db()

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
    Rota para cadastrar um abastecimento no banco de dados.
    """
    if not request.is_json:
        return jsonify({"success": False, "message": "Requisição inválida."}), 400
    
    data_abastecimento = request.json.get("data")
    quilometragem = request.json.get("quilometragem")
    litros = request.json.get("litros")
    preco = request.json.get("preco")
    combustivel = request.json.get("combustivel")
    valor_total = litros * preco

    if not all([data_abastecimento, quilometragem, litros, preco, combustivel]):
        return jsonify({"success": False, "message": "Todos os campos são obrigatórios."}), 400
        
    try:
        conn = get_db_connection()
        with conn:
            conn.execute("""
                INSERT INTO abastecimentos (data, quilometragem, litros, preco, combustivel, valor_total)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (data_abastecimento, quilometragem, litros, preco, combustivel, valor_total))
        conn.close()
        
        print("Abastecimento cadastrado com sucesso no banco de dados.")
        
        return jsonify({"success": True, "message": "Abastecimento cadastrado com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao cadastrar abastecimento: {e}")
        return jsonify({"success": False, "message": "Erro ao tentar cadastrar no banco de dados."}), 500

# Esta é a posição correta para a nova rota de listagem
@app.route("/abastecimentos/listar", methods=["GET"])
def listar_abastecimentos():
    """
    Rota para listar todos os abastecimentos do banco de dados.
    """
    abastecimentos = []
    try:
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM abastecimentos ORDER BY data DESC;")
            abastecimentos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(abastecimentos), 200
    except Exception as e:
        print(f"Erro ao listar abastecimentos: {e}")
        return jsonify({"success": False, "message": "Erro ao tentar buscar abastecimentos no banco de dados."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
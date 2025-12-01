from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# Inicializa a aplicação Flask
app = Flask(__name__)
# Habilita o CORS para toda a aplicação.
CORS(app)

# Define o nome do arquivo do banco de dados
DATABASE = 'mototrack.db'

# Banco de dados de usuários locais
USERS = {
    "teste@mototrack.com": "123456",
    "usuario@mototrack.com": "senha123",
    "teste@gmail.com": "teste"
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

# inicializando o banco de dados 
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

@app.route("/abastecimentos/listar", methods=["GET"])
def listar_abastecimentos():
    """
    Nova rota para listar todos os abastecimentos do banco de dados.
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

from flask import request, jsonify 

@app.route('/abastecimentos/excluir/<int:id>', methods=['DELETE'])
def excluir_abastecimento(id):
    try:
        conn = sqlite3.connect('mototrack.db')
        cursor = conn.cursor()

        # Comando SQL para deletar o registro
        cursor.execute("DELETE FROM abastecimentos WHERE id = ?", (id,))
        
        conn.commit()
        conn.close()
        
        # msg sucesso
        return jsonify({"message": f"Abastecimento ID {id} excluído com sucesso!"}), 200

    except Exception as e:
        # msg erro
        return jsonify({"message": f"Erro ao excluir abastecimento: {str(e)}"}), 500
@app.route("/abastecimentos/<int:id>", methods=["GET"])
def obter_abastecimento_por_id(id):
    """
    Rota para buscar os detalhes de um único abastecimento pelo ID.
    """
    try:
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM abastecimentos WHERE id = ?", (id,))
            abastecimento = cursor.fetchone()
        conn.close()
        
        if abastecimento is None:
            return jsonify({"success": False, "message": f"Abastecimento ID {id} não encontrado."}), 404
            
        # Retorna o abastecimento como um dicionário JSON
        return jsonify(dict(abastecimento)), 200
        
    except Exception as e:
        print(f"Erro ao buscar abastecimento ID {id}: {e}")
        return jsonify({"success": False, "message": "Erro ao buscar detalhes do abastecimento."}), 500

## ROTA PATCH PARA EDIÇÃO (Atualização Parcial)
@app.route('/abastecimentos/editar/<int:id>', methods=['PATCH'])
def editar_abastecimento(id):
    """
    Rota para atualização PARCIAL de um abastecimento existente pelo ID (PATCH).
    Busca os dados antigos, mescla com os novos e recalcula o valor total.
    """
    dados = request.get_json()
    
    if not dados:
        return jsonify({"success": False, "message": "Nenhum dado fornecido para atualização."}), 400
    
    try:
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            
            # 1. Buscar o registro existente para ter os valores atuais
            cursor.execute("SELECT * FROM abastecimentos WHERE id = ?", (id,))
            registro_antigo = cursor.fetchone()
            
            if not registro_antigo:
                return jsonify({"success": False, "message": f"Abastecimento ID {id} não encontrado."}), 404
            
            registro_antigo = dict(registro_antigo)
            
            # 2. Prepara os novos dados, tratando a conversão para float
            litros = float(dados.get('litros', registro_antigo['litros']))
            preco = float(dados.get('preco', registro_antigo['preco']))
            
            # 3. Recalcula o valor total
            valor_total = litros * preco
            
            # 4. Monta a lista de campos a serem atualizados
            campos_para_atualizar = []
            valores_para_atualizar = []
            
            # Mapeia todos os campos da tabela com os valores atualizados (novos ou antigos)
            campos_com_valores = {
                'data': dados.get('data', registro_antigo['data']),
                'quilometragem': float(dados.get('quilometragem', registro_antigo['quilometragem'])),
                'litros': litros,
                'preco': preco,
                'combustivel': dados.get('combustivel', registro_antigo['combustivel']),
                'valor_total': valor_total # Valor recalculado
            }

            # Itera sobre os campos para montar a query de UPDATE
            for chave, valor in campos_com_valores.items():
                campos_para_atualizar.append(f"{chave} = ?")
                valores_para_atualizar.append(valor)
            
            # 5. Execução do UPDATE
            query = f"UPDATE abastecimentos SET {', '.join(campos_para_atualizar)} WHERE id = ?"
            params = tuple(valores_para_atualizar) + (id,) 
            
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                return jsonify({"success": False, "message": f"Abastecimento ID {id} não encontrado (Falha na Atualização)."})
            
        return jsonify({"success": True, "message": f"Abastecimento ID {id} atualizado com sucesso!"}), 200

    except ValueError:
        return jsonify({"success": False, "message": "Os campos de números (quilometragem, litros, preço) devem ser válidos."}), 400
    except Exception as e:
        print(f"Erro ao editar abastecimento ID {id}: {e}")
        return jsonify({"success": False, "message": "Erro interno ao atualizar o abastecimento."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
// VARIÁVEL GLOBAL PARA ARMAZENAR O ID QUE ESTÁ SENDO EDITADO
// Isso é crucial para que a função de submissão saiba para qual ID enviar o PATCH.
let idAbastecimentoEmEdicao = null;

function confirmarExclusao(id, fetchAbastecimentosCallback) {
    if (confirm(`Tem certeza que deseja excluir o abastecimento ID ${id}? Esta ação não pode ser desfeita.`)) {
        // CORREÇÃO: Usando a porta 5002
        fetch(`http://127.0.0.1:5002/abastecimentos/excluir/${id}`, {
            method: 'DELETE',
        })
        // ... (resto da função) ...
        .then(response => {
            if (response.ok) {
                alert(`Abastecimento ID ${id} excluído com sucesso!`);
                fetchAbastecimentosCallback(); 
            } else {
                response.json().then(data => {
                    alert(`Erro ao excluir: ${data.message || response.statusText}`);
                }).catch(() => {
                    alert('Erro desconhecido ao excluir o abastecimento.');
                });
            }
        })
        .catch(error => {
            console.error('Erro na requisição de exclusão:', error);
            alert('Não foi possível conectar ao servidor para excluir o abastecimento.');
        });
    }
}

// Listar abastecimentos
async function fetchAbastecimentos() {
    const container = document.getElementById('abastecimentos-container');
    
    try {
        container.innerHTML = ''; 
        // CORREÇÃO: Usando a porta 5002
        const response = await fetch('http://127.0.0.1:5002/abastecimentos/listar');
        
        if (!response.ok) {
            throw new Error('Erro ao buscar os dados da API.');
        }
        
        const abastecimentos = await response.json();

        if (abastecimentos.length === 0) {
            container.innerHTML = '<p>Nenhum abastecimento encontrado.</p>';
            return;
        }

        // Cria a tabela base
        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Quilometragem (km)</th>
                    <th>Litros</th>
                    <th>Preço (R$/L)</th>
                    <th>Combustível</th>
                    <th>Valor Total (R$)</th>
                    <th>Ações</th> 
                </tr>
            </thead>
            <tbody>
                </tbody>
        `;
        
        const tbody = table.querySelector('tbody');

    // Retorno da api para a tabela
        abastecimentos.forEach(abastecimento => {
            const row = document.createElement('tr');
            row.innerHTML = `
    <td>${abastecimento.data}</td>
    <td>${abastecimento.quilometragem}</td>
    <td>${abastecimento.litros}</td>
    <td>${abastecimento.preco}</td>
    <td>${abastecimento.combustivel}</td>
    <td>${abastecimento.valor_total.toFixed(2)}</td>
    <td>
        <button class="btn-editar" 
                onclick="iniciarEdicao(${abastecimento.id})">
            Editar ✍️
        </button>
        <button class="btn-excluir" 
                onclick="confirmarExclusao(${abastecimento.id}, fetchAbastecimentos)">
            Excluir 🗑️
        </button>
    </td>

            `;
            tbody.appendChild(row);
        });

        container.appendChild(table);

    } catch (error) {
        console.error('Erro:', error);
        container.innerHTML = '<p>Erro ao carregar a lista de abastecimentos. Verifique se o servidor está rodando na porta 5002.</p>';
    }
}

// NOVA FUNÇÃO: Aciona a busca de dados e mostra o modal
async function iniciarEdicao(abastecimentoId) {
    // 1. Armazena o ID globalmente
    idAbastecimentoEmEdicao = abastecimentoId;
    
    try {
        // 2. CHAMA O NOVO ENDPOINT GET para pegar os dados
        // CORREÇÃO: Usando a porta 5002
        const response = await fetch(`http://127.0.0.1:5002/abastecimentos/${abastecimentoId}`);
        
        if (response.ok) {
            const dadosAbastecimento = await response.json();
            
            // 3. Chama a função para pré-preencher
            preencherFormularioEdicao(dadosAbastecimento);
            
            // 4. Mostra o modal/formulário de edição.
            document.getElementById('modal-edicao').style.display = 'block'; 

        } else {
            alert("Erro ao buscar dados para edição.");
            idAbastecimentoEmEdicao = null;
        }
    } catch (error) {
        console.error('Erro ao iniciar edição:', error);
        alert('Não foi possível conectar ao servidor para buscar os dados de edição.');
    }
}

// NOVA FUNÇÃO: Preenche o formulário de edição com os dados resgatados
function preencherFormularioEdicao(dados) {
    const form = document.getElementById('form-edicao'); 
    
    // Atualiza os valores dos inputs
    document.getElementById('display-id-edicao').textContent = dados.id; // Exibe o ID
    form.querySelector('#input-data-edicao').value = dados.data;
    form.querySelector('#input-quilometragem-edicao').value = dados.quilometragem;
    form.querySelector('#input-litros-edicao').value = dados.litros;
    form.querySelector('#input-preco-edicao').value = dados.preco;
    form.querySelector('#input-combustivel-edicao').value = dados.combustivel;
    
    // Exibe o valor total
    document.getElementById('display-valor-total-edicao').textContent = `R$ ${dados.valor_total.toFixed(2)}`;
}

// NOVA FUNÇÃO: Resgate os valores do formulário e envia o PATCH
async function submeterEdicao(event) {
    event.preventDefault(); // Impede o envio padrão do formulário

    if (!idAbastecimentoEmEdicao) {
        alert("Erro: Nenhum abastecimento selecionado para edição.");
        return;
    }

    // 1. Coleta os dados do formulário
    const form = document.getElementById('form-edicao'); 
    const dadosEditados = {
        data: form.querySelector('#input-data-edicao').value,
        quilometragem: parseFloat(form.querySelector('#input-quilometragem-edicao').value),
        litros: parseFloat(form.querySelector('#input-litros-edicao').value),
        preco: parseFloat(form.querySelector('#input-preco-edicao').value),
        combustivel: form.querySelector('#input-combustivel-edicao').value,
        // O valor_total é recalculado pelo backend (Flask)
    };

    // 2. Envio da requisição PATCH
    try {
        // CORREÇÃO: Usando a porta 5002
        const response = await fetch(`http://127.0.0.1:5002/abastecimentos/editar/${idAbastecimentoEmEdicao}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosEditados)
        });

        if (response.ok) {
            alert("Abastecimento atualizado com sucesso!");
            // Esconde o modal/formulário de edição
            document.getElementById('modal-edicao').style.display = 'none'; 
            
            // Recarrega a lista para mostrar a alteração
            fetchAbastecimentos(); 
        } else {
            const errorData = await response.json();
            alert(`Falha na atualização: ${errorData.message}`);
        }

    } catch (error) {
        console.error('Erro na submissão da edição:', error);
        alert('Não foi possível conectar ao servidor para atualizar o abastecimento.');
    }
}

document.addEventListener('DOMContentLoaded', () => {

    fetchAbastecimentos(); 
    
    // NOVO: Adiciona o listener para a submissão do formulário de edição
    const formEdicao = document.getElementById('form-edicao');
    if (formEdicao) {
        formEdicao.addEventListener('submit', submeterEdicao);
    }
});
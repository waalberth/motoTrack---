
function confirmarExclusao(id, fetchAbastecimentosCallback) {

    if (confirm(`Tem certeza que deseja excluir o abastecimento ID ${id}? Esta ação não pode ser desfeita.`)) {
        
        // 2. envio do delete
        fetch(`http://127.0.0.1:5001/abastecimentos/excluir/${id}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (response.ok) {
                alert(`Abastecimento ID ${id} excluído com sucesso!`);
                
                // 3. reload
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

        const response = await fetch('http://127.0.0.1:5001/abastecimentos/listar');
        
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
        container.innerHTML = '<p>Erro ao carregar a lista de abastecimentos. Verifique se o servidor está rodando.</p>';
    }
}


document.addEventListener('DOMContentLoaded', () => {

    fetchAbastecimentos(); 
});
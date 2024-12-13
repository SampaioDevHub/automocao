README Técnico
Visão Geral
Este projeto é uma aplicação web desenvolvida com o framework Flask. Ele permite o upload de uma planilha Excel e de um modelo de documento Word. A aplicação processa os dados da planilha para gerar fichas personalizadas, que podem ser baixadas em um arquivo ZIP.

Arquitetura
Framework: Flask.
Dependências:
pandas: Leitura de dados da planilha Excel.
python-docx: Manipulação de documentos Word.
concurrent.futures: Processamento paralelo.
zipfile: Criação de arquivos ZIP.
RotatingFileHandler: Gerenciamento de logs.
Estrutura de Diretórios:
uploads/: Diretório para armazenar os arquivos enviados.
download/: Diretório para armazenar as fichas geradas e o arquivo ZIP final.
app.log: Arquivo de log rotativo.
Funcionalidades
Página Inicial (GET /):

Renderiza um formulário para o upload de arquivos.
Upload de Arquivos (POST /upload):

Recebe uma planilha Excel e um modelo de documento Word.
Processa os dados para gerar fichas personalizadas em paralelo.
Retorna um link para download das fichas.
Download de Arquivo ZIP (GET /download):

Gera um arquivo ZIP com as fichas geradas.
Faz o envio do ZIP ao cliente.
Principais Melhorias
Concorrência Controlada:

Processamento paralelo com ProcessPoolExecutor (limitado a 4 workers).
Uso de threading.Lock para evitar acesso simultâneo ao arquivo ZIP.
Gerenciamento de Logs:

Logs configurados com rotação para evitar crescimento descontrolado.
Tratamento de Erros:

Manipulação detalhada de exceções com logs para diagnóstico.
Mensagens claras para o usuário em caso de erro.
Manutenção de Diretórios:

Diretório de saída é limpo antes de cada operação.
Performance:

Paralelismo na geração de fichas reduz tempo de processamento.
Redução de consumo de memória por meio de limitações de workers.
Como Usar
Instalação:

Certifique-se de ter Python 3.8+ instalado.
Instale as dependências com:
bash
Copy code
pip install flask pandas python-docx
Execução:

Inicie o servidor Flask com:
bash
Copy code
python app.py
Acesse http://localhost:5000 no navegador.
Fluxo de Operação:

Faça o upload de uma planilha Excel com dados de clientes e um modelo Word.
Clique no link para baixar as fichas geradas em um arquivo ZIP.
Requisitos de Arquivos
Planilha Excel:

Colunas obrigatórias:
Nome
Cidade
CPF ou CNPJ
Email
Modelo Word:

Deve conter placeholders como:
DADOS DO CLIENTE
Dia/mes/ano e CIDADE DO CLIENTE
NOME E CPF DO CLIENTE
EMAIL DO CLIENTE
Limitações Conhecidas
Volume de Dados:

Grandes volumes de dados podem levar a tempos de processamento elevados.
Segurança:

Upload de arquivos não valida formatos em profundidade.
Manutenção do Servidor:

Em produção, recomenda-se usar um servidor WSGI como Gunicorn para melhor desempenho.
Melhorias Futuras
Implementar validação mais robusta para arquivos enviados.
Adicionar suporte a outras linguagens para placeholders.
Incluir testes automatizados para garantir qualidade.

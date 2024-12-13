from flask import Flask, request, send_from_directory, render_template
import pandas as pd
from docx import Document
import os
from datetime import datetime
import zipfile
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed

# Configuração do Flask e diretórios
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "download"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configuração de logs
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Definir número máximo de workers
MAX_WORKERS = 4  # Limitar para evitar sobrecarga do servidor


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_files():
    try:
        # Verificar se os arquivos foram enviados
        planilha = request.files.get("planilha")
        modelo = request.files.get("modelo")

        if not planilha or not modelo:
            logging.warning("Planilha ou modelo não enviados pelo usuário.")
            return "Erro: Envie a planilha e o modelo de ficha.", 400

        # Salvar arquivos enviados
        planilha_path = salvar_arquivo(planilha, "Clientes.xlsx")
        modelo_path = salvar_arquivo(modelo, "modelo.docx")

        # Processar arquivos em paralelo
        processar_planilha_parallel(planilha_path, modelo_path)
        logging.info("Fichas geradas com sucesso.")

    except Exception as e:
        logging.exception(f"Erro inesperado ao processar os arquivos: {e}")
        return f"Erro inesperado: {e}", 500

    return "Fichas geradas com sucesso! <a href='/download'>Baixar fichas</a>"


@app.route("/download")
def download_zip():
    try:
        zip_path = criar_arquivo_zip()
        return send_from_directory(
            OUTPUT_FOLDER, os.path.basename(zip_path), as_attachment=True
        )
    except Exception as e:
        logging.exception(f"Erro ao criar ou enviar o arquivo ZIP: {e}")
        return "Erro ao preparar o download. Tente novamente mais tarde.", 500


# Funções auxiliares
def salvar_arquivo(arquivo, nome):
    """Salva o arquivo enviado no diretório de uploads."""
    caminho = os.path.join(UPLOAD_FOLDER, nome)
    arquivo.save(caminho)
    logging.info(f"Arquivo salvo com sucesso: {caminho}")
    return caminho


def processar_planilha_parallel(planilha_path, modelo_path):
    """Lê a planilha e gera fichas personalizadas em paralelo."""
    clientes = pd.read_excel(planilha_path)
    data_atual = datetime.now().strftime("%d/%m/%Y")

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for _, cliente in clientes.iterrows():
            futures.append(
                executor.submit(
                    gerar_ficha_cliente, cliente.to_dict(), modelo_path, data_atual
                )
            )

        for future in as_completed(futures):
            try:
                future.result()  # Levanta exceções, se houver
            except Exception as e:
                logging.exception(f"Erro ao gerar ficha: {e}")


def gerar_ficha_cliente(cliente, modelo_path, data_atual):
    """Gera uma ficha para um cliente específico."""
    try:
        ficha = Document(modelo_path)

        # Substituir placeholders nos parágrafos
        for paragraph in ficha.paragraphs:
            substituir_placeholders(paragraph, cliente, data_atual)

        # Salvar a ficha gerada em memória ou no disco
        nome_arquivo = (
            f"Ficha_{cliente.get('Nome', 'Desconhecido').replace(' ', '_')}.docx"
        )
        ficha.save(os.path.join(OUTPUT_FOLDER, nome_arquivo))
        logging.info(
            f"Ficha gerada para o cliente: {cliente.get('Nome', 'Desconhecido')}"
        )
    except Exception as e:
        logging.exception(
            f"Erro ao gerar ficha para o cliente {cliente.get('Nome', 'Desconhecido')}: {e}"
        )
        raise


def substituir_placeholders(paragraph, cliente, data_atual):
    """Substitui os placeholders no parágrafo."""
    placeholders = {
        "DADOS DO CLIENTE": cliente.get("Nome", "DADOS NÃO ENCONTRADOS"),
        "Dia/mes/ano e CIDADE DO CLIENTE": f"{data_atual} - {cliente.get('Cidade', 'CIDADE NÃO ENCONTRADA')}",
        "NOME E CPF DO CLIENTE": f"{cliente.get('Nome', 'NOME NÃO ENCONTRADO')} - {cliente.get('CPF ou CNPJ', 'CPF/CNPJ NÃO ENCONTRADO')}",
        "EMAIL DO CLIENTE": cliente.get("Email", "EMAIL NÃO ENCONTRADO"),
    }

    for placeholder, valor in placeholders.items():
        if placeholder in paragraph.text:
            paragraph.text = paragraph.text.replace(placeholder, valor)


def criar_arquivo_zip():
    """Cria um arquivo ZIP contendo todas as fichas geradas."""
    zip_path = os.path.join(OUTPUT_FOLDER, "fichas.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(OUTPUT_FOLDER):
            for file in files:
                if file != "fichas.zip":  # Evitar incluir o próprio ZIP no arquivo ZIP
                    zipf.write(os.path.join(root, file), file)
    logging.info(f"Arquivo ZIP criado com sucesso: {zip_path}")
    return zip_path


if __name__ == "__main__":
    app.run(debug=False)

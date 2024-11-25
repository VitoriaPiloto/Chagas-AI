import os
from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
import PyPDF2  # Biblioteca para ler PDFs
import pytesseract  # Biblioteca para OCR
from PIL import Image  # Biblioteca para manipulação de imagens
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Conectar ao banco de dados MySQL
def conectar_banco():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="13579",
        database="chagas_ai"
    )

# Função para extrair texto de um arquivo PDF
def extrair_texto_pdf(arquivo):
    texto = ""
    with open(arquivo, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for pagina in pdf_reader.pages:
            texto += pagina.extract_text() or ""  # Adiciona texto da página se não for None
    return texto

# Função para extrair texto de uma imagem
def extrair_texto_imagem(arquivo):
    texto = ""
    try:
        imagem = Image.open(arquivo)
        texto = pytesseract.image_to_string(imagem)
    except Exception as e:
        print(f"Erro ao ler a imagem: {e}")
    return texto

# Função para processar sintomas e gerar diagnóstico simulado
def processar_sintomas(texto_extraido):
    sintomas = re.findall(r'\bfebre\b|\binchaço\b|\bdor\b|\bmal-estar\b', texto_extraido, re.IGNORECASE)
    if sintomas:
        probabilidade = 0.9 if len(sintomas) > 1 else 0.6
    else:
        probabilidade = 0.2
    diagnostico = "positivo" if probabilidade > 0.7 else "pode ter" if probabilidade > 0.4 else "negativo"
    return {"diagnostico": diagnostico, "probabilidade": probabilidade}

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para fazer upload e processamento dos arquivos
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    # Verifica se o arquivo é um PDF ou imagem
    if file and (file.filename.endswith('.pdf') or file.filename.lower().endswith(('.png', '.jpg', '.jpeg'))):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Extração do texto via PDF ou imagem
        if file.filename.endswith('.pdf'):
            texto_extraido = extrair_texto_pdf(filepath)
        else:
            texto_extraido = extrair_texto_imagem(filepath)

        # Analisar sintomas e calcular diagnóstico
        resultado = processar_sintomas(texto_extraido)

        # Salvar arquivo e resultado no banco
        conexao = conectar_banco()
        cursor = conexao.cursor()
        query = "INSERT INTO diagnosticos (arquivo_nome, texto_extraido, diagnostico, probabilidade) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (file.filename, texto_extraido, resultado['diagnostico'], resultado['probabilidade']))
        conexao.commit()
        cursor.close()
        conexao.close()

        return f"Diagnóstico: {resultado['diagnostico']}, Probabilidade: {resultado['probabilidade']:.2f}"
    else:
        return "Por favor, envie apenas arquivos PDF ou imagens (PNG, JPG).", 400

# Iniciar o servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Executa o servidor no IP 0.0.0.0 e na porta 5000

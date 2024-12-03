import os
from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
import PyPDF2  # Biblioteca para ler PDFs
import pytesseract  # Biblioteca para OCR
from PIL import Image  # Biblioteca para manipulação de imagens
import re
import pickle

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
            texto += pagina.extract_text() or ""
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

def processar_sintomas(texto_extraido):
    # Convertendo o texto extraído para minúsculas e removendo caracteres estranhos
    texto_extraido = texto_extraido.lower().strip()
    
    # Sintomas para Chagas
    sintomas_chagas = re.findall(r'\bfebre\b|\btaquicardia\b|\bicterícia\b|\bmanchas vermelhas na pele\b|\bedema de face\b|\bedema de membros\b|\binchaço\b|\bdor no corpo\b|\bdor de cabeça\b|\bvomitos\b|\bdiarreia\b|\bnausea\b|\bmal-estar\b|\bfraqueza\b|\bcrescimento do baço\b|\bcrescimento do fígado\b', texto_extraido, re.IGNORECASE)
    
    # Sintomas para outras doenças
    sintomas_gripe = re.findall(r'\btosse\b|\bcalafrios\b|\bdor de garganta\b|\bnariz entupido\b', texto_extraido, re.IGNORECASE)
    sintomas_resfriado = re.findall(r'\btosse\b|\bnariz entupido\b|\bespirros\b|\bdor de cabeça\b', texto_extraido, re.IGNORECASE)
    sintomas_covid = re.findall(r'\btosse\b|\bfalta de ar\b|\bfebre\b|\bdor muscular\b', texto_extraido, re.IGNORECASE)
    sintomas_pneumonia = re.findall(r'\bfalta de ar\b|\bcalafrios\b|\bcansaço\b|\bdor no peito\b', texto_extraido, re.IGNORECASE)

    # Inicializando probabilidade
    probabilidade = 0.2
    diagnostico = "negativo"

    # Se sintomas de Chagas forem encontrados, aumentar a probabilidade
    if len(sintomas_chagas) > 1:
        probabilidade += 0.3

    # Ajustando a probabilidade com base nos sintomas de outras doenças
    if sintomas_gripe or sintomas_resfriado or sintomas_covid or sintomas_pneumonia:
        probabilidade -= 0.2  # Diminui um pouco a probabilidade caso haja sintomas de outras doenças

    # Garantindo que a probabilidade não ultrapasse 1 (100%)
    probabilidade = min(probabilidade, 1.0)

    # Diagnóstico final com base na probabilidade ajustada
    if probabilidade >= 0.7:
        diagnostico = "Existe muita chance de conter a doença de chagas! Procure um médico!"
    elif probabilidade >= 0.3:
        diagnostico = "Exista a possibilidade de conter a doença"
    else:
        diagnostico = "Não possui a doença"

    # Corrigindo para não gerar valores inesperados

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

    if file and (file.filename.endswith('.pdf') or file.filename.lower().endswith(('.png', '.jpg', '.jpeg'))):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        if file.filename.endswith('.pdf'):
            texto_extraido = extrair_texto_pdf(filepath)
        else:
            texto_extraido = extrair_texto_imagem(filepath)

        resultado = processar_sintomas(texto_extraido)

        conexao = conectar_banco()
        cursor = conexao.cursor()
        query = "INSERT INTO diagnosticos (arquivo_nome, texto_extraido, diagnostico, probabilidade) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (file.filename, texto_extraido, resultado['diagnostico'], resultado['probabilidade']))
        conexao.commit()
        cursor.close()
        conexao.close()

        return jsonify({"diagnostico": resultado['diagnostico'], "probabilidade": resultado['probabilidade']})
    else:
        return "Por favor, envie apenas arquivos PDF ou imagens (PNG, JPG).", 400

# Rota para receber feedback
@app.route('/feedback', methods=['POST'])
def receber_feedback():
    data = request.get_json()
    if not data or 'arquivo_nome' not in data or 'diagnostico_real' not in data:
        return jsonify({"message": "Dados inválidos"}), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()
    query = "INSERT INTO feedback (arquivo_nome, diagnostico_real, processado) VALUES (%s, %s, FALSE)"
    cursor.execute(query, (data['arquivo_nome'], data['diagnostico_real']))
    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({"message": "Feedback recebido com sucesso!"}), 200

# Rota para re-treinar o modelo
@app.route('/retrain', methods=['POST'])
def retrain_model():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM feedback WHERE processado = FALSE")
    feedbacks = cursor.fetchall()

    if not feedbacks:
        return jsonify({"message": "Nenhum feedback disponível para treinamento"}), 200

    texts = []
    labels = []
    for feedback in feedbacks:
        texts.append(feedback['arquivo_nome'])  # Ajuste conforme necessário
        labels.append(feedback['diagnostico_real'])

    with open('modelo_chagas.pkl', 'rb') as f:
        vectorizer, model = pickle.load(f)

    X_feedback = vectorizer.transform(texts)
    model.partial_fit(X_feedback, labels, classes=["positivo", "negativo", "indeterminado"])

    with open('modelo_chagas.pkl', 'wb') as f:
        pickle.dump((vectorizer, model), f)

    cursor.executemany("UPDATE feedback SET processado = TRUE WHERE id = %s", [(f['id'],) for f in feedbacks])
    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({"message": "Modelo atualizado com sucesso!"}), 200

# Iniciar o servidor
if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.134', port=8080)

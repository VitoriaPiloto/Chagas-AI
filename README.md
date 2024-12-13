# Chagas AI 

Uma inteligência artificial gerada para conseguir ler resultado de exames de doença de chagas. 

## [Link do vídeo da apresentação presencial](https://drive.google.com/file/d/1U4PGGvmRPnA_FfUobHDa8siF45kZByaY/view?usp=sharing)

## Como rodar no seu computador

1. Instalar as dependências necessárias
```bash
   pip install -r requirements.txt
   ```
2. Configure o [mySQL](https://dev.mysql.com/downloads/installer/) Server em sua máquina
  

4. Instalar o Tesseract 5.4.0
5. Configure o banco de dados com o script abaixo
6. Alterar o app.py os dados do banco de dados.

## Script para criação do banco

```bash
CREATE TABLE diagnosticos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    arquivo_nome VARCHAR(255) NOT NULL,
    texto_extraido TEXT NOT NULL,
    diagnostico ENUM('positivo', 'pode ter', 'negativo') NOT NULL,
    probabilidade DECIMAL(5, 2) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    arquivo_nome VARCHAR(255) NOT NULL,
    diagnostico_real VARCHAR(50) NOT NULL,
    processado BOOLEAN DEFAULT FALSE
);
```



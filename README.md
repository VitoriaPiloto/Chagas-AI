# Chagas AI 

Umma inteligência artificial gerada para conseguir ler resultado de exames de doença de chagas. 

## Script para criação do banco

CREATE TABLE Paciente 
( 
 id INT PRIMARY KEY,  
 dataNascimento INT,  
 cpf INT,  
 endereco INT,  
 nome INT,  
); 

CREATE TABLE Medico 
( 
 id INT PRIMARY KEY,  
 nome INT,  
 crm INT,  
 especialidade INT,  
); 

CREATE TABLE diagnosticos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    arquivo_nome VARCHAR(255) NOT NULL,
    texto_extraido TEXT NOT NULL,
    diagnostico ENUM('positivo', 'pode ter', 'negativo') NOT NULL,
    probabilidade DECIMAL(5, 2) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chagas_ai.feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    arquivo_nome VARCHAR(255) NOT NULL,
    diagnostico_real VARCHAR(50) NOT NULL,
    processado BOOLEAN DEFAULT FALSE
);

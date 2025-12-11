# Assistente de Ensino de Java com FastAPI e Gemini

## Objetivo do Projeto

Este projeto consiste em um microserviço de backend que atua como um assistente de ensino inteligente especializado em desenvolvimento Java. A API, construída com Python e FastAPI, se integra ao modelo Gemini do Google para gerar explicações didáticas.

O diferencial desta API é que ela retorna um **objeto JSON estruturado**, separando a explicação em seções (como "Visão Geral", "Analogia", etc.) e fornecendo uma lista de perguntas de acompanhamento sugeridas. Isso permite que qualquer cliente (um frontend web, um aplicativo de terminal ou um API client como o Bruno) construa uma experiência de usuário rica e interativa.

## Estrutura do Projeto

```
/
├── bruno/                          # Coleção de testes para o API Client Bruno
│   ├── Bad Request (No 'message' field).bru
│   ├── Chat Java.bru
│   ├── Method Not Allowed (GET).bru
│   └── bruno.json
├── main.py                       # Arquivo principal com a lógica da aplicação FastAPI.
├── client.py                     # Cliente de linha de comando interativo para a API.
├── requirements.txt              # Lista de dependências Python.
├── .gitignore                    # Arquivo para ignorar arquivos de ambiente e outros.
├── .env                          # Arquivo local para armazenar a chave da API (não versionado).
├──.env.example                  # Exemplo de arquivo .env para configuração.
```

## Instruções de Instalação

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### 1. Clone o Repositório e Instale as Dependências

```bash
# Clone o repositório
git clone <>
cd java-assistant

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: .\venv\Scripts\activate

# Instale todas as dependências
pip install -r requirements.txt
```

### 2. Configure a Chave da API

1.  Crie uma chave de API no [Google AI Studio](https://aistudio.google.com/app/api-keys).
2.  Crie um arquivo chamado `.env` na raiz do projeto.
3.  Adicione sua chave ao arquivo da seguinte forma:
    ```
    GOOGLE_API_KEY='SUA_CHAVE_API_AQUI'
    ```

## Como Rodar a Aplicação

Para usar a aplicação, você tem duas opções principais: usar o cliente interativo (recomendado) ou testar a API diretamente com o Bruno.

### Opção 1: Usar o Cliente Interativo (Recomendado)

Você precisará rodar o **servidor** e o **cliente** em dois terminais separados.

**Terminal 1: Rodar o Servidor da API**
```bash
uvicorn main:app --reload
```
Deixe este terminal aberto. O servidor estará disponível em `http://127.0.0.1:8000`.

**Terminal 2: Rodar o Cliente Interativo**
```bash
# Ative o ambiente virtual novamente, se necessário
source venv/bin/activate

# Execute o cliente
python client.py
```
Agora você pode interagir com o assistente diretamente neste terminal.

### Opção 2: Testar a API Diretamente com Bruno

**Bruno** é um cliente de API de código aberto que permite importar e testar coleções de API de forma simples.

1.  **Instale o Bruno**: Baixe e instale o Bruno a partir do [site oficial](https://www.usebruno.com/).
2.  **Abra a Coleção**:
    *   Com o Bruno aberto, clique em "Open Collection".
    *   Navegue até a pasta do seu projeto e selecione a pasta `bruno/`.
    *   O Bruno irá importar automaticamente a coleção "Assistente de Ensino de Java" com todas as requisições.
3.  **Execute as Requisições**:
    *   **`Chat Java`**: Esta é a requisição principal para uma conversa bem-sucedida. Ela possui documentação detalhada na aba "Doc".
    *   **`Bad Request`**: Testa se a API retorna um erro `422` ao enviar um corpo de requisição inválido.
    *   **`Method Not Allowed`**: Testa se a API retorna um erro `405` ao tentar usar o método `GET`.
    
    Para cada requisição, clique no botão "Send" e verifique a resposta e o status no painel de resultados. A aba "Tests" mostrará se os testes de validação passaram.

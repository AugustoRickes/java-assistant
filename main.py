import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

# --- Configuração Inicial ---
load_dotenv()
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi configurada.")
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    # Este erro será lançado na inicialização do servidor se a chave não estiver configurada
    raise RuntimeError(f"Erro na configuração da API do Gemini: {e}") from e


# --- Modelos Pydantic para a Resposta Estruturada ---

class ExplicacaoSecao(BaseModel):
    titulo: str = Field(..., description="O título da seção de explicação (ex: 'Visão Geral').")
    conteudo: str = Field(..., description="O texto de conteúdo para a seção.")

class Verificacao(BaseModel):
    resumo_prompt: str = Field(..., description="Um prompt curto pedindo ao usuário para resumir o que entendeu.")
    perguntas_acompanhamento: List[str] = Field(..., description="Uma lista de perguntas de acompanhamento sugeridas.")

class StructuredChatResponse(BaseModel):
    explicacao: List[ExplicacaoSecao] = Field(..., description="Uma lista de seções que compõem a explicação principal.")
    verificacao: Verificacao = Field(..., description="A seção de verificação com prompts para o usuário.")


# --- Lógica da IA ---

# Instrução de sistema para forçar a saída em JSON
system_instruction = """Você é um professor especialista em desenvolvimento Java. Sua missão é ensinar conceitos de Java de forma didática e interativa.

Sua resposta DEVE SER OBRIGATORIAMENTE um objeto JSON válido, e nada mais. Não inclua ```json ou qualquer outro texto fora do objeto JSON.

O JSON deve seguir esta estrutura:
{
  "explicacao": [
    {
      "titulo": "Visão Geral",
      "conteudo": "Uma visão geral simples do conceito."
    },
    {
      "titulo": "Analogia",
      "conteudo": "Uma analogia do mundo real para ilustrar o conceito."
    },
    {
      "titulo": "Explicação Progressiva",
      "conteudo": "A explicação dividida em etapas, aumentando a complexidade."
    },
    {
      "titulo": "Relações",
      "conteudo": "Como o conceito se relaciona com outras áreas de Java."
    },
    {
      "titulo": "Exemplos Práticos",
      "conteudo": "Um exemplo de código prático e sua explicação detalhada."
    },
    {
      "titulo": "Detalhes Técnicos",
      "conteudo": "Detalhes técnicos mais profundos sobre o conceito."
    }
  ],
  "verificacao": {
    "resumo_prompt": "Um prompt curto pedindo ao usuário para resumir o que entendeu.",
    "perguntas_acompanhamento": [
      "Primeira pergunta de acompanhamento para explorar o tópico.",
      "Segunda pergunta de acompanhamento.",
      "Terceira pergunta de acompanhamento."
    ]
  }
}

Garanta que o conteúdo de cada campo seja claro e siga a metodologia de ensino. Não responda a perguntas que não sejam sobre Java.
"""

# Inicializa o modelo generativo
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash-lite',
    system_instruction=system_instruction
)


# --- Aplicação FastAPI ---

app = FastAPI(
    title="Assistente de Ensino de Java",
    description="Uma API que fornece explicações estruturadas sobre Java e sugere perguntas de acompanhamento.",
    version="2.0.0",
)

class ChatRequest(BaseModel):
    message: str
    # Opcionalmente, podemos passar o histórico na requisição no futuro
    # history: List[Dict[str, str]] = []

# Histórico da conversa global (solução simples em memória)
conversation_history = []

@app.post("/chat", response_model=StructuredChatResponse)
async def chat(request: ChatRequest):
    """
    Recebe uma pergunta sobre Java, interage com o modelo Gemini para obter uma
    resposta estruturada em JSON, e a retorna.
    """
    global conversation_history

    try:
        # Inicia uma sessão de chat com o histórico
        chat_session = model.start_chat(history=conversation_history)
        # Usando send_message síncrono por simplicidade, para async/await, o Gemini usa send_message_async
        response = chat_session.send_message(request.message)

        # Limpa e decodifica a resposta JSON da IA
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        
        try:
            parsed_data = json.loads(cleaned_response_text)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=502, # Bad Gateway
                detail="A resposta da IA não era um JSON válido."
            )

        # Adiciona a interação atual ao histórico para manter o contexto
        # Adicionamos a string JSON bruta para reforçar o formato para a IA
        conversation_history.append({"role": "user", "parts": [request.message]})
        conversation_history.append({"role": "model", "parts": [cleaned_response_text]})

        # Limita o histórico para as últimas 6 interações (3 pares)
        if len(conversation_history) > 6:
            conversation_history = conversation_history[-6:]
        
        # FastAPI validará o dicionário `parsed_data` contra o `StructuredChatResponse`
        return parsed_data

    except Exception as e:
        # Tratamento de erro genérico para outras falhas da API do Gemini
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar a solicitação: {str(e)}")

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Bem-vindo à API do Assistente de Ensino de Java. Acesse /docs para a documentação."}

import requests
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

# --- Configuração do Cliente ---
API_URL = "http://127.0.0.1:8000/chat"
console = Console()


def call_chat_api(message: str):
    """Envia uma mensagem para a API backend e retorna a resposta."""
    try:
        response = requests.post(API_URL, json={"message": message}, timeout=60)
        response.raise_for_status()  # Lança um erro para respostas 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"\n[bold red]Erro de Conexão:[/bold red] Não foi possível se conectar ao servidor da API em {API_URL}.")
        console.print("Por favor, certifique-se de que o servidor 'main.py' está rodando em outro terminal.")
        return None

def display_response(data: dict):
    """Formata e exibe a resposta estruturada da API usando rich."""
    
    # Lista para guardar as perguntas que serão retornadas
    follow_up_questions = []

    # Imprime as seções da explicação
    explicacao = data.get("explicacao", [])
    for i, secao in enumerate(explicacao):
        titulo = secao.get("titulo", "Sem Título")
        conteudo = secao.get("conteudo", "Sem conteúdo.")
        
        # Define cores diferentes para os painéis para melhor visualização
        cor_borda = "blue" if i % 2 == 0 else "magenta"
        
        panel = Panel(
            Text(conteudo, justify="left"),
            title=f"[bold]{titulo.upper()}[/bold]",
            border_style=cor_borda,
            padding=(1, 2)
        )
        console.print(panel)

    # Imprime a parte de verificação
    verificacao = data.get("verificacao", {})
    if verificacao:
        resumo_prompt = verificacao.get("resumo_prompt", "")
        perguntas = verificacao.get("perguntas_acompanhamento", [])

        console.print(Panel(
            Text(resumo_prompt, justify="center", style="italic"),
            title="[bold yellow]VERIFICAÇÃO DE APRENDIZAGEM[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        ))

        if perguntas:
            follow_up_text = Text("\nSugestões para continuar a conversa:", style="bold green")
            for i, pergunta in enumerate(perguntas, 1):
                follow_up_text.append(f"\n{i}. {pergunta}", style="default")
            
            console.print(follow_up_text)
            follow_up_questions = perguntas
            
    return follow_up_questions


if __name__ == "__main__":
    follow_up_questions = []

    console.print(Panel(
        "[bold green]Bem-vindo ao Assistente de Ensino de Java (CLI Interativo)[/bold green]\n\n"
        "Digite sua pergunta sobre Java, ou 'sair' para terminar.\n"
        "Se houver sugestões, você pode digitar o número da pergunta para selecioná-la.",
        title="Assistente Java",
        border_style="green"
    ))

    while True:
        try:
            # Usa o Prompt do rich para uma entrada mais elegante
            user_input = Prompt.ask("[bold cyan]>>> Sua pergunta[/bold cyan]")

            if user_input.lower() in ["sair", "exit", "quit"]:
                console.print("\n[bold]Até a próxima![/bold] 👋")
                break

            user_message = ""
            # Verifica se o usuário escolheu uma pergunta de acompanhamento
            if user_input.isdigit() and follow_up_questions:
                index = int(user_input) - 1
                if 0 <= index < len(follow_up_questions):
                    user_message = follow_up_questions[index]
                    console.print(f"\n[italic]Você selecionou: '{user_message}'[/italic]")
                else:
                    console.print("\n[yellow]Opção inválida. Por favor, digite uma nova pergunta.[/yellow]")
                    continue
            else:
                user_message = user_input
            
            with console.status("[bold green]Gerando a explicação... Aguarde um momento.[/bold green]", spinner="dots"):
                response_data = call_chat_api(user_message)

            if response_data:
                follow_up_questions.clear()
                follow_up_questions = display_response(response_data)
        
        except KeyboardInterrupt:
            console.print("\n\n[bold]Saindo... Até a próxima![/bold] 👋")
            sys.exit(0)
        except Exception as e:
            console.print(f"\n[bold red]Ocorreu um erro inesperado:[/bold red] {e}")

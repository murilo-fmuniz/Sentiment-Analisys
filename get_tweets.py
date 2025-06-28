import os
import asyncio
import csv
from datetime import datetime
from twikit import Client
from dotenv import load_dotenv

# --- Configurações ---
QUERIES = ['Palmeiras', 'Corinthians', 'São Paulo FC', 'Gremio', 'Flamengo']
TWEETS_POR_QUERY = 200
CSV_FILENAME = 'tweets_raspados.csv'
COOKIE_FILENAME = 'cookies.json'

# --- Carregamento de Variáveis de Ambiente ---
load_dotenv()
USERNAME = os.getenv('TWITTER_USERNAME')
EMAIL = os.getenv('TWITTER_EMAIL')
PASSWORD = os.getenv('TWITTER_PASSWORD')

# --- Inicialização ---
client = Client('pt-BR')
tweet_count = 0

async def autenticar_cliente():
    """
    Verifica se existe uma sessão de cookie válida.
    Se existir, carrega. Se não, faz um novo login e salva os cookies.
    """
    print("--- INICIANDO PROCESSO DE AUTENTICAÇÃO ---")
    if os.path.exists(COOKIE_FILENAME):
        print(f"Arquivo '{COOKIE_FILENAME}' encontrado. Carregando sessão...")
        client.load_cookies(COOKIE_FILENAME)
        try:
            # Tenta verificar se a sessão é válida fazendo uma chamada leve à API
            meu_usuario = await client.get_own_user()
            print(f"Sessão válida para o usuário: @{meu_usuario.screen_name}. Autenticação bem-sucedida!")
            return True
        except Exception as e:
            print(f"Sessão de cookie inválida ou expirada: {e}")
            print("Será necessário fazer um novo login.")
    
    # Se os cookies não existem ou são inválidos, faz o login
    print("Iniciando novo processo de login...")
    if not all([USERNAME, EMAIL, PASSWORD]):
        print("[ERRO FATAL] Credenciais não encontradas no arquivo .env para fazer novo login.")
        return False
        
    try:
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD
        )
        client.save_cookies(COOKIE_FILENAME)
        print(f"Login bem-sucedido! Nova sessão salva em '{COOKIE_FILENAME}'.")
        return True
    except Exception as e:
        print(f"[ERRO FATAL] Falha no login: {e}")
        print("Verifique suas credenciais no .env ou se há alguma verificação de segurança no Twitter.")
        return False


async def raspar_dados():
    """
    Função principal que executa a raspagem dos dados após a autenticação.
    """
    global tweet_count

    # Cria o cabeçalho do CSV
    with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nro_Tweet', 'Query', 'Usuario', 'Texto', 'Data de Criacao', 'Retweets', 'Likes'])

    # Itera sobre cada termo de busca
    for query in QUERIES:
        print(f"\n{'='*50}\nIniciando busca para a query: '{query}'\n{'='*50}")
        tweets = None
        local_tweet_count = 0
        max_retries = 30
        retry_count = 0

        while local_tweet_count < TWEETS_POR_QUERY:
            try:
                retry_count = 0
                if tweets is None:
                    print(f'{datetime.now()} - Buscando primeiros tweets para "{query}"...')
                    tweets = await client.search_tweet(query, 'Top')
                else:
                    print(f'{datetime.now()} - Buscando página seguinte de tweets...')
                    tweets = await tweets.next()

                if not tweets:
                    print(f'{datetime.now()} - Não foram encontrados mais tweets para "{query}"!')
                    break

                for tweet in tweets:
                    tweet_count += 1
                    local_tweet_count += 1
                    tweet_data = [
                        tweet_count, query, tweet.user.name, tweet.text,
                        tweet.created_at, tweet.retweet_count, tweet.favorite_count
                    ]
                    with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(tweet_data)
                    
                    if local_tweet_count >= TWEETS_POR_QUERY:
                        break
                
                print(f'{datetime.now()} - {local_tweet_count} tweets raspados para "{query}". Total no arquivo: {tweet_count}')
                await asyncio.sleep(5)

            except Exception as e:
                retry_count += 1
                print(f"\n[ERRO] Falha na busca para '{query}': {e}")
                if retry_count >= max_retries:
                    print(f"[AVISO] Máximo de tentativas ({max_retries}) atingido. Pulando para a próxima query.")
                    break
                else:
                    print(f"Tentativa {retry_count}/{max_retries}. Aguardando 60 segundos...")
                    await asyncio.sleep(60)
                    continue
        
        print(f"Finalizada a busca para '{query}'. Pausa de 15 segundos.")
        await asyncio.sleep(15)

    print(f"\nProcesso finalizado! Total de {tweet_count} tweets salvos em '{CSV_FILENAME}'.")


async def main():
    if await autenticar_cliente():
        print("\n--- INICIANDO PROCESSO DE RASPAGEM DE DADOS ---")
        await raspar_dados()
    else:
        print("\nNão foi possível autenticar. Encerrando o script.")

if __name__ == "__main__":
    asyncio.run(main())
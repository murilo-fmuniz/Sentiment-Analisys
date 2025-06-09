import os
import asyncio
import csv
from datetime import datetime
from twikit import Client
from dotenv import load_dotenv

load_dotenv()

QUERIES = ['Palmeiras', 'Corinthians', 'São Paulo FC', 'Gremio', 'Flamengo']

TWEETS_POR_QUERY = 200

CSV_FILENAME = 'tweets_raspados.csv'

USERNAME = os.getenv('TWITTER_USERNAME')
EMAIL = os.getenv('TWITTER_EMAIL')
PASSWORD = os.getenv('TWITTER_PASSWORD')

if not all([USERNAME, EMAIL, PASSWORD]):
    raise ValueError("Credenciais não encontradas no arquivo .env. Verifique o arquivo.")


client = Client('pt-BR')
tweet_count = 0

with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Nro_Tweet', 'Query', 'Usuario', 'Texto', 'Data de Criacao', 'Retweets', 'Likes'])


async def main():
    print(f'Esperando 15 segundos antes de buscar tweets....')
    await asyncio.sleep(15)
    global tweet_count

    print("Iniciando processo de raspagem de dados...")
    client.load_cookies('cookies.json')

    for query in QUERIES:
        print(f"\n{'='*50}\nIniciando busca para a query: '{query}'\n{'='*50}")

        tweets = None
        local_tweet_count = 0

        while local_tweet_count < TWEETS_POR_QUERY:
            try:
                if tweets is None:
                    print(f'{datetime.now()} - Buscando primeiros tweets para "{query}"...')
                    tweets = await client.search_tweet(query, 'Top')
                else:
                    print(f'{datetime.now()} - Buscando mais tweets...')
                    tweets = await tweets.next()

                if not tweets:
                    print(f'{datetime.now()} - Não foram encontrados mais tweets para "{query}"!')
                    break # Vai para a próxima query da lista

                for tweet in tweets:
                    tweet_count += 1
                    local_tweet_count += 1

                    tweet_data = [
                        tweet_count,
                        query,
                        tweet.user.name,
                        tweet.text,
                        tweet.created_at,
                        tweet.retweet_count,
                        tweet.favorite_count
                    ]

                    with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(tweet_data)
                    
                    if local_tweet_count >= TWEETS_POR_QUERY:
                        break
                
                print(f'{datetime.now()} - {local_tweet_count} tweets raspados para "{query}". Total no arquivo: {tweet_count}')

            except Exception as e:
                print(f"Ocorreu um erro durante a busca para '{query}': {e}")
                print("Aguardando 60 segundos antes de continuar...")
                await asyncio.sleep(60)
                break
        await asyncio.sleep(15)

    print(f"\nProcesso finalizado! Total de {tweet_count} tweets salvos em '{CSV_FILENAME}'.")


if __name__ == "__main__":
    asyncio.run(main())
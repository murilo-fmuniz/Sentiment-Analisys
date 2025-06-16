import os
import asyncio
from twikit import Client
from dotenv import load_dotenv

# Nome do arquivo onde os cookies serão salvos
COOKIE_FILE = 'cookies.json'

async def generate_cookies():
    """
    Realiza o login no Twitter com as credenciais do arquivo .env
    e salva os cookies de sessão em um arquivo JSON.
    """
    print("Carregando credenciais do arquivo .env...")
    load_dotenv()

    # Carrega as informações da conta a partir das variáveis de ambiente
    USERNAME = os.getenv('TWITTER_USERNAME')
    EMAIL = os.getenv('TWITTER_EMAIL')
    PASSWORD = os.getenv('TWITTER_PASSWORD')

    # Verifica se as credenciais foram carregadas corretamente
    if not all([USERNAME, EMAIL, PASSWORD]):
        print("\nERRO: Uma ou mais credenciais (USERNAME, EMAIL, PASSWORD) não foram encontradas.")
        print("Por favor, verifique se o arquivo .env está no mesmo diretório e configurado corretamente.")
        return

    print("Credenciais carregadas com sucesso.")
    client = Client('pt-BR')

    try:
        print(f"\nTentando fazer login com o usuário '{USERNAME}'...")
        # Realiza o login usando as credenciais
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD
        )
        print("Login bem-sucedido!")

        # Salva os cookies no arquivo especificado
        client.save_cookies(COOKIE_FILE)
        print(f"Cookies de sessão foram salvos com sucesso no arquivo '{COOKIE_FILE}'.")
        print("\nAgora você pode executar o seu script principal (main.py).")

    except Exception as e:
        print(f"\nERRO DURANTE O LOGIN: {e}")
        print("Verifique se suas credenciais estão corretas.")
        print("O Twitter pode exigir uma verificação de segurança (captcha ou e-mail). Se isso acontecer, tente fazer login pelo navegador primeiro.")


if __name__ == "__main__":
    # Executa a função assíncrona para gerar os cookies
    asyncio.run(generate_cookies())
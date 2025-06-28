# Nome do arquivo: analise_sentimento.py
# Objetivo: Pré-processar tweets e classificá-los com pysentimiento para treinamento.

import pandas as pd
import re
import os
import torch
from pysentimiento import create_analyzer

# --- CONFIGURAÇÕES ---
ARQUIVO_ENTRADA = 'tweets_raspados.csv'
ARQUIVO_SAIDA = 'tweets_para_treinamento.csv' # Nome otimizado para o próximo passo

# Mapeamento dos rótulos da biblioteca para os rótulos desejados
MAPA_SENTIMENTO = {
    'POS': 'Positivo',
    'NEG': 'Negativo',
    'NEU': 'Neutro'
}

def verificar_gpu():
    """Verifica se uma GPU compatível com CUDA está disponível e avisa o usuário."""
    if torch.cuda.is_available():
        print("✅ GPU detectada! A análise será acelerada.")
        print(f"Dispositivo: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️ GPU não detectada. A análise será executada em CPU (pode ser lento).")
    print("-" * 50)

def limpar_texto(texto: str) -> str:
    """
    Realiza a limpeza de um texto, removendo ruídos para a análise de sentimento.
    """
    # Esta verificação já lida com o caso de entrada não-string (incluindo NaN se não for tratado antes)
    if not isinstance(texto, str):
        return ""
    # Remove links (URLs)
    texto = re.sub(r'http\S+|www\S+', '', texto)
    # Remove menções (@usuario)
    texto = re.sub(r'@\w+', '', texto)
    # Remove o caractere de hashtag (#), mas mantém a palavra
    texto = re.sub(r'#', '', texto)
    # Remove caracteres que não são letras, números ou pontuação essencial
    texto = re.sub(r'[^\w\s.,!?-]', '', texto)
    # Remove espaços duplicados e espaços no início/fim
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def analisar_e_salvar():
    """
    Função principal que orquestra todo o processo.
    """
    verificar_gpu()

    # --- 1. CARREGAMENTO DOS DADOS ---
    print(f"Carregando dados do arquivo '{ARQUIVO_ENTRADA}'...")
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"ERRO: Arquivo de entrada '{ARQUIVO_ENTRADA}' não encontrado.")
        return

    df = pd.read_csv(ARQUIVO_ENTRADA)
    print(f"Carregados {len(df)} tweets.")
    
    # Armazena o número original de linhas antes da remoção
    linhas_originais = len(df)

    # --- REMOÇÃO COMPLETA DE NaN ---
    # Verifica e remove linhas onde 'Texto' ou 'Query' são NaN
    colunas_essenciais = ['Texto', 'Query']
    for col in colunas_essenciais:
        if col not in df.columns:
            print(f"⚠️ Aviso: A coluna '{col}' não foi encontrada no arquivo de entrada.")
            # Se a coluna não existe, não podemos remover NaN dela, então a pulamos
            # ou você pode decidir parar o script aqui se essa coluna for estritamente necessária.
            # Por enquanto, apenas avisamos e continuamos.
            colunas_essenciais.remove(col) # Remove da lista para não tentar dropar em coluna inexistente

    if colunas_essenciais: # Verifica se ainda há colunas para verificar
        print(f"Removendo linhas com valores nulos (NaN) nas colunas: {', '.join(colunas_essenciais)}...")
        df.dropna(subset=colunas_essenciais, inplace=True)
        linhas_removidas = linhas_originais - len(df)
        print(f"Foram removidas {linhas_removidas} linhas devido a valores NaN.")
        print(f"Restam {len(df)} tweets para processamento.")
    else:
        print("Não há colunas essenciais para verificar NaN ou elas não foram encontradas.")


    # --- VERIFICAÇÃO DA COLUNA 'Query' (mantida para robustez, embora NaN já tenham sido removidos) ---
    # Esta seção agora serve mais para confirmar a presença da coluna após a remoção de NaN
    if 'Query' not in df.columns:
        print(f"⚠️ A coluna 'Query' ainda não foi encontrada após a remoção de NaN.")
        print("Isso pode indicar que o arquivo de entrada não possui essa coluna ou que todas as linhas que a continham foram removidas.")
        df['Query'] = "" # Adiciona uma coluna vazia para evitar erros posteriores, se necessário
    else:
        print("✅ Coluna 'Query' está presente e livre de nulos nas linhas restantes.")


    # --- 2. PRÉ-PROCESSAMENTO ---
    print("\nIniciando pré-processamento e limpeza dos textos...")
    # Como 'Texto' já teve os NaN removidos, 'limpar_texto' receberá strings válidas
    df['texto_limpo'] = df['Texto'].apply(limpar_texto)
    
    # --- 3. ANÁLISE DE SENTIMENTO ---
    print("\nCarregando o modelo de sentimento 'bertweet-pt-sentiment'...")
    print("(Pode demorar alguns minutos na primeira execução para baixar o modelo)")
    analyzer = create_analyzer(task="sentiment", lang="pt")
    
    print(f"\nAnalisando {len(df)} tweets... Por favor, aguarde.")
    # Converte a coluna para uma lista para processamento em lote (muito mais rápido)
    textos_para_analise = df['texto_limpo'].tolist()
    
    # O analyzer processa a lista inteira de uma vez
    previsoes = analyzer.predict(textos_para_analise)
    
    # Extrai o resultado ('POS', 'NEG', 'NEU') e mapeia para os nomes desejados
    sentimentos_finais = [MAPA_SENTIMENTO.get(p.output) for p in previsoes]
    df['sentimento'] = sentimentos_finais
    print("Análise de sentimento concluída!")

    # --- 4. PREPARAÇÃO E SALVAMENTO DO ARQUIVO FINAL ---
    print(f"\nSalvando resultados no arquivo '{ARQUIVO_SAIDA}'...")
    # Seleciona as colunas essenciais para o treinamento com scikit-learn, incluindo 'Query'
    df_final = df[['texto_limpo', 'sentimento', 'Query']].copy()
    
    # Salva o arquivo final
    df_final.to_csv(ARQUIVO_SAIDA, index=False, encoding='utf-8')
    
    print("\n--- PROCESSO CONCLUÍDO COM SUCESSO! ---")
    print(f"O arquivo '{ARQUIVO_SAIDA}' está pronto para ser usado no treinamento do seu modelo.")
    print("\nDistribuição dos sentimentos encontrados:")
    print(df_final['sentimento'].value_counts())

if __name__ == '__main__':
    analisar_e_salvar()
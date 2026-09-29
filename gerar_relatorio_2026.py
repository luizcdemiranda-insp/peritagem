from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
import csv

# Use a mesma chave JSON que já autoriza suas automações no Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'caminho/para/sua/chave-bot-sistema-peritagem.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

# ID da pasta principal "OFICINA" que você compartilhou
PASTA_RAIZ_ID = '1OB6QU3o4Dto7AJMG3yXjti1B7_xWBgeW'

def levantar_arquivos_2026():
    resultados = []
    
    # 1. Encontra todas as pastas "ID XXXX - NOME DE CLIENTE" na raiz
    query_clientes = f"'{PASTA_RAIZ_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    pastas_clientes = service.files().list(q=query_clientes, fields="files(id, name)").execute().get('files', [])
    
    for cliente in pastas_clientes:
        # 2. Busca especificamente a subpasta "PERITAGEM" dentro do cliente
        query_perit = f"'{cliente['id']}' in parents and name='PERITAGEM' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        pastas_perit = service.files().list(q=query_perit, fields="files(id)").execute().get('files', [])
        
        for peritagem in pastas_perit:
            # 3. Lista apenas os arquivos (fotos/pdfs) criados em 2026
            query_arquivos = (
                f"'{peritagem['id']}' in parents and "
                f"createdTime >= '2026-01-01T00:00:00Z' and "
                f"createdTime <= '2026-12-31T23:59:59Z' and "
                f"mimeType != 'application/vnd.google-apps.folder' and trashed=false"
            )
            
            page_token = None
            while True:
                response = service.files().list(
                    q=query_arquivos,
                    fields='nextPageToken, files(id, name, createdTime)',
                    pageToken=page_token
                ).execute()
                
                for arquivo in response.get('files', []):
                    resultados.append({
                        'Cliente': cliente['name'],
                        'ID_Arquivo': arquivo['id'],
                        'Nome': arquivo['name'],
                        'Data_Criacao': arquivo['createdTime']
                    })
                    
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
                    
    return resultados

# Executa a varredura e exporta os dados
dados = levantar_arquivos_2026()
print(f"Total de arquivos de peritagem em 2026: {len(dados)}")

with open('levantamento_peritagens_2026.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Cliente', 'ID_Arquivo', 'Nome', 'Data_Criacao'])
    writer.writeheader()
    writer.writerows(dados)

print("Relatório salvo com sucesso: levantamento_peritagens_2026.csv")

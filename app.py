import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import time
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- IDs DOS REPOSITÓRIOS ---
DRIVE_FOLDER_ID = '1IOCs6mhGqX8Jgt0JnAHpTRtTYn1_Y8M6'
SHEET_ID = '1LD0s8o8kb3bYE5couyA72B0r7W4sggl3'
NOME_ABA_PENDENTES = 'Pendentes' # Ajuste para o nome real da sua aba
NOME_ABA_CONCLUIDOS = 'Concluidos' # Ajuste para o nome real da sua aba

# --- CONFIGURAÇÃO ---
st.set_page_config(
    page_title="Sistema de Peritagem",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INICIALIZAÇÃO DE MEMÓRIA (SESSION STATE) ---
if 'modulo_ativo' not in st.session_state:
    st.session_state['modulo_ativo'] = 'Dashboard'
if 'id_selecionado' not in st.session_state:
    st.session_state['id_selecionado'] = None
if 'etapa_peritagem' not in st.session_state:
    st.session_state['etapa_peritagem'] = 'lista_ids'

# --- IDENTIDADE VISUAL E CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #112240; border-right: 1px solid #233554; }
    p, h1, h2, h3, h4, h5, h6 { color: #e0e0e0 !important; }
    div[role="radiogroup"] > label > div:first-child { display: none !important; }
    div[role="radiogroup"] > label { padding: 12px 15px; border-radius: 8px; margin-bottom: 5px; color: #b0b4c4 !important; border-left: 4px solid transparent; background-color: transparent; transition: all 0.3s ease; cursor: pointer; width: 100%; }
    div[role="radiogroup"] > label:hover { background-color: rgba(255, 152, 0, 0.1); color: #ff9800 !important; }
    div[role="radiogroup"] > label[data-checked="true"] { border-left: 4px solid #ff9800; background-color: #112240; color: #ff9800 !important; box-shadow: 0 0 15px rgba(255, 152, 0, 0.5); }
    .tempermar-card { background-color: #112240; border: 1px solid #233554; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); transition: transform 0.2s ease, box-shadow 0.2s ease; }
    .tempermar-card:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(255, 152, 0, 0.3); border-color: #ff9800; }
    .stButton > button { width: 100%; border-radius: 8px; border: 1px solid #233554; background-color: #112240; color: #e0e0e0; transition: all 0.3s; }
    .stButton > button:hover { border-color: #ff9800; color: #ff9800; box-shadow: 0 0 15px rgba(255, 152, 0, 0.5); }
    </style>
""", unsafe_allow_html=True)

# --- INTEGRAÇÕES E PDF (MÓDULO 4 REAL) ---
@st.cache_resource
def get_google_credentials():
    """Amortecedor de Credenciais: Puxa os dados seguros do Streamlit Secrets"""
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    return creds

def gerar_pdf_peritagem(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, f"LAUDO DE PERITAGEM TÉCNICA - ID: {dados['id']}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "1. Inspeção Visual e Mecânica", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(0, 8, f"Notas Visuais: {dados['notas_visuais']}")
    pdf.cell(0, 8, f"Condição das Tampas/Mancais: {dados['tampas']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Condição do Eixo/Rotor: {dados['eixo']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "2. Ensaios Elétricos e Isolamento", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    res = dados['resistencia']
    pdf.cell(0, 8, f"Resistência Ôhmica (mOhm) -> Fase U: {res['U']} | Fase V: {res['V']} | Fase W: {res['W']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Índice de Polarização (IP): {dados['ip']} | Absorção Dielétrica (DAR): {dados['dar']}", new_x="LMARGIN", new_y="NEXT")
    estufa_txt = "Sim" if dados['estufa'] else "Não"
    pdf.cell(0, 8, f"Requer Ciclo de Secagem em Estufa: {estufa_txt}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    return bytes(pdf.output())

def upload_para_drive(id_pipedrive, pdf_bytes):
    creds = get_google_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    # Amortecedor de Busca: Tenta achar a pasta com o nome da ID criada pela Pluga
    query = f"name='{id_pipedrive}' and '{DRIVE_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    # Se achar a subpasta, salva nela. Se não achar, salva na pasta raiz fornecida.
    pasta_destino = items[0]['id'] if items else DRIVE_FOLDER_ID
        
    file_metadata = {
        'name': f'Laudo_Peritagem_{id_pipedrive}.pdf',
        'parents': [pasta_destino]
    }
    media = MediaIoBaseUpload(io.BytesIO(pdf_bytes), mimetype='application/pdf', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    
    return file.get('webViewLink')

def mover_linha_sheets(id_pipedrive):
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    doc = client.open_by_key(SHEET_ID)
    
    aba_pendentes = doc.worksheet(NOME_ABA_PENDENTES)
    aba_concluidos = doc.worksheet(NOME_ABA_CONCLUIDOS)
    
    # Amortecedor: Encontrar a linha baseada no ID e mover
    cell = aba_pendentes.find(id_pipedrive)
    if cell:
        linha_dados = aba_pendentes.row_values(cell.row)
        aba_concluidos.append_row(linha_dados)
        aba_pendentes.delete_rows(cell.row)
    return True

# --- NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("### 🧭 Menu Principal")
    menu_opcoes = ['Dashboard', 'Peritagem', 'Configurações']
    escolha = st.radio("Navegação", menu_opcoes, label_visibility="collapsed", index=menu_opcoes.index(st.session_state['modulo_ativo']))
    
    if escolha != st.session_state['modulo_ativo']:
        st.session_state['modulo_ativo'] = escolha
        st.rerun()

# --- CARGA DE DADOS (GOOGLE SHEETS REAL) ---
@st.cache_data(ttl=60) # Amortecedor: Recarrega a cada 60s para não esgotar a cota da API
# --- CARGA DE DADOS (GOOGLE SHEETS REAL) ---
@st.cache_data(ttl=60)
def carregar_dados_pendentes():
    # Retiramos o try/except para expor o erro real da API
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    # Se falhar nesta linha, o erro será WorksheetNotFound (nome da aba errado) 
    # ou SpreadsheetNotFound (botão compartilhar não foi configurado)
    sheet = client.open_by_key(SHEET_ID).worksheet(NOME_ABA_PENDENTES)
    
    dados = sheet.get_all_records()
    df = pd.DataFrame(dados)
    
    if df.empty:
        return pd.DataFrame()
        
    colunas_obrigatorias = ['ID_Pipedrive', 'Cliente', 'Equipamento', 'Status', 'Data_Entrada']
    for col in colunas_obrigatorias:
        if col not in df.columns:
            df[col] = "N/D" 
            
    df['Data_Entrada'] = pd.to_datetime(df['Data_Entrada'], errors='coerce')
    return df

# --- ROTEAMENTO DE PÁGINAS ---
if st.session_state['modulo_ativo'] == 'Dashboard':
    st.title("📊 Visão Geral")
    st.write("Aqui entrarão os Mini KPIs com bordas de status coloridas.")

elif st.session_state['modulo_ativo'] == 'Peritagem':
    if st.session_state['etapa_peritagem'] == 'lista_ids':
        st.title("📋 Área de Peritagem")
        st.markdown("<p style='color: #b0b4c4;'>Selecione uma ID pendente para iniciar o preenchimento.</p>", unsafe_allow_html=True)
        st.divider()
        
        with st.spinner("Sincronizando com Google Sheets..."):
            df_pendentes = carregar_dados_pendentes()
        
        if df_pendentes.empty:
            st.info("Nenhuma peritagem pendente no momento ou a planilha está vazia.")
            st.stop()
            
        cols = st.columns(3)
        for index, row in df_pendentes.iterrows():
            col = cols[index % 3]
            with col:
                cor_borda = "#ff4b4b" if row['Status'] == 'Atrasado' else "#ff9800"
                html_card = f"""
                <div class="tempermar-card" style="margin-bottom: 10px; border-bottom: 4px solid {cor_borda};">
                    <h3 style="margin-top:0; color: #ff9800; font-size: 1.2rem;">ID: {row['ID_Pipedrive']}</h3>
                    <p style="margin: 0px; font-size: 0.9rem;"><b>Cliente:</b> {row['Cliente']}</p>
                    <p style="margin: 0px; font-size: 0.9rem;"><b>Equip:</b> {row['Equipamento']}</p>
                    <p style="margin-top: 10px; font-size: 0.8rem; color: #b0b4c4;">
                        Entrada: {row['Data_Entrada'].strftime('%d/%m/%Y') if pd.notnull(row['Data_Entrada']) else 'N/D'}
                    </p>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                
                if st.button(f"Abrir Peritagem", key=f"btn_{row['ID_Pipedrive']}", type="primary"):
                    st.session_state['id_selecionado'] = row['ID_Pipedrive']
                    st.session_state['etapa_peritagem'] = 'formulario'
                    st.rerun()
                    
    elif st.session_state['etapa_peritagem'] == 'formulario':
        col_voltar, col_titulo = st.columns([1, 4])
        with col_voltar:
            if st.button("⬅️ Voltar"):
                st.session_state['etapa_peritagem'] = 'lista_ids'
                st.session_state['id_selecionado'] = None
                st.rerun()
                
        with col_titulo:
            st.title(f"🛠️ Peritagem: {st.session_state['id_selecionado']}")
            
        st.divider()
        
        with st.form(key="form_peritagem", clear_on_submit=False):
            st.markdown("<h3 style='color: #ff9800;'>1. Inspeção Visual e Mecânica</h3>", unsafe_allow_html=True)
            notas_visuais = st.text_area("Descreva as condições gerais do equipamento:")
            
            col_mecanica1, col_mecanica2 = st.columns(2)
            with col_mecanica1:
                tampas_status = st.selectbox("Condição das Tampas/Mancais:", ["Bom", "Avariado", "Requer Usinagem"])
            with col_mecanica2:
                eixo_status = st.selectbox("Condição do Eixo/Rotor:", ["Bom", "Desgaste Acentuado", "Empenado"])

            st.markdown("<h3 style='color: #ff9800; margin-top: 20px;'>2. Ensaios Elétricos Iniciais</h3>", unsafe_allow_html=True)
            col_eletrica1, col_eletrica2 = st.columns(2)
            
            with col_eletrica1:
                st.markdown("<p style='color: #b0b4c4; margin-bottom:0;'>Resistência Ôhmica (mOhm)</p>", unsafe_allow_html=True)
                resistencia_u = st.number_input("Fase U", min_value=0.0, format="%.2f")
                resistencia_v = st.number_input("Fase V", min_value=0.0, format="%.2f")
                resistencia_w = st.number_input("Fase W", min_value=0.0, format="%.2f")
                
            with col_eletrica2:
                st.markdown("<p style='color: #b0b4c4; margin-bottom:0;'>Medições de Isolamento (Megôhmetro)</p>", unsafe_allow_html=True)
                indice_polarizacao = st.number_input("Índice de Polarização (IP)", min_value=0.0, format="%.2f")
                absorcao_dieletrica = st.number_input("Absorção Dielétrica (DAR)", min_value=0.0, format="%.2f")
                st.markdown("<br>", unsafe_allow_html=True)
                requer_estufa = st.checkbox("Requer ciclo de secagem em estufa?")

            st.markdown("<h3 style='color: #ff9800; margin-top: 20px;'>3. Registro Fotográfico</h3>", unsafe_allow_html=True)
            fotos_anexadas = st.file_uploader("Anexe as fotos da peritagem", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            submit_peritagem = st.form_submit_button("💾 Salvar Peritagem e Gerar PDF", type="primary")
            
            if submit_peritagem:
                if not notas_visuais.strip():
                    st.error("⚠️ As notas de inspeção visual são obrigatórias.")
                elif len(fotos_anexadas) == 0:
                    st.warning("⚠️ É recomendável anexar ao menos uma foto do equipamento.")
                else:
                    dados_compilados = {
                        "id": st.session_state['id_selecionado'],
                        "notas_visuais": notas_visuais,
                        "tampas": tampas_status,
                        "eixo": eixo_status,
                        "resistencia": {"U": resistencia_u, "V": resistencia_v, "W": resistencia_w},
                        "ip": indice_polarizacao,
                        "dar": absorcao_dieletrica,
                        "estufa": requer_estufa,
                    }
                    
                    try:
                        with st.spinner("📄 Gerando Laudo em PDF..."):
                            pdf_bytes = gerar_pdf_peritagem(dados_compilados)
                            
                        with st.spinner("☁️ Localizando pasta e enviando para o Google Drive..."):
                            link_pasta = upload_para_drive(dados_compilados['id'], pdf_bytes)
                            
                        with st.spinner("📊 Movendo card e atualizando Google Sheets..."):
                            mover_linha_sheets(dados_compilados['id'])
                            carregar_dados_pendentes.clear() # Limpa o cache para forçar a atualização da tela
                            
                        st.success(f"✅ Peritagem da ID {dados_compilados['id']} concluída com sucesso!")
                        st.markdown(f"**Arquivos salvos no Drive:** [Acessar Arquivo]({link_pasta})")
                        
                        time.sleep(3)
                        st.session_state['etapa_peritagem'] = 'lista_ids'
                        st.session_state['id_selecionado'] = None
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Ocorreu um erro durante a integração: {str(e)}")
                        st.info("Os dados do formulário foram mantidos. Tente submeter novamente.")

elif st.session_state['modulo_ativo'] == 'Configurações':
    st.title("⚙️ Configurações do Sistema")
    st.write("Ajustes de integração, links do Google Drive, etc.")

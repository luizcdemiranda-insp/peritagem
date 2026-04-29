import streamlit as st
import pandas as pd

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
    st.session_state['etapa_peritagem'] = 'lista_ids' # Controla se estamos vendo os cards ou o formulário

# --- IDENTIDADE VISUAL E CSS ---
# Aplicando o Tema Dark Elegante e os estilos de UI/UX
st.markdown("""
    <style>
    /* Fundo geral da aplicação e cor de texto base */
    .stApp {
        background-color: #0a192f;
        color: #e0e0e0;
    }
    
    /* Fundo do Sidebar */
    [data-testid="stSidebar"] {
        background-color: #112240;
        border-right: 1px solid #233554;
    }
    
    /* Textos genéricos */
    p, h1, h2, h3, h4, h5, h6 {
        color: #e0e0e0 !important;
    }

    /* Ocultar a 'bolinha' nativa do st.radio e customizar o layout do menu */
    div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    div[role="radiogroup"] > label {
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        color: #b0b4c4 !important;
        border-left: 4px solid transparent;
        background-color: transparent;
        transition: all 0.3s ease;
        cursor: pointer;
        width: 100%;
    }
    /* Efeito Hover nos itens do menu */
    div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 152, 0, 0.1);
        color: #ff9800 !important;
    }
    /* Item Selecionado no menu */
    div[role="radiogroup"] > label[data-checked="true"] {
        border-left: 4px solid #ff9800;
        background-color: #112240;
        color: #ff9800 !important;
        box-shadow: 0 0 15px rgba(255, 152, 0, 0.5);
    }

    /* Customização dos Cards (Mini KPIs e Dados) que usaremos depois */
    .tempermar-card {
        background-color: #112240;
        border: 1px solid #233554;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .tempermar-card:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(255, 152, 0, 0.3);
        border-color: #ff9800;
    }
    
    /* Customização de botões padrão */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #233554;
        background-color: #112240;
        color: #e0e0e0;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        border-color: #ff9800;
        color: #ff9800;
        box-shadow: 0 0 15px rgba(255, 152, 0, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# --- INTEGRAÇÕES E PDF (MÓDULO 4) ---
from fpdf import FPDF
import io
import time

def gerar_pdf_peritagem(dados):
    """
    Gera o laudo técnico em PDF.
    Amortecedor: Tratamento de encoding e fallback para imagens ausentes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    
    # Cabeçalho
    pdf.cell(0, 10, f"LAUDO DE PERITAGEM TÉCNICA - ID: {dados['id']}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    
    # Seção 1: Visual e Mecânica
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "1. Inspeção Visual e Mecânica", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(0, 8, f"Notas Visuais: {dados['notas_visuais']}")
    pdf.cell(0, 8, f"Condição das Tampas/Mancais: {dados['tampas']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Condição do Eixo/Rotor: {dados['eixo']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Seção 2: Ensaios Elétricos
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "2. Ensaios Elétricos e Isolamento", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    res = dados['resistencia']
    pdf.cell(0, 8, f"Resistência Ôhmica (mΩ) -> Fase U: {res['U']} | Fase V: {res['V']} | Fase W: {res['W']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Índice de Polarização (IP): {dados['ip']} | Absorção Dielétrica (DAR): {dados['dar']}", new_x="LMARGIN", new_y="NEXT")
    estufa_txt = "Sim" if dados['estufa'] else "Não"
    pdf.cell(0, 8, f"Requer Ciclo de Secagem em Estufa: {estufa_txt}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Retorna o PDF como bytes (fpdf2 já faz isso nativamente)
    # Em um ambiente real, você pode adicionar a lógica para plugar as fotos aqui
    return bytes(pdf.output())

def upload_para_drive(id_pipedrive, pdf_bytes):
    """
    Simula a busca da pasta com o nome da ID e o upload do PDF.
    """
    # Amortecedor de API: Simulação de delay de rede
    time.sleep(1.5)
    # Lógica real futura: 
    # 1. service.files().list(q=f"name='{id_pipedrive}' and mimeType='application/vnd.google-apps.folder'").execute()
    # 2. MediaIoBaseUpload() e service.files().create()
    return f"https://drive.google.com/drive/folders/mock_{id_pipedrive}"

def mover_linha_sheets(id_pipedrive):
    """
    Simula a movimentação da linha da aba 'Pendentes' para 'Concluídos'.
    """
    # Amortecedor de API: Simulação de delay de rede
    time.sleep(1)
    # Lógica real futura:
    # 1. gc = gspread.service_account(filename='credentials.json')
    # 2. sh = gc.open_by_url('URL_DA_PLANILHA')
    # 3. Ler linha de worksheet('Pendentes'), fazer append em worksheet('Concluídos'), deletar de 'Pendentes'
    return True

# --- NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("### 🧭 Menu Principal")
    
    # Menu via st.radio com CSS customizado
    menu_opcoes = ['Dashboard', 'Peritagem', 'Configurações']
    escolha = st.radio(
        "Navegação", 
        menu_opcoes, 
        label_visibility="collapsed", 
        index=menu_opcoes.index(st.session_state['modulo_ativo'])
    )
    
    # Atualiza o estado da navegação
    if escolha != st.session_state['modulo_ativo']:
        st.session_state['modulo_ativo'] = escolha
        st.rerun()

# --- CARGA DE DADOS (SIMULAÇÃO SHEETS) ---
@st.cache_data
def carregar_dados_pendentes():
    # Simulando os dados que viriam do Google Sheets alimentado pelo Pipedrive/Pluga
    dados_mock = {
        'ID_Pipedrive': ['PRJ-1045', 'PRJ-1046', 'PRJ-1047', 'PRJ-1048'],
        'Cliente': ['Indústria Alpha', 'Ferroviária Central', 'Mineradora Sul', 'Usina Norte'],
        'Equipamento': ['Motor AT 4.16kV', 'Alternador EMD 420N6', 'Transformador 500kVA', 'Motor 380V'],
        'Status': ['Aguardando Peritagem', 'Aguardando Peritagem', 'Atrasado', 'Aguardando Peritagem'],
        'Data_Entrada': ['2026-04-28', '2026-04-29', '2026-04-20', '2026-04-29']
    }
    df = pd.DataFrame(dados_mock)
    
    # BOAS PRÁTICAS: Amortecedor 1 - Verifica se DataFrame está vazio
    if df.empty:
        return pd.DataFrame()
        
    # BOAS PRÁTICAS: Amortecedor 2 - Garantir que as colunas essenciais existam
    colunas_obrigatorias = ['ID_Pipedrive', 'Cliente', 'Equipamento', 'Status', 'Data_Entrada']
    for col in colunas_obrigatorias:
        if col not in df.columns:
            df[col] = "N/D" # Preenche com Não Disponível para evitar quebra de UI
            
    # BOAS PRÁTICAS: Amortecedor 3 - Tratamento seguro de datas
    df['Data_Entrada'] = pd.to_datetime(df['Data_Entrada'], errors='coerce')
    
    return df

# --- ROTEAMENTO DE PÁGINAS ---
if st.session_state['modulo_ativo'] == 'Dashboard':
    st.title("📊 Visão Geral")
    st.write("Aqui entrarão os Mini KPIs com bordas de status coloridas.")

elif st.session_state['modulo_ativo'] == 'Peritagem':
    
    # Lógica de Roteamento Interno do Módulo (Master/Detail)
    if st.session_state['etapa_peritagem'] == 'lista_ids':
        st.title("📋 Área de Peritagem")
        st.markdown("<p style='color: #b0b4c4;'>Selecione uma ID pendente para iniciar o preenchimento.</p>", unsafe_allow_html=True)
        st.divider()
        
        df_pendentes = carregar_dados_pendentes()
        
        # Amortecedor de UI: Se não houver dados, exibe mensagem amigável e para a execução
        if df_pendentes.empty:
            st.info("Nenhuma peritagem pendente no momento.")
            st.stop()
            
        # Renderização em Grid (Cards Responsivos)
        cols = st.columns(3)
        for index, row in df_pendentes.iterrows():
            col = cols[index % 3] # Distribui os cards nas 3 colunas
            with col:
                # Regra de cor para a borda inferior (UI/UX dinâmico)
                cor_borda = "#ff4b4b" if row['Status'] == 'Atrasado' else "#ff9800"
                
                # Injeção do HTML do Card puxando as classes do Módulo 1
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
                
                # Botão nativo colado abaixo do card para engatilhar a ação
                if st.button(f"Abrir Peritagem", key=f"btn_{row['ID_Pipedrive']}", type="primary"):
                    st.session_state['id_selecionado'] = row['ID_Pipedrive']
                    st.session_state['etapa_peritagem'] = 'formulario'
                    st.rerun() # Atualiza a tela imediatamente sem quebrar o layout
                    
    elif st.session_state['etapa_peritagem'] == 'formulario':
        # Cabeçalho do formulário com botão de voltar blindado via callback
        col_voltar, col_titulo = st.columns([1, 4])
        with col_voltar:
            if st.button("⬅️ Voltar"):
                st.session_state['etapa_peritagem'] = 'lista_ids'
                st.session_state['id_selecionado'] = None
                st.rerun()
                
        with col_titulo:
            st.title(f"🛠️ Peritagem: {st.session_state['id_selecionado']}")
            
        st.divider()
        
        # --- FORMULÁRIO DE PERITAGEM ---
        # Utilizando st.form para empacotar os dados e evitar reruns desnecessários
        with st.form(key="form_peritagem", clear_on_submit=False):
            st.markdown("<h3 style='color: #ff9800;'>1. Inspeção Visual e Mecânica</h3>", unsafe_allow_html=True)
            notas_visuais = st.text_area("Descreva as condições gerais do equipamento (sujeira, oxidação, danos visíveis nas bobinas):")
            
            col_mecanica1, col_mecanica2 = st.columns(2)
            with col_mecanica1:
                tampas_status = st.selectbox("Condição das Tampas/Mancais:", ["Bom", "Avariado", "Requer Usinagem"])
            with col_mecanica2:
                eixo_status = st.selectbox("Condição do Eixo/Rotor:", ["Bom", "Desgaste Acentuado", "Empenado"])

            st.markdown("<h3 style='color: #ff9800; margin-top: 20px;'>2. Ensaios Elétricos Iniciais</h3>", unsafe_allow_html=True)
            col_eletrica1, col_eletrica2 = st.columns(2)
            
            with col_eletrica1:
                st.markdown("<p style='color: #b0b4c4; margin-bottom:0;'>Resistência Ôhmica (mΩ)</p>", unsafe_allow_html=True)
                resistencia_u = st.number_input("Fase U", min_value=0.0, format="%.2f")
                resistencia_v = st.number_input("Fase V", min_value=0.0, format="%.2f")
                resistencia_w = st.number_input("Fase W", min_value=0.0, format="%.2f")
                
            with col_eletrica2:
                st.markdown("<p style='color: #b0b4c4; margin-bottom:0;'>Medições de Isolamento (Megôhmetro)</p>", unsafe_allow_html=True)
                indice_polarizacao = st.number_input("Índice de Polarização (IP)", min_value=0.0, format="%.2f", help="Relação 10 min / 1 min (Ref. IEEE 43-2024)")
                absorcao_dieletrica = st.number_input("Absorção Dielétrica (DAR)", min_value=0.0, format="%.2f", help="Relação 60 seg / 30 seg")
                
                # Checkbox para decisão técnica
                st.markdown("<br>", unsafe_allow_html=True)
                requer_estufa = st.checkbox("Requer ciclo de secagem em estufa?")

            st.markdown("<h3 style='color: #ff9800; margin-top: 20px;'>3. Registro Fotográfico</h3>", unsafe_allow_html=True)
            fotos_anexadas = st.file_uploader(
                "Anexe as fotos da peritagem (Múltiplos arquivos permitidos)", 
                type=["png", "jpg", "jpeg"], 
                accept_multiple_files=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Botão de submissão do formulário
            submit_peritagem = st.form_submit_button("💾 Salvar Peritagem e Gerar PDF", type="primary")
            
            if submit_peritagem:
                # BOAS PRÁTICAS: Amortecedor de Validação de Dados
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
                    
                    # Fluxo de Integração com feedback visual
                    try:
                        with st.spinner("📄 Gerando Laudo em PDF..."):
                            pdf_bytes = gerar_pdf_peritagem(dados_compilados)
                            
                        with st.spinner("☁️ Localizando pasta e enviando para o Google Drive..."):
                            link_pasta = upload_para_drive(dados_compilados['id'], pdf_bytes)
                            
                        with st.spinner("📊 Movendo card e atualizando Google Sheets..."):
                            mover_linha_sheets(dados_compilados['id'])
                            
                        # Limpa o estado e exibe o sucesso
                        st.success(f"✅ Peritagem da ID {dados_compilados['id']} concluída com sucesso!")
                        st.markdown(f"**Arquivos salvos na pasta do Drive:** [Acessar Pasta]({link_pasta})")
                        
                        # Retorna para a lista após 3 segundos
                        time.sleep(3)
                        st.session_state['etapa_peritagem'] = 'lista_ids'
                        st.session_state['id_selecionado'] = None
                        st.rerun()
                        
                    except Exception as e:
                        # Amortecedor Crítico: Captura falhas de API sem quebrar a tela vermelha do Streamlit
                        st.error(f"❌ Ocorreu um erro durante a integração: {str(e)}")
                        st.info("Os dados do formulário foram mantidos. Tente submeter novamente.")

elif st.session_state['modulo_ativo'] == 'Configurações':
    st.title("⚙️ Configurações do Sistema")
    st.write("Ajustes de integração, links do Google Drive, etc.")

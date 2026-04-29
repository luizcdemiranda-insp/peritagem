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

# --- ROTEAMENTO DE PÁGINAS ---
if st.session_state['modulo_ativo'] == 'Dashboard':
    st.title("📊 Visão Geral")
    st.write("Aqui entrarão os Mini KPIs com bordas de status coloridas.")

elif st.session_state['modulo_ativo'] == 'Peritagem':
    st.title("📋 Área de Peritagem")
    st.write("Aqui vamos listar os IDs que vêm do Google Sheets e abrir os formulários.")

elif st.session_state['modulo_ativo'] == 'Configurações':
    st.title("⚙️ Configurações do Sistema")
    st.write("Ajustes de integração, links do Google Drive, etc.")

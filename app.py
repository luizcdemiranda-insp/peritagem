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
        st.info("Aqui vamos construir os campos do formulário (fotos, dados digitáveis, etc.) no próximo módulo.")

elif st.session_state['modulo_ativo'] == 'Configurações':
    st.title("⚙️ Configurações do Sistema")
    st.write("Ajustes de integração, links do Google Drive, etc.")

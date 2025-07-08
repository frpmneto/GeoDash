import streamlit as st
import geopandas as gpd
import geobr
from streamlit_folium import st_folium

# Configuração da página do Streamlit
st.set_page_config(layout="wide")

# Título do seu aplicativo
st.title("Mapa Interativo de Municípios por Estado")
st.write("Escolha um estado no menu lateral para visualizar seus municípios.")

# --- Dicionário de Estados e UFs para o dropdown ---
# Fonte: geobr.list_geobr()
estados_brasileiros = {
    'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM',
    'Bahia': 'BA', 'Ceará': 'CE', 'Distrito Federal': 'DF', 'Espírito Santo': 'ES',
    'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT', 'Mato Grosso do Sul': 'MS',
    'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
    'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ',
    'Rio Grande do Norte': 'RN', 'Rio Grande do Sul': 'RS', 'Rondônia': 'RO',
    'Roraima': 'RR', 'Santa Catarina': 'SC', 'São Paulo': 'SP',
    'Sergipe': 'SE', 'Tocantins': 'TO'
}

# --- Sidebar para controles ---
st.sidebar.header("Controles do Mapa")

# Dropdown para selecionar o estado
# Usamos .keys() para mostrar os nomes completos na lista
estado_selecionado_nome = st.sidebar.selectbox(
    "Escolha o Estado:",
    options=list(estados_brasileiros.keys()),
    index=16 # Define Pernambuco como padrão
)

# Obter a sigla (UF) a partir do nome do estado selecionado
uf_selecionada = estados_brasileiros[estado_selecionado_nome]


# --- Cache para otimizar o carregamento dos dados ---
@st.cache_data
def carregar_dados_estado(uf):
    """
    Carrega os dados dos municípios para a UF especificada.
    A anotação @st.cache_data garante que os dados não sejam baixados novamente
    se a mesma UF for selecionada.
    """
    try:
        gdf = geobr.read_municipality(code_muni=uf, year=2020)
        return gdf
    except Exception as e:
        st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
        return None

# Carrega os dados para o estado selecionado
gdf_estado = carregar_dados_estado(uf_selecionada)


# --- Criação e exibição do mapa ---
st.subheader(f"Mapa dos Municípios de {estado_selecionado_nome}")

if gdf_estado is not None:
    # 1. Cria o mapa com .explore()
    m = gdf_estado.explore(
        column="name_muni",
        tooltip="name_muni",
        popup=True,
        tiles="CartoDB positron",
        # cmap="viridis",
        style_kwds=dict(color="black", weight=0.5)
    )

    # 2. Renderiza o mapa no Streamlit
    st_folium(m, width='100%', height=600, use_container_width=True)
    # Opcional: Mostrar a tabela de dados
    if st.sidebar.checkbox("Mostrar tabela de dados"):
        st.subheader("Dados Tabulares")
        st.dataframe(gdf_estado.drop(columns='geometry'))
else:
    st.warning("Não há dados para exibir. Por favor, selecione outro estado.")
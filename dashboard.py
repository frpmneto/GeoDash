import streamlit as st
import geopandas as gpd
import geobr
from streamlit_folium import st_folium





# Configuração da página do Streamlit
st.set_page_config(layout="wide")











# Título do aplicativo
st.title("Mapa Interativo de Municípios por Estado")
st.write("Escolha seus filtros no menu lateral para visualizar o mapa e suas estatísticas.")









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
# Seletor de tema
tema_do_grafico = st.sidebar.selectbox(
    "Escolha o tema a ser visualizado:",
    options=['Municipios', "Escolas"],
    # options=['Municipios', "População", "Escolas", "Saúde", "Economia"],
    index=0 # Define municipios como padrão
)
# Seletor de estado
estado_selecionado_nome = st.sidebar.selectbox(
    "Escolha o Estado:",
    options=list(estados_brasileiros.keys()),
    index=16 # Define Pernambuco como padrão
)
# seletor de municipio
uf = estados_brasileiros[estado_selecionado_nome]
gdf = geobr.read_municipality(code_muni=uf, year=2020)
municipios_unicos = list(set(gdf['name_muni']))
municipios_unicos.sort()
municipios_unicos.insert(0,'Todos')
estado_selecionado_nome = st.sidebar.selectbox(
    "Escolha o Municipio:",
    options=municipios_unicos,
    index=0 # Define todos como padrão
)



# Carrega os dados para o estado selecionado
gdf = None

if tema_do_grafico == 'Escolas':
  
    # Carrega os dados de escolas para o estado selecionado
    try:
        base_escolas = geobr.read_schools(year=2020)
        gdf = base_escolas[base_escolas.abbrev_state == uf]
        if estado_selecionado_nome != 'Todos':
            gdf = gdf[gdf.name_muni == estado_selecionado_nome]
    except Exception as e:
        st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
    
    # define os parametros do mapa
    m = gdf.explore(
        # m=m,
        column='government_level',
        tooltip=False,
        # scheme= 'naturalbreaks',
        cmap='Spectral',
        name='Escolas de Recife',
        popup=['name_school', 'address', 'government_level', 'phone_number'],
        legend_kwds=dict(caption='Tipo da escola'),
        # marker_type = 'circle_marker',
        marker_kwds=dict(radius=5)
    )

elif tema_do_grafico == 'Municipios':
    try:
        gdf = geobr.read_municipality(code_muni=uf, year=2020)
        if estado_selecionado_nome != 'Todos':
            gdf = gdf[gdf.name_muni == estado_selecionado_nome]
    except Exception as e:
        st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
    # Para o tema "Municipios", usamos a geometria do estado selecionado
    # m = gdf_estado.explore(
    #     tooltip=False,
    #     color='black',
    #     style_kwds=dict(fillOpacity=0.2),
    #     highlight=False
    # )
    m = gdf.explore(
        column="name_muni",
        tooltip="name_muni",
        popup=True,
        style_kwds=dict(color="black", weight=0.5)
    )    



# --- Criação e exibição do mapa ---
st.subheader(f"Mapa dos Municípios de {estado_selecionado_nome}")

if gdf is not None:
    # 1. Cria o mapa com .explore()


    
    # m = gdf_estado.explore(
    #     column="name_muni",
    #     tooltip="name_muni",
    #     popup=True,
    #     tiles="CartoDB positron",
    #     # cmap="viridis",
    #     style_kwds=dict(color="black", weight=0.5)
    # )
    # mapa = base_filtrada.explore(
    #     m=m,
    #     column='government_level',
    #     tooltip=False,
    #     # scheme= 'naturalbreaks',
    #     cmap='Spectral',
    #     name='Escolas de Recife',
    #     popup=['name_school', 'address', 'government_level', 'phone_number'],
    #     legend_kwds=dict(caption='Tipo da escola'),
    #     # marker_type = 'circle_marker',
    #     marker_kwds=dict(radius=5)
    # )
    # 2. Renderiza o mapa no Streamlit
    st_folium(m, width='100%', height=600, use_container_width=True)
    # Opcional: Mostrar a tabela de dados
    if st.sidebar.checkbox("Mostrar tabela de dados"):
        st.subheader("Dados Tabulares")
        if tema_do_grafico == 'Escolas':
            cols = ['name_school', 'education_level', 'admin_category', 'government_level', 'size', 'urban', 'name_state', 'name_muni_right' ]
            # ['abbrev_state_left', 'name_muni_left', 'code_school', 'name_school', 'education_level', 'education_level_others', 'admin_category', 'address', 'phone_number', 'government_level', 'private_school_type', 'private_government_partnership', 'regulated_education_council', 'service_restriction', 'size', 'urban', 'location_type', 'date_update', 'geometry', 'index_right', 'code_muni', 'name_muni_right', 'code_state', 'abbrev_state_right', 'name_state', 'code_region', 'name_region']
            # todrop = ['geometry', 'index_right', 'id_school', 'id_muni', 'id_state', 'code_muni', 'code_region', 'code_state']
            st.dataframe(gdf[cols])
            # st.dataframe(base_filtrada)
else:
    st.warning("Não há dados para exibir. Por favor, selecione outro estado.")
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
    options=['Municipios', "Escolas", 'Terras Indígenas', 'Outro'],
    index=0 # Define municipios como padrão
)
# Seletor de estado

estados = list(estados_brasileiros.keys())
estado_selecionado_nome = st.sidebar.selectbox(
    "Escolha o Estado:",
    options= estados,
    index=16 # Define Pernambuco como padrão
)
# seletor de municipio
uf = estados_brasileiros[estado_selecionado_nome]

gdf = geobr.read_municipality(code_muni=uf, year=2020)
municipios_unicos = list(set(gdf['name_muni']))
municipios_unicos.sort()
municipios_unicos.insert(0,'Todos')
# estado_selecionado_nome = st.sidebar.selectbox(
municipio_selecionado_nome = st.sidebar.selectbox(
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
        if municipio_selecionado_nome != 'Todos':
            gdf = gdf[gdf.name_muni == municipio_selecionado_nome]
    except Exception as e:
        st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
    
    # define os parametros do mapa
    if municipio_selecionado_nome != 'Todos':
        try:
            rec = geobr.read_municipality(code_muni=uf, year=2020)
            rec = rec[rec.name_muni == municipio_selecionado_nome]
        except Exception as e:
            st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
        mapa = rec.explore(
            tooltip=False,
            color='black',
            style_kwds=dict(fillOpacity=0.2),
            highlight=False
        )
        m = gdf.explore(
            m=mapa,
            column='government_level',
            tooltip=False,
            # scheme= 'naturalbreaks',
            # cmap='Spectral',
            name='Escolas de Recife',
            popup=['name_school', 'address', 'government_level', 'phone_number', 'name_muni'],
            legend_kwds=dict(caption='Tipo da escola'),
            # marker_type = 'circle_marker',
            marker_kwds=dict(radius=5)
        )
    else:
        try:
            per = geobr.read_state(code_state=uf, year=2020)
        except Exception as e:
            st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
        mapa = per.explore(
            tooltip=False,
            color='black',
            style_kwds=dict(fillOpacity=0.2),
            highlight=False
        )
        cols = ['name_school', 'education_level', 'admin_category', 'government_level', 'size', 'urban', 'name_muni', 'abbrev_state']
        m = gdf.explore(
            m=mapa,
            column='government_level',
            tooltip=cols,
            # scheme= 'naturalbreaks',
            cmap='Spectral',
            name='Escolas de Recife',
            popup=['name_school', 'address', 'government_level', 'phone_number', 'name_muni'],
            legend_kwds=dict(caption='Tipo da escola'),
            # marker_type = 'circle_marker',
            marker_kwds=dict(radius=5)
        )
   
elif tema_do_grafico == 'Municipios':
    try:
        gdf = geobr.read_municipality(code_muni=uf, year=2020)
        if municipio_selecionado_nome != 'Todos':
            gdf = gdf[gdf.name_muni == municipio_selecionado_nome]
    except Exception as e:
        st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
    # adicionando a coluna da area do municipio
    gdf_projetado = gdf.to_crs('ESRI:102033') # precisa converter para um sistema de coordenadas projetadas para calcular a área corretamente em km2 e nao em graus2
    gdf['area_km2'] = gdf_projetado.geometry.area / 1_000_000 # converte de metros quadrados para quilômetros quadrados
    gdf['area_km2'] = gdf['area_km2'].round(2)
    # seleciona as colunas para exibir na tabela
    cols = ['name_muni', 'name_state', 'name_region', 'area_km2']
    m = gdf.explore(
        column="name_muni",
        tooltip=cols,
        popup=True,
        style_kwds=dict(color="black", weight=0.5)
    )    

elif tema_do_grafico == 'Terras Indígenas':
    try:
        gdf = geobr.read_indigenous_land()
        if estado_selecionado_nome != 'Todos':
            gdf = gdf[gdf['abbrev_state'].str.contains(uf, na=False)]
        if municipio_selecionado_nome != 'Todos':
            gdf = gdf[gdf['name_muni'].str.contains(municipio_selecionado_nome, na=False)]
    except Exception as e:    
        st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
    
    # seleciona as colunas para exibir na tabela
    cols = ['terrai_nom', 'etnia_nome', 'superficie', 'modalidade', 'name_muni', 'abbrev_state']  # Colunas vazias, pois não há dados tabulares para exibir neste caso

    m = gdf.explore(
        column="terrai_nom",
        tooltip=cols,
        popup=True,
        style_kwds=dict(color="black", weight=0.5)
    )    

elif tema_do_grafico == 'Outro':
    try:
        gdf = geobr.read_municipality(code_muni=uf, year=2020)
        if municipio_selecionado_nome != 'Todos':
            gdf = gdf[gdf.name_muni == municipio_selecionado_nome]
    except Exception as e:
        st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
    
    m = gdf.explore(
        column="name_muni",
        tooltip="name_muni",
        popup=True,
        style_kwds=dict(color="black", weight=0.5)
    )    
    # adicionando a coluna da area do municipio
    gdf_projetado = gdf.to_crs('ESRI:102033') # precisa converter para um sistema de coordenadas projetadas para calcular a área corretamente em km2 e nao em graus2
    gdf['area_km2'] = gdf_projetado.geometry.area / 1_000_000 # converte de metros quadrados para quilômetros quadrados

    # seleciona as colunas para exibir na tabela
    cols = ['name_muni', 'name_state', 'name_region', 'area_km2']














# --- Criação e exibição do mapa ---
if municipio_selecionado_nome == 'Todos':
    estado_ou_municipio = estado_selecionado_nome
else:
    estado_ou_municipio = f"{municipio_selecionado_nome} - {uf}"
st.subheader(f"Mapa de {tema_do_grafico} de {estado_ou_municipio}")

if gdf is not None:
    
    # Renderiza o mapa no Streamlit
    st_folium(m, width='100%', height=600, use_container_width=True)
    
    # Opcional: Mostrar a tabela de dados
    if st.sidebar.checkbox("Mostrar tabela de dados"):
        st.subheader("Dados Tabulares")
        # if tema_do_grafico == 'Escolas':
        if cols != []:
            st.dataframe(gdf[cols])
        else:
            st.dataframe(gdf)
else:
    st.warning("Não há dados para exibir. Por favor, selecione outro estado.")
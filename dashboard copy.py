# app_educacao_ibge.py

import streamlit as st
import pandas as pd
import sidrapy
import folium
from streamlit_folium import st_folium

# --- Configurações da Página e Título ---
st.set_page_config(layout="wide")
st.title("📊 Dashboard de Dados Educacionais do Brasil (PNAD/IBGE)")
st.markdown("Dados da tabela **6417** do SIDRA/IBGE para o ano de **2022**.")
st.markdown("Pessoas de 10 anos ou mais de idade, por nível de ensino, sexo e cor ou raça.")

# --- Cache e Carregamento dos Dados ---
# @st.cache_data garante que os dados sejam baixados do SIDRA apenas uma vez.
@st.cache_data
def carregar_dados_sidra():
    """
    Busca os dados na API do SIDRA/IBGE e faz uma limpeza inicial.
    """
    try:
        df = sidrapy.get_table(
            table_code='6417',
            territorial_level='3',      # 3 = Unidade da Federação
            ibge_territorial_code='all',
            period='2022',
            variable='140',             # Pessoas de 10 anos ou mais de idade
            classifications={
                "133": "95263,95277,2826,2827,95274,95275,2836,12890,2837", # Cursos que frequentava
                "2": "4,5",             # Sexo
                "86": "2776,2777,2778,2779,2780" # Cor ou raça
            },
            format='pandas'
        )
        # Limpeza e Renomeação das colunas para facilitar o uso
        df_limpo = df.rename(columns={
            'V': 'Valor',
            'D1N': 'Unidade da Federação',
            'D5N': 'Sexo',
            'D6N': 'Cor ou raça',
            'D7N': 'Nível de Ensino'
        })

        # Selecionar colunas relevantes e converter 'Valor' para numérico
        colunas_relevantes = ['Unidade da Federação', 'Sexo', 'Cor ou raça', 'Nível de Ensino', 'Valor']
        df_limpo = df_limpo[colunas_relevantes]
        df_limpo['Valor'] = pd.to_numeric(df_limpo['Valor'], errors='coerce').fillna(0)
        
        # Criar coluna com a sigla do estado para o mapa
        df_limpo['UF'] = df_limpo['Unidade da Federação'].map(mapa_uf_sigla)
        
        return df_limpo

    except Exception as e:
        st.error(f"Erro ao carregar os dados do SIDRA: {e}")
        return pd.DataFrame()

# Dicionário para mapear nome do estado para sua sigla
mapa_uf_sigla = {
    'Rondônia': 'RO', 'Acre': 'AC', 'Amazonas': 'AM', 'Roraima': 'RR', 'Pará': 'PA',
    'Amapá': 'AP', 'Tocantins': 'TO', 'Maranhão': 'MA', 'Piauí': 'PI', 'Ceará': 'CE',
    'Rio Grande do Norte': 'RN', 'Paraíba': 'PB', 'Pernambuco': 'PE', 'Alagoas': 'AL',
    'Sergipe': 'SE', 'Bahia': 'BA', 'Minas Gerais': 'MG', 'Espírito Santo': 'ES',
    'Rio de Janeiro': 'RJ', 'São Paulo': 'SP', 'Paraná': 'PR', 'Santa Catarina': 'SC',
    'Rio Grande do Sul': 'RS', 'Mato Grosso do Sul': 'MS', 'Mato Grosso': 'MT',
    'Goiás': 'GO', 'Distrito Federal': 'DF'
}

# Carregar os dados
df_completo = carregar_dados_sidra()

if not df_completo.empty:
    # --- Barra Lateral com Filtros ---
    st.sidebar.header("Filtros para o Mapa")

    # Opções de filtro
    filtro_principal = st.sidebar.selectbox(
        "Visualizar por:",
        ["Total Geral", "Sexo", "Cor ou raça", "Nível de Ensino"]
    )

    df_filtrado = df_completo.copy()
    titulo_mapa = "Total de Pessoas (10 anos ou mais)"

    # Lógica para aplicar filtros secundários
    if filtro_principal == "Sexo":
        opcao_sexo = st.sidebar.selectbox("Selecione o Sexo:", df_completo['Sexo'].unique())
        df_filtrado = df_completo[df_completo['Sexo'] == opcao_sexo]
        titulo_mapa = f"Pessoas do sexo '{opcao_sexo}'"

    elif filtro_principal == "Cor ou raça":
        opcao_raca = st.sidebar.selectbox("Selecione a Cor/Raça:", df_completo['Cor ou raça'].unique())
        df_filtrado = df_completo[df_completo['Cor ou raça'] == opcao_raca]
        titulo_mapa = f"Pessoas da cor/raça '{opcao_raca}'"

    elif filtro_principal == "Nível de Ensino":
        opcao_ensino = st.sidebar.selectbox("Selecione o Nível de Ensino:", df_completo['Nível de Ensino'].unique())
        df_filtrado = df_completo[df_completo['Nível de Ensino'] == opcao_ensino]
        titulo_mapa = f"Pessoas no nível '{opcao_ensino}'"

    # --- Processamento para o Mapa ---
    # Agrupar por estado (UF) e somar os valores após o filtro
    dados_mapa = df_filtrado.groupby('UF')['Valor'].sum().reset_index()

    # --- Exibição do Mapa ---
    st.header(f"🗺️ Mapa: {titulo_mapa}")

    # URL do GeoJSON com as fronteiras dos estados do Brasil
    geojson_url = "https://raw.githubusercontent.com/luizpedone/municipal-brazilian-geodata/master/data/UF.json"
    
    # Criar mapa base centrado no Brasil
    mapa = folium.Map(location=[-15.788497, -47.879873], zoom_start=4)

    # Criar o mapa coroplético
    folium.Choropleth(
        geo_data=geojson_url,
        data=dados_mapa,
        columns=['UF', 'Valor'],
        key_on='feature.properties.SIGLA_UF', # Chave no GeoJSON que corresponde à nossa coluna 'UF'
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=titulo_mapa,
        highlight=True
    ).add_to(mapa)

    # Renderizar o mapa no Streamlit
    st_folium(mapa, width=1200, height=600)

    # --- Exibição do DataFrame ---
    with st.expander("Clique para ver a tabela de dados agregados usada no mapa"):
        st.dataframe(dados_mapa.sort_values('Valor', ascending=False), use_container_width=True)
    
    with st.expander("Clique para ver a tabela de dados brutos completa do SIDRA"):
        st.dataframe(df_completo, use_container_width=True)
else:
    st.warning("Não foi possível carregar os dados. Verifique a conexão ou os parâmetros da API.")

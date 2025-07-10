import streamlit as st
import geopandas as gpd
import geobr
from streamlit_folium import st_folium
import sidrapy
import pandas as pd
import plotly as plt
import geobr as geo
import plotly.express as px
import warnings
from branca.element import MacroElement
from jinja2 import Template



# Configuração da página do Streamlit
st.set_page_config(layout="wide")
warnings.filterwarnings("ignore")




gdf = None
rec = None
per = None


@st.cache_data  # Cache para os dados de municípios por estado
def carregar_municipios(uf):
    return geobr.read_municipality(code_muni=uf, year=2020)

@st.cache_data  # Cache para os dados de terras indigenas por estado
def carregar_indis():
    return geobr.read_indigenous_land()

@st.cache_data  # Cache para os dados de escolas por estado
def carregar_escolas():
    return geobr.read_schools(year=2020)

@st.cache_data  # Cache para os dados de escolas por estado
def carregar_estados(uf):
    return geobr.read_state(code_state=uf, year=2020)
    
# @st.cache_data
# def gerar_mapa(gdf=0,tooltip, column, cmap, name, popup, legend_kwds, marker_kwds, color, highlight=True):
#     x()
#     df = 0

#     m = ''
#     return m
@st.cache_data
def gerar_mapa(df=0, **kwargs):
    if df == 0:
        m = gdf.explore(**kwargs)
        return m
    elif df == 1:
        mapa = rec.explore(
            tooltip=False,
            color='black',
            style_kwds=dict(fillOpacity=0.2),
            highlight=False
        )
        m = gdf.explore(
            m=mapa,
            column='government_level',
            tooltip=cols,
            name='Escolas de Recife',
            popup=['name_school', 'address', 'government_level', 'phone_number', 'name_muni'],
            legend_kwds=dict(caption='Tipo da escola'),
            marker_kwds=dict(radius=5)
        )
        return m
    elif df == 2:
        mapa = per.explore(
            tooltip=False,
            color='black',
            style_kwds=dict(fillOpacity=0.2),
            highlight=False
        )        
        m = gdf.explore(
            m=mapa,
            column='government_level',
            tooltip=cols,
            cmap='Spectral',
            name='Escolas de Recife',
            popup=['name_school', 'address', 'government_level', 'phone_number', 'name_muni'],
            legend_kwds=dict(caption='Tipo da escola'),
            marker_kwds=dict(radius=5)
        )
        return m
   
    m = df.explore(**kwargs)
    return m











# --- Dicionário de Estados e UFs para o dropdown ---
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
    options=['Municipios', "Escolas", 'Terras Indígenas'],
    # options=['Municipios', "Escolas", 'Terras Indígenas', 'Religião', 'Sexo', 'Cor/Raça'],
    index=0 # Define municipios como padrão
)
# Seletor de estado

estados = list(estados_brasileiros.keys())
estado_selecionado_nome = st.sidebar.selectbox(
    "Escolha o Estado:",
    options= estados,
    index=16 # Define Pernambuco como padrão
)


if tema_do_grafico in ['Terras Indígenas', 'Escolas', 'Municipios']:
    # Título do aplicativo
    st.title("Mapa Interativo de Municípios por Estado")
    st.write("Escolha seus filtros no menu lateral para visualizar o mapa e suas estatísticas.")
    # seletor de municipio
    uf = estados_brasileiros[estado_selecionado_nome]

    gdf = carregar_municipios(uf)
    municipios_unicos = list(set(gdf['name_muni']))
    municipios_unicos.sort()
    municipios_unicos.insert(0,'Todos')
    # estado_selecionado_nome = st.sidebar.selectbox(
    municipio_selecionado_nome = st.sidebar.selectbox(
        "Escolha o Municipio:",
        options=municipios_unicos,
        index=0 # Define todos como padrão
    )
else:
    # Título do aplicativo
    st.title("Gráficos dos Dados Demográficos retirados do SIDRA")
    st.write("Escolha o tema e o estado para visualizar os gráficos.")

# Carrega os dados para o estado selecionado
gdf = None

@st.cache_data
def ler_dataframe():
    dataframe = pd.read_csv('merged_df.csv')
    return dataframe

merged_df = ler_dataframe()
state_name = estado_selecionado_nome
if tema_do_grafico == 'Escolas':
  
    # Carrega os dados de escolas para o estado selecionado
    try:
        base_escolas = carregar_escolas()
        gdf = base_escolas[base_escolas.abbrev_state == uf]
        if municipio_selecionado_nome != 'Todos':
            gdf = gdf[gdf.name_muni == municipio_selecionado_nome]
    except Exception as e:
        st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
    cols = ['name_school', 'education_level', 'admin_category', 'government_level', 'size', 'urban', 'name_muni', 'abbrev_state']
    # define os parametros do mapa
    if municipio_selecionado_nome != 'Todos':
        try:
            rec = carregar_municipios(uf)
            rec = rec[rec.name_muni == municipio_selecionado_nome]
        except Exception as e:
            st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
        
        # m = gerar_mapa(df=1)
        mapa = rec.explore(
            tooltip=False,
            color='black',
            style_kwds=dict(fillOpacity=0.2),
            highlight=False
        )
        m = gdf.explore(
            m=mapa,
            column='government_level',
            tooltip=cols,
            name='Escolas de Recife',
            popup=['name_school', 'address', 'government_level', 'phone_number', 'name_muni'],
            legend_kwds=dict(caption='Tipo da escola'),
            marker_kwds=dict(radius=5)
        )
    else:
        try:
            per = carregar_estados(uf)
        except Exception as e:
            st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
       
        # m = gerar_mapa(df=2)
        mapa = per.explore(
            tooltip=False,
            color='black',
            style_kwds=dict(fillOpacity=0.2),
            highlight=False
        )        
        m = gdf.explore(
            m=mapa,
            column='government_level',
            tooltip=cols,
            cmap='Spectral',
            name='Escolas de Recife',
            popup=['name_school', 'address', 'government_level', 'phone_number', 'name_muni'],
            legend_kwds=dict(caption='Tipo da escola'),
            marker_kwds=dict(radius=5)
        )

        # legend_style = """
        # <style>
        # .legend {
        #     color: black !important;
        # }
        # </style>
        # """
        # # Insere o CSS no mapa com MacroElement
        # legend_css = MacroElement()
        # legend_css._template = Template(legend_style)
        # m.get_root().add_child(legend_css)

        # legend_style = """
        # <style>
        # .leaflet-control .legend {
        #     background-color: black !important;
        #     color: white !important;
        #     padding: 10px;
        #     border-radius: 8px;
        #     box-shadow: 0 0 8px rgba(0,0,0,0.3);
        # }
        # </style>
        # """
        # # Adiciona ao mapa
        # legend_css = MacroElement()
        # legend_css._template = Template(legend_style)
        # m.get_root().add_child(legend_css)
   
elif tema_do_grafico == 'Municipios':
    try:
        gdf = carregar_municipios(uf)
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
    
    # m = gerar_mapa(
    #     column="name_muni",
    #     tooltip=cols,
    #     popup=True,
    #     style_kwds=dict(color="black", weight=0.5),
    #     legend=False, 
    #     add_layer_control=False
    # )
    m = gdf.explore(
        column="name_muni",
        tooltip=cols,
        popup=True,
        style_kwds=dict(color="black", weight=0.5),
        legend=False, 
        add_layer_control=False
    ) 

elif tema_do_grafico == 'Terras Indígenas':
    try:
        gdf = carregar_indis()
        if estado_selecionado_nome != 'Todos':
            gdf = gdf[gdf['abbrev_state'].str.contains(uf, na=False)]
        if municipio_selecionado_nome != 'Todos':
            gdf = gdf[gdf['name_muni'].str.contains(municipio_selecionado_nome, na=False)]
    except Exception as e:    
        st.error(f"Não foi possível carregar os dados para {uf}. Erro: {e}")
    
    # seleciona as colunas para exibir na tabela
    cols = ['terrai_nom', 'etnia_nome', 'superficie', 'modalidade', 'name_muni', 'abbrev_state']  # Colunas vazias, pois não há dados tabulares para exibir neste caso

    # m = gerar_mapa(
    #     column="terrai_nom",
    #     tooltip=cols,
    #     popup=True,
    #     style_kwds=dict(color="black", weight=0.5)
    # )
    m = gdf.explore(
        column="terrai_nom",
        tooltip=cols,
        popup=True,
        style_kwds=dict(color="black", weight=0.5)
    )    




def escala_formato(value):
        if value >= 1_000_000:
            return f'{value / 1_000_000:.2f} M'
        elif value >= 1000:
            return f'{value / 1000:.0f} K'
        else:
            return f'{value:.0f}'







if tema_do_grafico in ['Terras Indígenas', 'Escolas', 'Municipios']:
    # --- Criação e exibição do mapa ---
    if municipio_selecionado_nome == 'Todos':
        estado_ou_municipio = estado_selecionado_nome
    else:
        estado_ou_municipio = f"{municipio_selecionado_nome} - {uf}"
    st.subheader(f"Mapa de {tema_do_grafico} de {estado_ou_municipio}")

    if gdf is not None:
        
        # Renderiza o mapa no Streamlit
        
        st_folium(m, width='100%', height=600, use_container_width=True)
        
        # Opcional: Mostrar as tabelas e graficos
        if st.sidebar.checkbox("Mostrar tabela de dados"):
            st.subheader("Dados Tabulares")
            # if tema_do_grafico == 'Escolas':
            if cols != []:
                st.dataframe(gdf[cols])
            else:
                st.dataframe(gdf)

        
        if st.sidebar.checkbox(f"Mostrar distribuição de pessoas por religião"):
            st.subheader(f"Distribuição da População de {estado_selecionado_nome} selecionado por Religião")
            df_state = merged_df[merged_df['Unidade da Federação'] == state_name]

            # Agrupando por Religião pela soma
            religiao_group = df_state.groupby('Religião')['Valor'].sum().reset_index()

            # Criando coluna formatada com escala personalizada
            religiao_group['Valor_formatado'] = religiao_group['Valor'].apply(escala_formato)

            # Convertendo Valor para milhões para manter o eixo
            religiao_group['Valor_M'] = religiao_group['Valor'] / 1_000_000

            # Ordenando
            religiao_group.sort_values(by='Valor_M', ascending=False, inplace=True)

            # Plotando o gráfico
            fig1 = px.bar(
                religiao_group,
                x='Religião',
                y='Valor_M',
                title=f'Distribuição da População por Religião em {state_name}',
                text='Valor_formatado',
                color='Religião',
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            fig1.update_layout(
                xaxis_tickangle=-45,
                xaxis_title=None,
                yaxis_title=None,
                yaxis=dict(showticklabels=True, showgrid=True, zeroline=True, tickfont=dict(size=20, color='white')),
                plot_bgcolor='white',
                height=700,
                width=600
            )
            fig1.update_traces(
                textposition='outside',  # Define a posição do texto dentro das barras
                textfont=dict(
                    color='black',  # Define a cor da fonte do texto para preto
                    size=20         # Opcional: ajusta o tamanho da fonte para melhor leitura
                )
            )
            st.plotly_chart(fig1, use_container_width=True)

        

        if st.sidebar.checkbox(f"Mostrar distribuição de pessoas por Cor/Raça"):
            st.subheader(f"Distribuição da População de {estado_selecionado_nome} por Cor/Raça")
            
            df_state = merged_df[merged_df['Unidade da Federação'] == state_name]

            # Agrupando por Cor/Raça
            cor_group = df_state.groupby('Cor ou raça')['Valor'].sum().reset_index()

            # Criando coluna formatada
            cor_group['Valor_formatado'] = cor_group['Valor'].apply(escala_formato)

            # Convertendo Valor para milhões para manter o eixo fixo em M
            cor_group['Valor_M'] = cor_group['Valor'] / 1_000_000

            # Ordenando
            cor_group.sort_values(by='Valor_M', ascending=False, inplace=True)

            # Plotando o gráfico
            fig3 = px.bar(
                cor_group,
                x='Cor ou raça',
                y='Valor_M',
                title=f'Distribuição da População por Cor/Raça em {state_name}',
                text='Valor_formatado',
                color='Cor ou raça',
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            fig3.update_layout(
                xaxis_tickangle=-45,
                xaxis_title=None,
                yaxis_title=None,
                yaxis=dict(showticklabels=True, showgrid=True, zeroline=True, tickfont=dict(size=20, color='white')),
                plot_bgcolor='white',
                height=700,
                width=600
            )
            fig3.update_traces(
                textposition='outside',  # Define a posição do texto dentro das barras
                textfont=dict(
                    color='black',  # Define a cor da fonte do texto para preto
                    size=20         # Opcional: ajusta o tamanho da fonte para melhor leitura
                )
            )
            st.plotly_chart(fig3, use_container_width=True)

        if st.sidebar.checkbox(f"Mostrar distribuição de pessoas por sexo"):
            st.subheader(f"Distribuição da População de {estado_selecionado_nome} por sexo")
            df_state = merged_df[merged_df['Unidade da Federação'] == state_name]

            # Agrupando por Sexo pela soma do Valor
            sexo_group = df_state.groupby('Sexo')['Valor'].sum().reset_index()

            # Plotando a figura
            fig2 = px.pie(
                sexo_group,
                names='Sexo',
                values='Valor',
                title= f'% da População por Sexo em {state_name}',
                         color_discrete_sequence=px.colors.qualitative.Vivid,
            )

            # Elementos de design do gráfico
            fig2.update_traces(textinfo='percent+label', pull=[0.05, 0])
            fig2.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                height=400,
                width=600
            )
            st.plotly_chart(fig2, use_container_width=True)

        if st.sidebar.checkbox(f"Mostrar distribuição de Religião por Cor/Raça"):
            df_state = merged_df[merged_df['Unidade da Federação'] == state_name]

            # Agrupando por Religião pela soma
            religiao_group = df_state.groupby(['Religião', 'Cor ou raça'])['Valor'].sum().reset_index()

            fig5 = px.bar(
                religiao_group,
                x='Religião',
                y='Valor',
                color='Cor ou raça',
                title=f'Distribuição da população por Religião e Cor/Raça - {state_name}',
                color_discrete_sequence=px.colors.qualitative.Set3,
                text='Valor'
            )
            fig5.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                height=700,
                yaxis=dict(showticklabels=True, showgrid=True, zeroline=True, tickfont=dict(size=20, color='white')),
                plot_bgcolor='white',
                width=800
            )
            fig5.update_traces(
                texttemplate='%{text:.2s}', 
                textfont=dict(
                    color='black',  # Define a cor da fonte do texto para preto
                    size=20         # Opcional: ajusta o tamanho da fonte para melhor leitura
                ),
                textposition='outside')
            
            st.plotly_chart(fig5, use_container_width=True)

        if st.sidebar.checkbox(f"Mostrar distribuição de Sexo por Cor/Raça"):

            df_state = merged_df[merged_df['Unidade da Federação'] == state_name]

            df_sexo_cor = df_state.groupby(['Sexo', 'Cor ou raça'])['Valor'].sum().reset_index()

            fig4 = px.bar(
                        df_sexo_cor,
                        x='Sexo',
                        y='Valor',
                        color='Cor ou raça',
                        title=f'Distribuição da População por Cor/Raça e Sexo - {state_name}',
                        labels={'Valor': 'População'},
                        color_discrete_sequence=px.colors.qualitative.Vivid,
                        text='Valor')

            fig4.update_layout(barmode='stack', 
                                margin=dict(l=20, r=20, t=50, b=20),
                                height=700,
                                yaxis=dict(showticklabels=True, showgrid=True, zeroline=True, tickfont=dict(size=20, color='white')),
                                plot_bgcolor='white',
                                width=600)
            fig4.update_traces(
                texttemplate='%{text:.2s}', 
                textfont=dict(
                    color='black',  # Define a cor da fonte do texto para preto
                    size=20         # Opcional: ajusta o tamanho da fonte para melhor leitura
                ),
                textposition='outside')
            
            st.plotly_chart(fig4, use_container_width=True)

    else:
        st.warning("Não há dados para exibir. Por favor, selecione outro estado.")
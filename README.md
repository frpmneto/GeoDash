# GeoDash

Geodash é um dashboard interativo com diversos dados do IBGE, como dados de escolas e de reservas indígenas, e opções de filtros por Estado e Município. 

## Tecnologias utilizadas

O dashboard em si foi desenvolvido em python utilizando a biblioteca [Streamlit](https://streamlit.io/). Já os dados utilizados vieram das APIs do SIDRA, pelo [sidrapy](https://sidrapy.readthedocs.io/pt-br/latest/), e do [GeoBR](https://ipeagit.github.io/geobr/articles/python-intro/py-intro-to-geobr.html).

Também foram utilizadas outras bibliotecas como o plotly para auxiliar na criação de gráficos, e o [Geopandas](https://geopandas.org/en/stable/index.html) para gerar os mapas.

## Como executar o projeto

1. **Clone o repositório**
git clone https://github.com/frpmneto/GeoDash.git

2. **Instale as bibliotecas necessárias**
pip install -r requirements.txt

3. **Execute o dashboard**
streamlit run dashboard.py

Então uma janela se abrirá em seu navegador rodando o dashboard.

## Planos futuros

Os próximos passos para esse projeto são:
- comparar estatísticas entre diferentes estados
- comparar dados por ano
- fazer um heatmap dos estados baseando-se no filtro selecionado (cor = 'x', ou religiao = 'y')

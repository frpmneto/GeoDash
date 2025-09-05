# GeoDash

[Geodash](https://geodash.streamlit.app/) is an interactive dashboard featuring a wide range of data from IBGE (the Brazilian Institute of Geography and Statistics), such as information on schools and indigenous reserves, with options to filter by state and municipality.

## Tecnologias utilizadas

The dashboard itself was developed in Python using the [Streamlit](https://streamlit.io/) library. The data is sourced from the SIDRA APIs, via [Sidrapy](https://sidrapy.readthedocs.io/pt-br/latest/), and from [GeoBR](https://ipeagit.github.io/geobr/articles/python-intro/py-intro-to-geobr.html).

Other libraries were also utilized, such as Plotly for assistance in creating charts, and [Geopandas](https://geopandas.org/en/stable/index.html) for generating the maps.

## How to Run

1. **Clone the repository**
git clone https://github.com/frpmneto/GeoDash.git

2. **Install the requirements**
pip install -r requirements.txt

3. **Run the dashboard**
streamlit run dashboard.py

A new window will then open in your browser running the dashboard.

## Future Plans

The next steps for this project are:
- Compare statistics between different states
- Compare data by year
- Create a heatmap of the states based on the selected filter (e.g., race = 'x', or religion = 'y')

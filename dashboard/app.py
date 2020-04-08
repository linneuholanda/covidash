import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from epimodels.continuous.models import SEQIAHR
st.title('Cenarios de Controle da Covid-19')



WHOLE_BRASIL = "Brasil inteiro"
########################################## my changes #############################################
REGIONS = {"CO": ["DF", "GO", "MS", "MT"], "N": ["AC", "AM", "PA", "RO", "RR", "TO", "AP"], 
           "NE": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE",], "S": ["PR", "RS", "SC"],
           "SE": ["ES", "MG", "RJ", "SP"]}
###################################################################################################
PAGE_CASE_NUMBER = "Evolução do Número de Casos"

COLUMNS = {
    "A": "Asintomáticos",
    "S": "Suscetíveis",
    "E": "Expostos",
    "I": "Infectados",
    "H": "Hospitalizados",
    "R": "Recuperados",
    "C": "Hospitalizações Acumuladas",
}

DESCRPTION = {
    "chi": "Descrição chi",
    "phi": "Descrição phi",
    "beta": "Descrição beta",
    "rho": "Descrição rho",
    "delta": "Descrição delta",
    "alpha": "Descrição alpha",
    "p": "Descrição p",
    "q": "Descrição q",
}



def main():
    page = st.sidebar.selectbox("Escolha um Painel", ["Home",  "Modelos", "Dados", PAGE_CASE_NUMBER])
    if page == "Home":
        st.header("Dashboard COVID-19")
        st.write("Escolha um painel à esquerda")
    elif page == 'Modelos':
        st.title("Explore a dinâmica da COVID-19")
        st.sidebar.markdown("### Parâmetros do modelo")
        st.sidebar.markdown(f"<p>&chi;<span style='color:#b2b2b2;'> {DESCRPTION['chi']}</span></p>", unsafe_allow_html=True)
        chi = st.sidebar.slider('', 0.0, 1.0, 0.3)
        st.sidebar.markdown(f"<p>&phi;<span style='color:#b2b2b2;'> {DESCRPTION['phi']}</span></p>", unsafe_allow_html=True)
        phi = st.sidebar.slider('', 0.0, 0.5, 0.01)
        st.sidebar.markdown(f"<p>&beta;<span style='color:#b2b2b2;'> {DESCRPTION['beta']}</span></p>", unsafe_allow_html=True)
        beta = st.sidebar.slider('', 0.0, 1.0, 0.5)
        st.sidebar.markdown(f"<p>&rho;<span style='color:#b2b2b2;'> {DESCRPTION['rho']}</span></p>", unsafe_allow_html=True)
        rho = st.sidebar.slider('', 0.0, 1.0, 1.0)
        st.sidebar.markdown(f"<p>&delta;<span style='color:#b2b2b2;'> {DESCRPTION['delta']}</span></p>", unsafe_allow_html=True)
        delta  = st.sidebar.slider('', 0.0, 1.0, 0.01)
        st.sidebar.markdown(f"<p>&alpha;<span style='color:#b2b2b2;'> {DESCRPTION['alpha']}</span></p>", unsafe_allow_html=True)
        alpha  = st.sidebar.slider('', 0.0, 10.0, 2.0)

        st.markdown(f"<p>p<span style='color:#b2b2b2;'> {DESCRPTION['p']}</span></p>", unsafe_allow_html=True)
        p  = st.slider('', 0.0, 1.0, 0.75)
        st.markdown(f"<p>q<span style='color:#b2b2b2;'> {DESCRPTION['q']}</span></p>", unsafe_allow_html=True)
        q  = st.slider('', 0, 120, 30)
        params = {
            'chi': chi,
            'phi': phi,
            'beta': beta,
            'rho': rho,
            'delta': delta,
            'alpha': alpha,
            'p': p,
            'q': q
        }
        traces = pd.DataFrame(data=run_model(params=params)).rename(columns=COLUMNS)
        traces.set_index('time', inplace=True)

        st.line_chart(traces, height=400)

    elif page == "Dados":
        st.title('Probabilidade de Epidemia por Município')
        probmap = Image.open('dashboard/Outbreak_probability_full_mun_2020-04-06.png')
        st.image(probmap, caption='Probabilidade de Epidemia em 6 de abril',
        use_column_width=True)

    elif page == PAGE_CASE_NUMBER:
        st.title("Casos Confirmados no Brasil")
        data = get_data()
        ufs = sorted(list(data.state.drop_duplicates().values))
        uf_option = st.selectbox("Selecione o Estado", [WHOLE_BRASIL] + ufs)

        city_option = None
        if uf_option != WHOLE_BRASIL:
            cities = get_city_list(data, uf_option)
            city_option = st.selectbox("Selecione o Município", ["Todos"] + cities)
        
        data_uf = get_data_uf(data, uf_option, city_option)
#(data, uf, city_option)
        st.line_chart(data_uf, height=400)


@st.cache
def run_model(inits=[97.3e6, 0, 1, 0, 0, 0, 0], trange=[0, 365], N=97.3e6, params=None):
    model = SEQIAHR()
    model(inits=inits, trange=trange, totpop=N, params=params)
    return model.traces

@st.cache
def get_data():
    brasil_io_url = "https://brasil.io/dataset/covid19/caso?format=csv"
    cases = pd.read_csv(brasil_io_url).rename(
        columns={"confirmed": "Casos Confirmados"})

    return cases


@st.cache
def get_data_uf(data, uf=None, city_option=None):
    if uf:
        data = data.loc[(data.state==uf)&(data.place_type=="state"),:]
    if city_option:
        data = data.loc[(data.city==city_option)&(data.place_type=="city"),:]
    else:
        data = data.loc[data.place_type=="state",:]
    return data.groupby("date")["Casos Confirmados"].sum()

@st.cache
def get_data_region(data, region=None, uf=None, city_option=None):
    if region:
        if "region" not in data.columns:
            column_ix = cases.columns.get_loc("date")+1
        cases.insert(loc= column_ix,column="region",value=np.nan)
        for ix,s in enumerate(cases.state):
            cases.iloc[ix:,column_ix] = state_to_regions_dict[s]
        data = data.loc[(data.region == region)&(data.place_type=="state"),:]
    if uf:
        data = data.loc[(data.state==uf)&(data.place_type=="state"),:]
    if city_option:
        data = data.loc[(data.city==city)&(data.place_type=="city"),:]
    else:
        data = data.loc[data.place_type=="state",:] # get from the whole country
    return data.groupby("date")["Casos Confirmados"].sum()

@st.cache
def get_city_list(data, uf):
    return sorted(list(data.loc[(data.state==uf) & (~data.city.isnull())].city.drop_duplicates()))


@st.cache
def load_data():
    pass


if __name__ == "__main__":
    main()

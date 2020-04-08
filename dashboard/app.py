import altair as alt
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
#from epimodels.continuous.models import SEQIAHR
st.title('Cenarios de Controle da Covid-19')


WHOLE_BRASIL = "Brasil inteiro"

### Main menu goes here
HOME = "Home"
MODELS = "Modelos"
DATA = "Dados"
CASE_TIME_SERIES = "Evolução do Número de Casos"
CUM_CASE_COUNT = "Casos acumulados a partir de 100"

COLUMNS = {
    "A": "Assintomáticos",
    "S": "Suscetíveis",
    "E": "Expostos",
    "I": "Infectados",
    "H": "Hospitalizados",
    "R": "Recuperados",
    "C": "Hospitalizações Acumuladas",
}

VARIABLES = [
    'Expostos',
    'Infectados',
    'Assintomáticos',
    'Hospitalizados',
    'Hospitalizações Acumuladas'
]


logo = Image.open('dashboard/logo_peq.png')

def main():
    st.sidebar.image(logo, use_column_width=True)
    page = st.sidebar.selectbox("Escolha um Painel", [HOME,MODELS,DATA,CASE_TIME_SERIES, CUM_CASE_COUNT])
    if page == HOME:
        st.header("Dashboard COVID-19")
        st.write("Escolha um painel à esquerda")
    elif page == MODELS:
        st.title("Explore a dinâmica da COVID-19")
        st.sidebar.markdown("### Parâmetros do modelo")

        chi = st.sidebar.slider('χ, Fração de asintomáticos', 0.0, 1.0, 0.3)

        phi = st.sidebar.slider('φ, Taxa de Hospitalização', 0.0, 0.5, 0.01)

        beta = st.sidebar.slider('β, Taxa de transmissão', 0.0, 1.0, 0.5)

        rho = st.sidebar.slider('ρ, Atenuação da Transmissão em hospitalizados:', 0.0, 1.0, 1.0)

        delta  = st.sidebar.slider('δ, Taxa de recuperação:', 0.0, 1.0, 0.01)
        alpha  = st.sidebar.slider('α, Taxa de incubação', 0.0, 10.0, 2.0)


        p  = st.slider('Fração de assintomáticos:', 0.0, 1.0, 0.75)

        q  = st.slider('Dia de início da Quarentena:', 0, 120, 30)

        N = st.number_input('População em Risco:', value=97.3e6, max_value=200e6, step=1e6)
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
        traces = traces[['time'] + VARIABLES]
        #traces.set_index('time', inplace=True)
        traces[VARIABLES] *= N #Ajusta para a escala da População em risco
        melted_traces = pd.melt(
            traces,
            id_vars=['time'],
            var_name='Grupos',
            value_name="Número de Casos Estimados"
        )
        plot_model(melted_traces, q)

    elif page == DATA:
        st.title('Probabilidade de Epidemia por Município')
        probmap = Image.open('dashboard/Outbreak_probability_full_mun_2020-04-06.png')
        st.image(probmap, caption='Probabilidade de Epidemia em 6 de abril',
        use_column_width=True)

    elif page == CASE_TIME_SERIES:
        st.title("Casos Confirmados no Brasil")
        data = get_data()
        ufs = sorted(list(data.state.drop_duplicates().values))
        uf_option = st.multiselect("Selecione o Estado", ufs)

        city_options = None
        if uf_option:
            cities = get_city_list(data, uf_option)
            city_options = st.multiselect("Selecione os Municípios", cities)

        is_log = st.checkbox('Escala Logarítmica', value=False)
        #is_aligned = st.checkbox("Alinhar por primeiros 100 casos",value=False)
        data_uf = get_data_uf(data, uf_option, city_options)
        #data_uf = data_uf[data_uf>=100] if is_aligned else data_uf
        data_uf = np.log(data_uf + 1) if is_log else data_uf
        st.line_chart(data_uf, height=400)
        
    elif page==CUM_CASE_COUNT:
        st.title("Casos acumulados a partir do centésimo")
        data = get_data()
        ufs = sorted(list(data.state.drop_duplicates().values))
        uf_option = st.multiselect("Selecione o Estado", ufs)

        city_options = None
        if uf_option:
            cities = get_city_list(data, uf_option)
            city_options = st.multiselect("Selecione os Municípios", cities)
        is_log = st.checkbox('Escala Logarítmica', value=False)
        #is_aligned = st.checkbox("Alinhar por primeiros 100 casos",value=False)
        data_uf = get_data_uf(data, uf_option, city_options)
        #print(data_uf)
        data_uf = get_aligned_data(data_uf,align=100)
        #data_uf = data_uf[data_uf>=100] if is_aligned else data_uf
        data_uf = np.log(data_uf + 1) if is_log else data_uf
        st.line_chart(data_uf, height=400)
     #elif page


def plot_model(melted_traces, q):
    lc = alt.Chart(melted_traces, width=800, height=400).mark_line().encode(
        x="time",
        y='Número de Casos Estimados',
        color='Grupos',
    ).encode(
        x=alt.X('time', axis=alt.Axis(title='Dias'))
    )
    vertline = alt.Chart().mark_rule(strokeWidth=2).encode(
        x='a:Q',
    )
    la = alt.layer(
        lc, vertline,
        data=melted_traces
    ).transform_calculate(
        a="%d" % q
    )
    st.altair_chart(la)
    
def plot_aligned(df,align=100,log=False):
    pass
    #fig,ax = subplots(1,1,figsize=(15,8))
    #alinhados = 
    #alinhados = pd.concat([suecia[suecia>100].reset_index(),alemanha[alemanha>100].reset_index(),
    #       espanha[espanha>100].reset_index(),
    #       italia[italia>100].reset_index()], 
    #      axis=1)
    #alinhados['EUA'] = serie_US[serie_US.US>100].reset_index().US
    #alinhados['Brasil'] = df_brasil[df_brasil.casosAcumulados>100].reset_index().casosAcumulados
    #alinhados.plot(ax=ax,logy=True, grid=True);
    #plt.savefig('export/Brasil_vs_outros.png', dpi=300)
    #alinhados.to_csv('export/Brasil_vs_outros.csv')


@st.cache(suppress_st_warning=True)
def run_model(inits=[.99, 0, 1e-6, 0, 0, 0, 0], trange=[0, 365], N=97.3e6, params=None):
    # st.write("Cache miss: model ran")
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
def get_data_uf(data, uf, city_options):
    if uf:
        data = data.loc[data.state.isin(uf)]
        if city_options:
            city_options = [c.split(" - ")[1] for c in city_options]
            data = data.loc[
                (data.city.isin(city_options)) & (data.place_type == "city")
            ][["date", "state", "city", "Casos Confirmados"]]
            pivot_data = data.pivot_table(values="Casos Confirmados", index="date", columns="city")
            data = pd.DataFrame(pivot_data.to_records())
        else:
            data = data.loc[data.place_type == "state"][["date", "state", "Casos Confirmados"]]
            pivot_data = data.pivot_table(values="Casos Confirmados", index="date", columns="state")
            data = pd.DataFrame(pivot_data.to_records())

    else:
        return data.loc[data.place_type == "city"].groupby("date")["Casos Confirmados"].sum().to_frame()

    return data.set_index("date")

def get_aligned_data(df,align=100):
    align_dfs = [df.loc[df[c]>=100,[c]].values.reshape(-1,) for c in df.columns] 
    columns = [c for c in df.columns] 
    aligned_df = pd.DataFrame(align_dfs,index=columns).T                           
    #align_dfs = [d.reset_index() for d in align_dfs]
    #aligned = pd.concat([d for d in align_dfs],ignore_index=True)
    return aligned_df
    #def plot_aligned(df,align=100,log=False):
    #pass
    #fig,ax = subplots(1,1,figsize=(15,8))
    #alinhados = 
    #alinhados = pd.concat([suecia[suecia>100].reset_index(),alemanha[alemanha>100].reset_index(),
    #       espanha[espanha>100].reset_index(),
    #       italia[italia>100].reset_index()], 
    #      axis=1)
    #alinhados['EUA'] = serie_US[serie_US.US>100].reset_index().US
    #alinhados['Brasil'] = df_brasil[df_brasil.casosAcumulados>100].reset_index().casosAcumulados
    #alinhados.plot(ax=ax,logy=True, grid=True);
    #plt.savefig('export/Brasil_vs_outros.png', dpi=300)
    #alinhados.to_csv('export/Brasil_vs_outros.csv')

@st.cache
def get_city_list(data, uf):
    data_filt = data.loc[(data.state.isin(uf)) & (data.place_type == "city")]
    data_filt["state_city"] = data_filt["state"] + " - " + data_filt["city"]
    return sorted(list(data_filt.state_city.drop_duplicates().values))


@st.cache
def load_data():
    pass


if __name__ == "__main__":
    main()

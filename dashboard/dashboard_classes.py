import altair as alt
import numpy as np
import pandas as pd
#import streamlit as st
import pydeck as pdk
from PIL import Image
from epimodels.continuous.models import SEQIAHR
import humanizer_portugues as hp

import dashboard_models
import dashboard_data
from dashboard_models import seqiahr_model

#@st.title('A Matemática da Covid-19')

### Main menu goes here
#HOME = "Home"
#MODELS = "Modelos"
#DATA = "Probabilidade de Espalhamento"
#MAPA = "Distribuição Geográfica"
#CREDITOS = "Equipe"
#PAGE_CASE_DEATH_NUMBER_BR = "Casos e Mortes no Brasil"
#CUM_DEATH_COUNT_BR = "Mortes acumuladas no Brasil"
#CUM_DEATH_CART = "Mortes registradas em cartório"
#PAGE_GLOBAL_CASES = "Casos no Mundo"

#COLUMNS = {
#    "A": "Assintomáticos",
#    "S": "Suscetíveis",
#    "E": "Expostos",
#    "I": "Infectados",
#    "H": "Hospitalizados",
#    "R": "Recuperados",
#    "C": "Hospitalizações Acumuladas",
#    "D": "Mortes Acumuladas",
#}

#VARIABLES = [
#    'Expostos',
#    'Infectados',
#    'Assintomáticos',
#    'Hospitalizados',
#    'Hospitalizações Acumuladas',
#    "Mortes Acumuladas"
#]

class timeseries_visualization:
    """ 
    This class encapsulates visualizations of number of cases, number of deaths and similar visualizations.
    """
    def __init__(self, datasets_dict):
        """
        inputs
        ------
        dataset_dict: a dictionary specifying the data sets to be used {dataset_name: {source: source, index_col: index_col, usecols: usecols,  parse_dates: parse_dates,      renamecols: renamecols}
        """
        self.datasets_dict = datasets_dict
        self.figure = None
        concat_dfs = []
        for ds_name, ds_dict in self.datasets_dict.items():
            source, index_col, usecols, parse_dates, renamecols = ds_dict.values()
            df = pd.read_csv(source,index_col=index_col,usecols=usecols,parse_dates=parse_dates)
            if renamecols is not None:
                if renamecols == "dataset_name":
                    renamecols = {c: ds_name+"_"+c for c in df.columns}
                df.rename(columns=renamecols)
            concat_dfs.append(df)
        self.dataframe = pd.concat(concat_dfs,axis=1)
    def plot_series():
        pass
        
                     
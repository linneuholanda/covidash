import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
from PIL import Image
from epimodels.continuous.models import SEQIAHR
import humanizer_portugues as hp
import settings
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

class dataset:
    """
    This class condenses information available for a particular data set
    """
    def __init__(self,name, source, read_csv_kw={}):
        self.name = name
        self.source = source
        read_csv_kw["filepath_or_buffer"] = source
        self.dataframe = pd.read_csv(**read_csv_kw)
        self.timeseries_visualizations = {}
        
    def add_timeseries_visualization(self,vis_name,yvar,xvar,filters=None):
        """
        Defines dictionaries for visualization
        """
        self.timeseries_visualizations[vis_name] = {}
        self.timeseries_visualizations[vis_name]["yvar"] = yvar
        self.timeseries_visualizations[vis_name]["xvar"] = xvar
        self.timeseries_visualizations[vis_name]["filters"] = filters
    
    def get_timeseries_visualizations(self):
        return self.timeseries_visualizations
        
class menu_tag:
    """ 
    This class encapsulates visualizations of number of cases, number of deaths and similar visualizations.
    """
    def __init__(self, datasets):
        """
        inputs
        ------
        dataset_dict: a dictionary specifying the data sets to be used {dataset_name: {source: , index_col: , usecols: ,  parse_dates: ,      renamecols: , visualization_cols: }}
        """
        self.datasets = datasets
        #self.datasets = list(datasets_dict.keys())
        #self.figure = None
        #self.dataframes = {}
        #for ds_name, ds_dict in self.datasets_dict.items():
        #    source, index_col, usecols, parse_dates, renamecols, visualization_cols = ds_dict.values()
        #    df = pd.read_csv(source,index_col=index_col,usecols=usecols,parse_dates=parse_dates)
        #    if renamecols is not None:
        #        if renamecols == "dataset_name":
        #            renamecols = {c: ds_name+"_"+c for c in df.columns}
        #        df.rename(columns=renamecols)
        #    self.dataframes[ds_name] = df
        #self.visualizations = None
    
    def get_list_of_datasets(self):
        return list(self.datasets.keys())
    
    def add_dataset_visualization(self,dataset_name,visualization_name,y_variable,x_variable,filters=None):
        ds = self.datasets[dataset_name]
        ds.add_visualization(visualization_name,y_variable,x_variable,filters)
        
    @st.cache(ttl=settings.CACHE_TTL)
    def get_visualization_menu(self,dataset_names):
        visualization_menu = []
        for ds_name in dataset_names:
            ds = self.datasets[ds_name]
            for vis_name in ds.get_timeseries_visualizations():
                visualization_menu.append(ds_name + " - " + vis_name) 
        #self.visualization_options = visualization_options 
        return visualization_menu

    
    @st.cache(ttl=settings.CACHE_TTL)
    def __get_visualization_menu(self):
        visualization_menu = []
        for ds_name, ds in self.datasets.items():
            for vis_name in ds.get_visualizations():
                visualization_menu.append(ds_name + " - " + vis_name) 
        #self.visualization_options = visualization_options 
        return visualization_menu
    
    def get_menu_for_variable(self,visualization_menu,variable):
        #df_name = 
        pass
        
    def plot_series():
        pass
        
                     
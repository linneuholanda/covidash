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
import plotly.express as px

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
    
    @st.cache(ttl=settings.CACHE_TTL)
    def get_unique_elements_from_column(self,column):
        unique_elements = self.dataframe.loc[:,column].drop_duplicates(keep="first")
        return unique_elements
    
    def plot_timeseries(self,vis_name,px_scatter_kw={}):
        data = self.dataframe.copy()
        #if is_log:
        #    #data = data.copy()
        #    log_y_variable = f"Log[{y_variable}]"
        #    data[log_y_variable] = np.log(data[y_variable] + 1)
        #    y_variable = log_y_variable
        px_scatter_kw["data_frame"] = data
        px_scatter_kw["x"], px_scatter_kw["y"] = self.timeseries_visualizations[vis_name]["xvar"],                                                                                self.timeseries_visualizations[vis_name]["yvar"]
        fig = px.scatter(**px_scatter_kw)#, color=region_name)    
        fig.update_traces(mode='lines+markers')
        fig.update_layout(xaxis_title="Data", yaxis_title="Indivíduos",plot_bgcolor='rgba(0,0,0,0)', legend_orientation="h")
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',showline=True, linewidth=1, linecolor='black')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',showline=True, linewidth=1, linecolor='black')
    
        return fig
    
    
#def plot_series(data, x_variable, y_variable, region_name, is_log):
#    if is_log:
#        data = data.copy()
#        log_y_variable = f"Log[{y_variable}]"
#        data[log_y_variable] = np.log(data[y_variable] + 1)
#        y_variable = log_y_variable
#
#    fig = px.scatter(data, x=x_variable, y=y_variable, color=region_name)    
#    
#    fig.update_traces(mode='lines+markers')
#    fig.update_layout(
#        xaxis_title="Data",
#        yaxis_title="Indivíduos",
#        plot_bgcolor='rgba(0,0,0,0)',
#        legend_orientation="h",        
#    )
#    fig.update_xaxes(
#        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
#        showline=True, linewidth=1, linecolor='black',
#    )
#    fig.update_yaxes(
#        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
#        showline=True, linewidth=1, linecolor='black',
#    )
#    
#    return fig
#        
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
        self.chosen_datasets = None
        self.chosen_timeseries_visualizations = {}
    
    @st.cache(ttl=settings.CACHE_TTL)
    def choose_dataset(self,chosen_datasets):
        self.chosen_datasets = chosen_datasets
    def get_list_of_datasets(self):
        return list(self.datasets.keys())
    
    def add_dataset_visualization(self,dataset_name,visualization_name,y_variable,x_variable,filters=None):
        ds = self.datasets[dataset_name]
        ds.add_visualization(visualization_name,y_variable,x_variable,filters)
        
    @st.cache(ttl=settings.CACHE_TTL)
    def get_timeseries_visualization_menu(self,dataset_names):
        visualization_menu = []
        for ds_name in dataset_names:
            ds = self.datasets[ds_name]
            for vis_name in ds.get_timeseries_visualizations():
                visualization_menu.append(ds_name + " - " + vis_name) 
        #self.visualization_options = visualization_options 
        return visualization_menu
    
    @st.cache(ttl=settings.CACHE_TTL)
    def get_menu_from_column(self,dataset_name, column):
        ds = self.datasets[dataset_name]
        menu_from_column = ds.get_unique_elements_from_column(column).values
        #print("type: ", type(menu_from_column))
        #menu_from_column = ["a", "b", "c"]
        return menu_from_column
    
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
        
                     

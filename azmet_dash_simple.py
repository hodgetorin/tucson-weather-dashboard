# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 09:28:47 2022

@author: Torin
"""
import sys, os
#from datetime import date, timedelta, datetime

import time

import pandas as pd
import numpy as np


import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc




### DASH APP ### 
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# User Defined:
Location = "Tucson"


# data frame processing
def load_df(Location):
     df = pd.read_csv("df_historic_"+Location+".csv") # to simplify changing locations' DF..?
     return df
 
def preprocess(df):
     
     df['Rainfall - in'] = df['Rainfall'] / 2.54         
     df['Air Temp - Mean - F'] = (df['Air Temp - Mean']*(9/5) + 32)
     df['Tmax - F'] = df['Tmax']*(9/5) + 32
     df['Tmin - F'] = df['Tmin']*(9/5) + 32
     
     # extra columns for aggregating at different time intervals:
     df['Mo_Day'] = df['Date'].str[5:10] # this will be used to isolate our historic dataframe of the past 7 days
     
     #df['temp_date'] = pd.to_datetime(df['Date']) #convert from str to py dt format
     #df['Date'] = df['temp_date'].dt.date
     
     df.set_index('Date')
     
     #df['Year'] = df['Date'].dt.year #replace old Year col w/ dt format year.
     #df['Month'] = df['Date'].dt.month
     
     # round up the temp and rainfall columns to 2 decimals
     df['Tmax - F'] = round(df['Tmax - F'],2)
     df['Tmin - F'] = round(df['Tmin - F'],2)
     df['Rainfall - in'] = round(df['Rainfall - in'], 2)

     return df  

      
### how to send logic to/from dcc objects?
## i.e. when YTD graph is selected from above viz_dropdown, how do we have it fix the datepicker max and mins, or make it only accept 

datepicker = dcc.DatePickerRange(
        id='dt_pk_rng',  # ID to be used for callback
        calendar_orientation='horizontal',  # vertical or horizontal
        day_size=39,  # size of calendar image. Default is 39
        end_date_placeholder_text="End Date",  # text that appears when no end date chosen
        with_portal=False,  # if True calendar will open in a full screen overlay portal
        first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
        reopen_calendar_on_clear=True,
        is_RTL=False,  # True or False for direction of calendar
        clearable=True,  # whether or not the user can clear the dropdown
        number_of_months_shown=1,  # number of months shown when calendar is open
        #min_date_allowed=dt(2018, 1, 1),  # minimum date allowed on the DatePickerRange component
        #max_date_allowed=dt(2020, 6, 20),  # maximum date allowed on the DatePickerRange component
        initial_visible_month=dt.date(2021, 1, 1),  # the month initially presented when the user opens the calendar
        display_format='MMM Do',  # how selected dates are displayed in the DatePickerRange component.
        month_format='MMMM',  # how calendar headers are displayed when the calendar is opened.
        minimum_nights=2,  # minimum number of days between start and end date
    
        persistence=True,
        persisted_props=['start_date'],
        persistence_type='session',  # session, local, or memory. Default is 'local'
    
        updatemode='bothdates'  # singledate or bothdates. Determines when callback is triggered
),
     
         
metric_dropdown = dcc.Dropdown(id='metric',
            options=[
                    {'label':'Max Air Temps', 'value':'Tmax - F'}, 
                    {'label':'Min Air Temps','value':'Tmin - F'},
                    {'label':'Mean Relative Humidity','value':'RH - Mean'},
                    {'label':'Mean Vapor Pressure Deficit','value':'VPD - Mean'},
                    {'label':'Total Solar Radiation','value':'SR-Total'},
                    {'label':'Rainfall','value':'Rainfall - in'},
                    {'label':'Wind Speed','value':'Wind Speed'},
                    {'label':'Heat Units','value':'Heat units'},
    
            ],
            value='Tmax - F',
            clearable=False, 
            multi=False
                    )
      


app.layout = dbc.Container([
    html.Br(),       
    html.H4("Historic Tucson Weather Dashboard"),
    html.Br(),
    dbc.Row([
        dbc.Col([metric_dropdown],
                width={'size':6}),
        ]),
    
    dbc.Row([
        dbc.Col(datepicker),
        html.Br()
        ]),
    
    dbc.Row([
       dbc.Col([dcc.Graph(id="graph1")
                ], width={'size':6}),
       
       dbc.Col([
           dcc.Graph(id="graph2")
           ], width=6)
                 
        ])   
])

@app.callback(
    
    Output(component_id="graph1", component_property="figure"),
    Output(component_id="graph2", component_property="figure"),
    
    Input('dt_pk_rng', 'start_date'),
    Input('dt_pk_rng', 'end_date'),
    Input('metric', component_property='value')

)
   
def main_graph(start_dt, end_dt, metric_chosen):
    
    # from dash RE: start and end data types: strings are preferred bc thats the form dates take as callback args.
    
    df = load_df(Location)
    df = preprocess(df) 
    
    start_dt = dt.datetime.strptime(start_dt,'%Y-%m-%d')
    end_dt = dt.datetime.strptime(end_dt, '%Y-%m-%d')

    # convert back to strings:
    start_dt = str(start_dt)
    end_dt = str(end_dt)
  
    
    #if viz_chosen == 'viz_ytd_mm':
        
     #   dff = df[(df['Date'] >= start_dt) & (df['Date'] <= end_dt)] 
      #  dff['Mo_Day'] = dff['Mo_Day'].replace('-','/', regex=True) # change formatting to allow better readability from plotly dash 
        
       # fig1 = px.scatter(dff, x='Mo_Day', y=metric_chosen)
        #fig2 = px.histogram(dff, x=metric_chosen, orientation='v')
        
        #fig1.layout.template = 'plotly_dark'
        
      
   
        
    start_dt = start_dt[5:10]
    end_dt = end_dt[5:10]

    dff = df[(df['Mo_Day'] >= start_dt) & (df['Mo_Day'] <= end_dt)] 
    dff['Mo_Day'] = dff['Mo_Day'].replace('-','/', regex=True) # change formatting to allow better readability from plotly dash 
    
        # calculate median and average for the histogram:
    md = dff[metric_chosen].median
    avg = dff[metric_chosen].mean        
     
    fig1 = px.box(dff, x='Mo_Day', y=metric_chosen) 
    fig1.update_xaxes(type='category')  
        #fig1.update_layout(margin=dff['Mo_Day'])
        
    fig2 = px.histogram(dff, x=metric_chosen, orientation='v')
    
        
          # xaxis_rangeslider_visible=False,
    
    return fig1, fig2
      

if __name__ == "__main__":
    app.run_server(debug=False, port=8056)

















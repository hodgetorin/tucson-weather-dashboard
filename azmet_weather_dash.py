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



# CSS Stylesheet
external_css = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

### DASH APP ### 
app = Dash(__name__, external_stylesheets=external_css)

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

viz_dropdown = dcc.Dropdown(id='viz',
            options=[
                    {'label':'Year-to-Date Multiple Metrics', 'value':'viz_ytd_mm'}, 
                    {'label':'Multiyear Box Plot','value':'viz_yearly_box'} 
                    ],
            value='viz_ytd_mm',
            clearable=False, 
                    )
      
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
        initial_visible_month=dt.date(2020, 5, 1),  # the month initially presented when the user opens the calendar
        display_format='MMM Do, YYYY',  # how selected dates are displayed in the DatePickerRange component.
        month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
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
            ],
            value='Tmax - F',
            clearable=False, 
            multi=True
                    )
      

app.layout = dbc.Container([
    html.Br(),       
    html.H4("Historic Tucson Weather Dashboard"),
    html.Br(),
    dbc.Row([
        dbc.Col(viz_dropdown),
        html.Br(),
        dbc.Col(datepicker),
        html.Br(),
        dbc.Col(metric_dropdown),
        html.Br()
        ]),
    
    dbc.Row([
       dbc.Col(dcc.Graph(id="graph"))
        ])    
])



@app.callback(
    
    Output(component_id="graph", component_property="figure"),
    
    Input('viz', component_property='value'),
    Input('dt_pk_rng', 'start_date'),
    Input('dt_pk_rng', 'end_date'),
    Input('metric', component_property='value')

)
   
def main_graph(viz_chosen, start_dt, end_dt, metric_chosen):
    
    # from dash RE: start and end data types: 'srings are preferred bc thats the form dates take as callback args.
    
    df = load_df(Location)
    df = preprocess(df) 
    
    start_dt = dt.datetime.strptime(start_dt,'%Y-%m-%d')
    end_dt = dt.datetime.strptime(end_dt, '%Y-%m-%d')

    # convert back to strings:
    start_dt = str(start_dt)
    end_dt = str(end_dt)
  
    
    if viz_chosen == 'viz_ytd_mm':
        
        dff = df[(df['Date'] >= start_dt) & (df['Date'] <= end_dt)] 
        dff['Mo_Day'] = dff['Mo_Day'].replace('-','/', regex=True) # change formatting to allow better readability from plotly dash 
        
        fig = px.scatter(dff, x='Mo_Day', y=metric_chosen)
        
      
    elif viz_chosen == 'viz_yearly_box': # user picks DATES, not knowing or picking the year. graph uses all years available.
        
        start_dt = start_dt[5:10]
        end_dt = end_dt[5:10]

        dff = df[(df['Mo_Day'] >= start_dt) & (df['Mo_Day'] <= end_dt)] 
        dff['Mo_Day'] = dff['Mo_Day'].replace('-','/', regex=True) # change formatting to allow better readability from plotly dash 
    
        fig = px.box(dff, x='Mo_Day', y=metric_chosen) 
        
    fig.layout.template = 'plotly_dark'
        #fig.update_xaxes(type='category')    
        #fig.update_layout(margin=dff['Mo_Day'])  # xaxis_rangeslider_visible=False,
    
    return fig
      

if __name__ == "__main__":
    app.run_server(debug=True, port=8056)

















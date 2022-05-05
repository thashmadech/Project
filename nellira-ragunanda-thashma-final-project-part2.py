#!/usr/bin/env python
# coding: utf-8

# I am using the dash library of python to create a dashboard.Written on top of Plotly.js and React.js, Dash is ideal for building and deploying data apps with customized user interfaces. It's particularly suited for anyone who works with data.
# 
# I also used pandas to create dataframes using the csv files and to filter out the necessary information for the plots.

# #####  References:
# https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Deploy_App_to_Web/Kaggle-GGL-Collab/Dash-on-GGL-Colab.ipynb
# 
# https://www.justintodata.com/python-interactive-dashboard-with-plotly-dash-tutorial/
# 
# https://dash.plotly.com/dash-core-components

# I am using 2 different csv datasets formy visualizations.
# 
# 1. Gapminder : Gapminder identifies systematic misconceptions about important global trends and proportions and uses reliable data to develop easy to understand teaching materials to rid people of their misconceptions. I have downloaded the file and used 3 different indicators for my visualization
# 
# 2. Countries and codes: A file downloaded from https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes which countains the Alpha-3 and Alpha-2 codes for countries
# 

# In[1]:


# essential imports
from jupyter_dash import JupyterDash 

import dash
from dash import html
from dash import dcc
from dash.dependencies import Output, Input

import plotly.express as px
import math
from dash import no_update

import pandas as pd
import numpy as np
import json


# In[2]:


# read the GDP data
df_country = pd.read_csv("https://github.com/thashmadech/IS445/blob/main/project/gapminder.csv?raw=true")


# In[3]:


df_country.head()


# In[4]:


# we load a secondary dataset with all countries and their 3-letter alpha code 
df_country_code = pd.read_csv("https://github.com/thashmadech/IS445/blob/main/project/countries_codes_and_coordinates.csv?raw=true")
df_country_code['Alpha-3 code'] = df_country_code['Alpha-3 code'].apply(lambda s : s.replace('"', ""))


# In[5]:


df_country_code.head()


# In[6]:


#available economic indicators in the gapminder.csv file

indicators = ['lifeExp','pop','gdpPercap']


# I am using the below helper function to display a single row from the Countries and codes dataframe as well as display the name of the country whose data has been hovered and clicked on the scatter plot.

# In[7]:


# a helper function
def get_country_name(country_code):    
  one_row = df_country_code[df_country_code['Alpha-3 code'].str.strip() == country_code]
  if not one_row.empty:
    display(one_row)
    return one_row['Country'].values[0]
  else:
    return ''
# end


# The below css is available at codepen.io which can be used to create rows and columns. I am using them to create a layout for my dashboard

# In[8]:


# this external css creates columns and row layout
style_css = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# ####  Dashboard Design:
# 
# In Dash, multiple html elements are added inside an html div tag as a list. The list construct takes classnames to evenly space the columns. For example we can use classname = "three columns" of we want to span the space into 3 columns.
# 
# Below, I am creating a dashboard template with rows and columns that I need. I have created 3 rows.
# 
# 1st row: The Header
# 
# 2nd row: Two drop downs and 2 radio boxes
# 
# 3rd row: A scatter plot, a slider and a bar plot
# 

# In[9]:


app = JupyterDash(__name__, external_stylesheets=style_css)

app.layout = html.Div([
    # first row: header
    html.H4('An interactive Dashboard of GDP Vs Population Vs life Expectancy '),

    # second row: two drop-downs and radio-boxes. 
    html.Div([
      html.Div([
        dcc.Dropdown(
          id='xaxis-column',
          options=[{'label': i, 'value': i} for i in indicators], #e.g., {label: 'pop', 'value':'pop'}
          value='lifeExp'
        ),
        dcc.RadioItems(
          id='xaxis-type',
          options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
          value='Linear',
          labelStyle={'display': 'inline-block'}
        )
      ], className='four columns'),

      html.Div([
        dcc.Dropdown(
          id='yaxis-column',
          options=[{'label': i, 'value': i} for i in indicators],
          value='gdpPercap'
        ),
        dcc.RadioItems(
          id='yaxis-type',
          options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
          value='Linear',
          labelStyle={'display': 'inline-block'}
        )
      ], className='four columns')

    ], className='row'),


    # third row:
    html.Div([

      # first item: scatter plot
      html.Div([

        # add scatter plot
        dcc.Graph(
          id='scatter-plot',
          figure=px.scatter() 
        ),

        # add slider
        dcc.Slider(
          id='year-slider',
          min=df_country['year'].min(),
          max=df_country['year'].max(),
          value=df_country['year'].min(),
          marks={str(year): str(year) for year in df_country['year'].unique()},
          step=None
        )

      ], className='seven columns'),

      

      # second item: bar chart
      html.Div([
        dcc.Graph(
          id='bar-chart',
          figure=px.bar()
        )
      ], className='five columns')

    ], className = 'row'),

    

    # fourth row
    html.Div([
        html.Div([
#           html.H3('Debug'),
          #html.Br(),
          html.P(id='output_text_1', children='Total:'),
          html.P(id='output_text_2', children='Details:')
#           html.P(id='output_text_3', children='Details2:'),
#           html.P(id='output_text_4', children='Details3:')
        ], className = 'five columns')

    ], className = 'row')

])




# #### Callbacks
# 
# I am creating 2 call backs for the 2 plots on my dashboard.
# 
# Each callback  has 2 components, a callback definition(@app.callback and a callback function after tge callback definition.)
# 
# The input and the output of the callback function must match the definition of @app.callback
# 
# The output is followed by one or more inputs.

# In[10]:


# callback definition for the scatter plot
@app.callback(
  Output('scatter-plot', 'figure'),
  Output('output_text_1', 'children'), #debug
  Input('year-slider', 'value'),
  Input('xaxis-column', 'value'),
  Input('yaxis-column', 'value'),
  Input('xaxis-type', 'value'),
  Input('yaxis-type', 'value'),
)



# first callback function
def update_graph(selected_year, xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type):
  # print all input params to keep track of the clicks and coordinates
  debug_params =''
    #'Input: {0}, {1}, {2}, {3}, {4}'.format(selected_year, xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type)

  # filter data frame by year
  filtered_df = df_country[df_country.year == selected_year]

  fig_scatter_plot = px.scatter(
    data_frame = filtered_df,
    x=str(xaxis_column_name),
    y=str(yaxis_column_name),
    hover_name="country",
    color="continent",
    size_max=55,
    
    custom_data = ["iso_alpha"],
    title= "{0}  vs {1} of Countries".format(xaxis_column_name, yaxis_column_name)
  )

  fig_scatter_plot.update_layout(transition_duration=500)

  fig_scatter_plot.update_xaxes(
    title=xaxis_column_name,
    type='linear' if xaxis_type == 'Linear' else 'log'
  )

  fig_scatter_plot.update_yaxes(
    title=yaxis_column_name,
    type='linear' if yaxis_type == 'Linear' else 'log'
  )

  # return
  return fig_scatter_plot, debug_params
# end update_








# second callback for the bar plot
@app.callback(
  Output('bar-chart', 'figure'),
  Output('output_text_2', 'children'), #debug
  Input('scatter-plot', 'clickData'), 
  Input('xaxis-column', 'value'),
  Input('xaxis-type', 'value')
)
# second callback definition
def update_bar_graph(clickData, xaxis_column_name, axis_type):
  if not clickData:
    return no_update

  debug_params = '' #using the debug params to keep track of the click data points
    #'Input: {0}, {1}, {2}'.format(clickData['points'], xaxis_column_name, axis_type)

  #print(str(clickData['points'][0]['customdata'][0]))
  country_code = str(clickData['points'][0]['customdata'][0])

  filtered_df = df_country[df_country['iso_alpha'] == country_code]

  fig_bar_plot = px.bar(
    data_frame = filtered_df,
    x="year",
    y=str(xaxis_column_name),
    title= "{0} of {1} ".format(xaxis_column_name, get_country_name(country_code))
  )

  fig_bar_plot.update_yaxes(
    title=xaxis_column_name,
    type='linear' if axis_type == 'Linear' else 'log'
  )

  # return
  return fig_bar_plot, debug_params
# end


# #### Clicking on any point of the scatterplot loads the barplot on the right side. The slider at the bottom of the scatter plot shows the indicator value for the specified year. 
# 
# ####  Clicking on the legends(continent) will highlight the scatterplot of only the remaining continents
# 
# #### clicking on the slider will show the variations of the indicators by year
# 
# Running the dash app on port 8030(my local machine)

# In[11]:


app.run_server(mode='inline', port=8030)


# #### Group Submission Guidelines: I am doing this project individually
# 
# I have included an additional slider to make sense of the plot across different years.

# From this assignment I learned a new python plotly library called dash which can be used to build apps with dashboards that can be run on browsers and IDE's.
# While building the dashboard I encountered a lot of challenges and obstacles as this is my first time using this library. Watching tutorial videos and going through sample sources available online helped me overcome these challenges as well as learn new ways of creating visualizations.  

# For part 3 I plan on adding a map component and a line chart for my dashboard which will show the countries making it eaier to identify the growth of the Gapminder indicators.

# In[12]:


get_ipython().system(' jupyter nbconvert --to html nellira-ragunanda-thashma-final-project-part2.ipynb')


# In[ ]:





# In[ ]:





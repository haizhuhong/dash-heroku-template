import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


### Data preparation 
#%%capture
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = """
In United States, the average wage of women is known to be less than that of men. As stated in [Wikipedia](https://en.wikipedia.org/wiki/Gender_pay_gap#:~:text=The%20gender%20pay%20gap%20or,and%20women%20who%20are%20working.&text=In%20the%20United%20States%2C%20for,for%20the%20adjusted%20average%20salary.), the unadjusted female's average annual salary is only 79% of male's average annual salary. Even after adjusting differences in the occupational prestige, hours worked, education, and job experiences, the average annual salary of female's is still 5% less than male's.

In our dashboard, we are going to present several findings from the [GSS](http://www.gss.norc.org/About-The-GSS) of year 2018. The GSS is the abbreviation for the General Social Survey, which was first started in 1972, aimed to trace the social changes in Contemporary American Society. The GSS is conducted through personal interviews, where interviewees answer questions about their demographics, behaviors, attitudes and other topics of special interests. The responses of interviewees are recorded and made available as the one of the best data sources for studying social structure and trends of American Society.
"""

### Generate table
table = gss_clean.groupby('sex').agg({'income': 'mean', 'job_prestige':'mean', 'socioeconomic_index':'mean', 'education':'mean'}).round(2)
fig = ff.create_table(table)
fig.layout.width = 800
fig.layout.height = 300


### Barplot
gss_bar = gss_clean.groupby(['sex', 'male_breadwinner']).size().reset_index().rename({0:'count'}, axis=1)
fig_1 = px.bar(gss_bar, x='male_breadwinner', y='count', color='sex',
            labels={'male_breadwinner': 'agree/disagree: male is the bread winner', 'count':'number of responses'},
            text='count',
            barmode='group')
fig_1.update_layout(showlegend=True)

### Scatterplot
fig_2 = px.scatter(gss_clean, x='job_prestige', y='income',
                 color = 'sex',
                 trendline='ols',
                 height=600, width=600,
                 labels={'income':'annual income', 
                        'job_prestige':'occupational prestige score'},
                 hover_data=['education', 'socioeconomic_index'])
fig_2.layout.width = 700
fig_2.layout.height = 650

### Boxplots for income and job prestige side-by-side
fig_3 = px.box(gss_clean, x='sex', y = 'income', color = 'sex',
                   labels={'income':'personal annual income', 'sex':''})
fig_3.update_layout(showlegend=False)
fig_3.layout.width = 550
fig_3.layout.height = 500

fig_4 = px.box(gss_clean, x='sex', y = 'job_prestige', color = 'sex',
                   labels={'job_prestige':'occupational prestige score', 'sex':''})
fig_4.update_layout(showlegend=False)
fig_4.layout.width = 550
fig_4.layout.height = 500

### Boxplots
gss_plot = gss_clean[['income', 'sex', 'job_prestige']]
gss_plot['prestige_cat'] = pd.cut(gss_plot['job_prestige'], bins=[15.99, 26.66, 37.33, 47.99, 58.66, 69.33, 80], 
                                  labels=('level1', 'level2', 'level3', 'level4', 'level5', 'level6'))
gss_plot = gss_plot.dropna()

fig_5 = px.box(gss_plot, x='sex', y = 'income', color = 'sex', 
             facet_col='prestige_cat', facet_col_wrap = 2,
             labels={'prestige_cat':'occupational prestige Level', 'income':'annual income', 'sex':''},
             color_discrete_map = {'male':'blue', 'female':'red'})
fig_5.update_layout(showlegend=True)
fig_5.layout.width = 800
fig_5.layout.height = 900

gss_clean['education_level'] = pd.cut(gss_clean['education'], bins=[-0.01, 6, 8, 12, 16, 20], 
                                      labels=('Elementary', 'Middle School', 'High School', 'College', 'Graduate'))
value_columns = ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork'] 
group_columns = ['sex', 'region', 'education_level']
gss_dropdown = gss_clean[value_columns + group_columns].dropna()

### Create app
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    [
        html.H1("Exploring the Gender Wage Gap with GSS", style={'textAlign': 'center'}),
        
        dcc.Markdown(children = markdown_text),
        
        html.H4("Comparing Mean Income, Occupational Prestige, Socioeconomic Status and Education Level By Gender", ),
        
        dcc.Graph(figure=fig),
    
        html.H4("Comparing the Relationship Between Annual Income and Occupational Prestige By Gender"),
        
        dcc.Graph(figure=fig_2),
        
        html.Div([
            
            html.H4("Boxplot For Annual Income By Gender"),
            
            dcc.Graph(figure=fig_3)
            
        ], style = {'backgroundColor':'#111111', 'color':'#7FDBFF', 'width':'50%', 'float':'left'}),
        
        html.Div([
            
            html.H4("Boxplot For Occupational Prestige By Gender"),
            
            dcc.Graph(figure=fig_4)
            
        ], style = {'backgroundColor':'#111111', 'color':'#7FDBFF', 'width':'50%', 'float':'right'}),
        
        html.H4("Boxplot For Annual Income By Gender and Occupational Prestige Level"),
        
        dcc.Graph(figure=fig_5),
        
        html.H4("Barplots with Dropdown Menu"),
        
        html.Div([
            html.H3("y-axis features"),
            dcc.Dropdown(id='values',
                         options=[{'label': i, 'value': i} for i in value_columns],
                         value='satjob'),

            html.H3("x-axis features"),
            dcc.Dropdown(id='groups',
                         options=[{'label': i, 'value': i} for i in group_columns],
                         value='sex')
        ], style={'width': '25%', 'float': 'right'}),
        
        html.Div([
            dcc.Graph(id="graph")
        ], style={'width': '70%', 'float': 'left'}),
        
    ]
)
@app.callback(Output(component_id="graph",component_property="figure"), 
                  [Input(component_id='values',component_property="value"),
                   Input(component_id='groups',component_property="value")])

def make_figure(x,y):
    gss_bar = gss_dropdown.groupby([x, y]).size().reset_index().rename({0:'count'}, axis=1)
    return px.bar(
        gss_bar,
        x=x,
        y='count',
        color=y,
        text='count',
        barmode='group',
        height=600
)


if __name__ == '__main__':
    app.run_server(debug=True)

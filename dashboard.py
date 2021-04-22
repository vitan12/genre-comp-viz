import dash
import dash_core_components as dcc
import dash_html_components as html
from matplotlib.pyplot import polar
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pickle

NUM_GENRES = 8

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

with open('spectogram.pickle', 'rb') as file, open ('chroma.pickle', 'rb') as file2:
    spectograms = pickle.load(file)
    chroma_graphs = pickle.load(file2)
radar_data = pd.read_csv('filtered.csv')
scalemin = radar_data['(\'echonest\', \'audio_features\', \'tempo\')'].min() 
scalemax = radar_data['(\'echonest\', \'audio_features\', \'tempo\')'].max()

app.layout = html.Div([
    dcc.Tabs(id='av-tabs', value='tab-1', children=[
        dcc.Tab(label='Radar Graphs', value='tab-1'),
        dcc.Tab(label='Spectrograms/Chromagrams', value='tab-2'),
    ]),
    html.Div(id='av-tabs-content')
])

# for the tabs, fill in ??? with the actual data

# radar tab
row = 1
col = 1
fig_radar = make_subplots(rows=2, cols=4, specs=[[{'type': 'polar'} for x in range(4)] for y in range(2)], horizontal_spacing=.1, \
                          subplot_titles=['Hip-Hop', 'Pop', 'Folk', 'Rock', 'International', 'Electronic', 'Instrumental', 'Experimental'])
for count, genre in enumerate(radar_data['(\'track\', \'genre_top\')'].unique(), 0):
    names = [x.split(',')[2][2:-2].title() for x in radar_data.columns[1:-1]]
    data = list(radar_data[radar_data['(\'track\', \'genre_top\')'] == genre].mean())[1:]
    data[-2] = (data[-2] - scalemin) / (scalemax - scalemin)
    trace = go.Scatterpolar(r=data, theta=list(names), fill='toself', name=genre)
    fig_radar.add_trace(trace, row=row, col=col)
    if col == 4:
        row += 1
        col = 0
    col += 1
fig_radar.update_polars(radialaxis=dict(range=[0,1]))
fig_radar.update_layout(height=1000)

@app.callback(Output('av-tabs-content', 'children'),
              Input('av-tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Comparison of Genre Attributes'),
            dcc.Graph(id='Radar', figure=fig_radar)
        ])
    elif tab == 'tab-2':
        selections =  [{'label': x, 'value': x} for x in radar_data['(\'track\', \'genre_top\')'].unique()]
        return html.Div([
            html.Div([
                html.H3(''),
                dcc.Dropdown(id='spectro-dropdown', options=selections, value='Pop'),
                html.Div(id='spectro'),
            ], className="six columns"),
            html.Div([
                html.H3(''),
                dcc.Dropdown(id='spectro-dropdown-2', options=selections, value='Hip-Hop'),
                html.Div(id='spectro-2'),
            ], className="six columns"), 
        ], className="row")

@app.callback(
    dash.dependencies.Output('spectro', 'children'),
    [dash.dependencies.Input('spectro-dropdown', 'value')])
def render_spectro(value):
    fig_spectro = make_subplots(rows=3, cols=1, specs=[[{'type': 'xy'}], [{'type': 'xy'}], [{'type': 'polar'}]],
            shared_xaxes=True)
    
    fig_spectro.add_trace(go.Heatmap(
                    z=spectograms[value],
                    #labels=dict(x="Time (s)", y="Frequency (kHz)", color="dBFS"),
                   ), row=1, col=1)
    # add chromagram
    fig_spectro.add_trace(go.Heatmap(
                    z=chroma_graphs[value],
                    # labels=dict(x="Time (s)", y="Pitch Class", color="Intensity"),
                    y=["C", "", "D", "", "E", "F", "", "G", "", "A", "", "B"],
                   ), row=2, col=1)
    # add radar graph
    names = [x.split(',')[2][2:-2].title() for x in radar_data.columns[1:-1]]
    data = list(radar_data[radar_data['(\'track\', \'genre_top\')'] == value].mean())[1:]
    data[-2] = (data[-2] - scalemin) / (scalemax - scalemin)
    trace = go.Scatterpolar(r=data, theta=list(names), fill='toself', name=value)
    fig_spectro.add_trace(trace, 3, 1)
    fig_spectro.update_polars(radialaxis=dict(range=[0,1]))
    # fig_spectro.update_layout(
    #         height=1000)
    #         coloraxis=dict(colorscale='deep_r', ),
    #         coloraxis2=dict(colorscale='matter_r'))
    return dcc.Graph(id="spectro", figure=fig_spectro, style={'height':'90vh'})

@app.callback(
    dash.dependencies.Output('spectro-2', 'children'),
    [dash.dependencies.Input('spectro-dropdown-2', 'value')])
def render_spectro_2(value):
    fig_spectro = make_subplots(rows=3, cols=1, specs=[[{'type': 'xy'}], [{'type': 'xy'}], [{'type': 'polar'}]],
            shared_xaxes=True)
    
    fig_spectro.add_trace(go.Heatmap(
                    z=spectograms[value],
                    #labels=dict(x="Time (s)", y="Frequency (kHz)", color="dBFS"),
                   ), row=1, col=1)
    # add chromagram
    fig_spectro.add_trace(go.Heatmap(
                    z=chroma_graphs[value],
                    # labels=dict(x="Time (s)", y="Pitch Class", color="Intensity"),
                    y=["C", "", "D", "", "E", "F", "", "G", "", "A", "", "B"],
                   ), row=2, col=1)
    # add radar graph
    names = [x.split(',')[2][2:-2].title() for x in radar_data.columns[1:-1]]
    data = list(radar_data[radar_data['(\'track\', \'genre_top\')'] == value].mean())[1:]
    data[-2] = (data[-2] - scalemin) / (scalemax - scalemin)
    trace = go.Scatterpolar(r=data, theta=list(names), fill='toself', name=value)
    fig_spectro.add_trace(trace, 3, 1)
    fig_spectro.update_polars(radialaxis=dict(range=[0,1]))
    # fig_spectro.update_layout(
    #         height=1000)
    #         coloraxis=dict(colorscale='deep_r', ),
    #         coloraxis2=dict(colorscale='matter_r'))
    return dcc.Graph(id="spectro-2", figure=fig_spectro, style={'height':'90vh'})

if __name__ == '__main__':
    app.run_server(debug=True)

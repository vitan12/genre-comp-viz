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

app = dash.Dash(__name__)

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
fig_radar = make_subplots(rows=2, cols=4, specs=[[{'type': 'polar'} for x in range(4)] for y in range(2)])#, subplot_titles=radar_data['(\'track\', \'genre_top\')'].unique())
for count, genre in enumerate(radar_data['(\'track\', \'genre_top\')'].unique(), 0):
    
    names = [x.split(',')[2][2:-2].title() for x in radar_data.columns[1:-1]]
    data = list(radar_data[radar_data['(\'track\', \'genre_top\')'] == genre].mean())[1:]
    data[-2] = (data[-2] - scalemin) / (scalemax - scalemin)
    # df = pd.DataFrame(dict(r=list(data.values[1:]), theta=list(names)))
    # trace = go.Scatterpolar(df, r= 'r', theta='theta', line_close=True)
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
            html.H3('In-Depth View of a Genre'),
            dcc.Dropdown(id='spectro-dropdown', options = selections, value='Pop'),
            html.Div(id='dd-output-container')      
        ])

@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('spectro-dropdown', 'value')])
def render_spectro(value):
    # spectrogram/chromagram tab
    fig_spectro = make_subplots(rows=2, cols=2, specs=[[{'type': 'xy'}, {'type': 'xy'}], [{'type': 'polar'}, {'type': 'polar'}]])
    # add spectrogram
    
    fig_spectro.add_trace(go.Heatmap(
                    z=spectograms[value]
                    #labels=dict(x="Time (s)", y="Frequency (kHz)", color="dBFS"),
                   ), 1, 1)
    # add chromagram
    fig_spectro.add_trace(go.Heatmap(
                    z=chroma_graphs[value], 
                    #labels=dict(x="Time (s)", y="Pitch Class", color="Intensity"),
                    y=["C", "", "D", "", "E", "F", "", "G", "", "A", "", "B"]
                   ), 1, 2)
    # add radar graph
    names = [x.split(',')[2][2:-2].title() for x in radar_data.columns[1:-1]]
    data = list(radar_data[radar_data['(\'track\', \'genre_top\')'] == genre].mean())[1:]
    data[-2] = (data[-2] - scalemin) / (scalemax - scalemin)
    # df = pd.DataFrame(dict(r=list(data.values[1:]), theta=list(names)))
    # trace = go.Scatterpolar(df, r= 'r', theta='theta', line_close=True)
    trace = go.Scatterpolar(r=data, theta=list(names), fill='toself', name=genre)
    fig_spectro.add_trace(trace, 2, 1)
    fig_spectro.update_polars(radialaxis=dict(range=[0,1]))
    fig_spectro.update_layout(height=500)

    return dcc.Graph(id="Spectro", figure=fig_spectro)

if __name__ == '__main__':
    app.run_server(debug=True)
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
import plotly

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
        dcc.Tab(label='FAQ', value='tab-3')
    ]),
    html.Div(id='av-tabs-content')
])

# for the tabs, fill in ??? with the actual data

# radar tab
row = 1
col = 1
fig_radar = make_subplots(rows=2, cols=4, specs=[[{'type': 'polar'} for x in range(4)] for y in range(2)], horizontal_spacing=.1, \
                          subplot_titles=['Hip-Hop', 'Pop', 'Folk', 'Rock', 'International', 'Electronic', 'Instrumental', 'Experimental'])
colors = plotly.colors.DEFAULT_PLOTLY_COLORS
color_map = {}
for count, genre in enumerate(radar_data['(\'track\', \'genre_top\')'].unique(), 0):
    names = [x.split(',')[2][2:-2].title() for x in radar_data.columns[1:-1]]
    data = list(radar_data[radar_data['(\'track\', \'genre_top\')'] == genre].mean())[1:]
    data[-2] = (data[-2] - scalemin) / (scalemax - scalemin)
    color_map[genre] = colors[count]
    trace = go.Scatterpolar(r=data, theta=list(names), fill='toself', name=genre, marker=dict(color=color_map[genre]))
    fig_radar.add_trace(trace, row=row, col=col)
    if col == 4:
        row += 1
        col = 0
    col += 1
fig_radar.update_polars(radialaxis=dict(range=[0,1]))
fig_radar.update_layout(height=1000, legend_y=1.1)
 
for idx, annotation in enumerate(fig_radar['layout']['annotations']): 
        if idx < 4:
            annotation['yanchor']='bottom'
            annotation['y']=1.025
            annotation['yref']='paper'
        else:
            annotation['yanchor']='bottom'
            annotation['y']=0.4
            annotation['yref']='paper'

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
        x = html.Div([
            html.Div([
                html.H3(''),
                dcc.Dropdown(id='spectro-dropdown', options=selections, value='Pop'),
                # html.Div(id='spectro'),
                dcc.Graph(id='spectro', style={'height':'90vh'})
            ], className="six columns"),
            html.Div([
                html.H3(''),
                dcc.Dropdown(id='spectro-dropdown-2', options=selections, value='Hip-Hop'),
                # html.Div(id='spectro-2'),
                dcc.Graph(id='spectro-2', style={'height':'90vh'})
            ], className="six columns"), 
        ], className="row")
        return x
    elif tab == 'tab-3':
        return html.Div([
            html.H3('FMA Dataset'),
            html.P('The songs we analyzed are all licensed under Creative Commons and can be found in the following public dataset:'),
            dcc.Link(href='https://github.com/mdeff/fma'),
            html.H3('Radar Graph Metrics'),
            html.P('Energy: Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.'),
            html.P('Danceability: Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.'),
            html.P('Acousticness: A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.'),
            html.P('Valence: A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).'),
            html.P('Tempo: The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration. For our visualization, we standardize tempo on a 0 to 1 scale.'),
            html.P('Speechiness: Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.'),
            html.P('Liveness: Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.'),
            html.P('Instrumentalness: Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.'),
            html.P('Source:'),
            dcc.Link(href='https://developer.spotify.com/documentation/web-api/reference/#category-tracks'),
            html.H3('Spectrograms'),
            html.P('Spectrograms are a way of visualizing the waveforms of different sound files by plotting their frequencies over time. In other words, it’s a way to see a sound file. Each data point is an xyz triple, where each time (x) and frequency (y) pair has an associated dBFS (z) value, where dBFS is decibels relative to full scale. dBFS works just like decibels (dB) except that there is a defined maximum set to value of 0. You can read more about dBFS here:'),
            dcc.Link(href='https://en.wikipedia.org/wiki/DBFS'),
            html.H3('Chromagrams'),
            html.P('Chromagrams categorize frequencies at each time into “pitch classes,” classifying what note is likely being played at that time. This can give interesting insight into the structure of a song’s melody and harmony. Just like spectrograms, each data point on a chromagram is an xyz triple, where each time (x) and pitch class (y) has an associated intensity (z).')
        ])



def gen_plot(value, graph_id):
    fig_spectro = make_subplots(rows=3, cols=1, specs=[[{'type': 'xy'}], [{'type': 'xy'}], [{'type': 'polar'}]], subplot_titles=['Spectrogram', 'Chromagram', 'Attributes'])
    
    fig_spectro.add_trace(go.Heatmap(
                    z=spectograms[value],
                    # labels=dict(x="Time (s)", y="Frequency (kHz)", color="dBFS"),
                    colorbar=dict(len=0.25, y=.89, title='dBFS')
                   ), row=1, col=1)
    # add chromagram
    # print(chroma_graphs[value].shape)
    fig_spectro.add_trace(go.Heatmap(
                    z=chroma_graphs[value],
                    # labels=dict(x="Time (s)", y="Pitch Class", color="Intensity"),
                    y=["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
                    colorbar=dict(len=0.25, y=.505, title='Intensity'),
                    colorscale='Viridis'
                   ), row=2, col=1)
    # add radar graph
    names = [x.split(',')[2][2:-2].title() for x in radar_data.columns[1:-1]]
    data = list(radar_data[radar_data['(\'track\', \'genre_top\')'] == value].mean())[1:]
    data[-2] = (data[-2] - scalemin) / (scalemax - scalemin)
    trace = go.Scatterpolar(r=data, theta=list(names), fill='toself', name=value, marker=dict(color=color_map[value]))
    fig_spectro.add_trace(trace, 3, 1)
    fig_spectro.update_polars(radialaxis=dict(range=[0,1]))
    # fig_spectro.update_layout(
    #         coloraxis=dict(colorscale='deep_r', y=.85, len=.25),
    #         coloraxis2=dict(colorscale='matter_r', len=.25, y=.5))
    fig_spectro['layout']['xaxis']['title'] = 'Time (ms)'
    fig_spectro['layout']['xaxis2']['title'] = 'Time (ms)'
    fig_spectro['layout']['yaxis']['title'] = 'Frequency (kHz)'
    fig_spectro['layout']['yaxis2']['title'] = 'Pitch Class'
    
    fig_spectro['layout']['annotations'][2]['y']=0.25
    return fig_spectro
    # return dcc.Graph(id=graph_id, figure=fig_spectro, style={'height':'90vh'})

@app.callback(
    dash.dependencies.Output('spectro', 'figure'),
    [dash.dependencies.Input('spectro-dropdown', 'value')])
def render_spectro(value):
    return gen_plot(value, 'spectro')

@app.callback(
    dash.dependencies.Output('spectro-2', 'figure'),
    [dash.dependencies.Input('spectro-dropdown-2', 'value')])
def render_spectro_2(value):
    return gen_plot(value, 'spectro-2')



if __name__ == '__main__':
    app.run_server(debug=True)

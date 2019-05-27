# -*- coding: utf-8 -*-/
"""
Created on Wed Jan  2 18:33:20 2019

@author: Sam Purkiss
"""

#Updates
#This version was changed so that it no longer relies on 
#webscraping each time the tv show is changed.
#Instead it relies on a database of show ratings

import pandas as pd
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html

average_season_ratings = pd.read_csv('https://raw.githubusercontent.com/sampurkiss/movie_ratings_imdb/master/average_rating_by_season.csv')
average_season_ratings = average_season_ratings.sort_values(by = ['tvshow_code','seasonNumber'], ascending = True)

titles = pd.read_csv('https://raw.githubusercontent.com/sampurkiss/movie_ratings_imdb/master/episode_rating_database.csv')
titles['show_premier_year'] = titles['show_premier_year'].astype(str)

list_text = (titles[['show_name','show_premier_year','tvshow_code']]
                .groupby(by=['show_name','tvshow_code'])
                .min()
                .reset_index()
            )
#show.plot_ratings()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


app.layout = html.Div([
    html.Div([html.Label('Dropdown menu'),
                dcc.Dropdown(id='show-identifier',
                    options = [
                        {'label': list_text['show_name'].iloc[i].title()+', '+list_text['show_premier_year'].iloc[i],
                         'value': list_text['tvshow_code'].iloc[i]} for i in range(0,len(list_text))],
                            value= 'tt1856010')]),
    dcc.Graph(
    id= 'tv-show-ratings')    
    ])

######################################
#Change layout given dropdown value
######################################
@app.callback(
        dash.dependencies.Output('tv-show-ratings','figure'),
        [dash.dependencies.Input('show-identifier','value')]
        )

def update_graph(show_identifier_value):
    data_table = titles.loc[titles['tvshow_code']==show_identifier_value]
    averages = average_season_ratings.loc[average_season_ratings['tvshow_code']==show_identifier_value]

    show_name = list_text[list_text['tvshow_code']==show_identifier_value]['show_name'].iloc[0]
    hover_text = []
    for i in range(0,len(data_table)):
        hover_text.append(
                ('Episode {episode_number}, <br>'+
                 '{name}').format(episode_number = data_table['episodeNumber'].iloc[i],
                             name = data_table['episode_name'].iloc[i]))            

    return {'data': [go.Scatter(
                    x=data_table['seasonNumber'],
                    y=data_table['averageRating'],
                    text=hover_text,
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 7,
                        'line': {'width': 0.5, 
                                 'color': 'white'}
                    },
                    name='Episode'), 
                go.Scatter(
                    x=averages['seasonNumber'],
                    y=averages['averageRating'],
                    text='Average',
                    mode='lines',
                    opacity=0.7,
                    line={'width':2,
                          'dash': 'longdash',
                        'color': 'red'
                    },
                    name='Average Season Rating')],
                
            'layout': go.Layout(
                    title=show_name.title()+' Episode Ratings',
                xaxis={'title': 'Season',
                       'tickformat':',d'},
                yaxis={'title': 'Rating', 'range':[0,10]},
                showlegend=True,
                legend=dict(bgcolor='rgba(0,0,0,0)',
                            x=0.05,
                            y=0.15
                            ),
                hovermode='closest',
            )
        }
    

if __name__ == '__main__':
    app.run_server(debug=True)





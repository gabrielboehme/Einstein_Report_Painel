import json
import plotly
import pandas as pd
import numpy as np
from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar, Heatmap, Histogram, Scatter
import plotly


#Flask Config
app = Flask(__name__)


#Import database
df = pd.read_csv('Dados/covid_data.csv')

#Routes
@app.route('/')
@app.route('/index')
def index():
    
    #Extract columns
    states = df['full_state']
    deaths = df['deaths']
    cases = df['cases']
    hospital_bed = df['total_hospital_beds']
    corr = df.corr()
    h_index = list(corr.iloc[:,1:].index)
    h_values = corr.values
    today_deaths = pd.read_csv('ETL/covid_hospital_data.csv')['todayDeaths'].sum()

    #KPI's
    total_deaths = df['deaths'].sum()
    total_cases = df['cases'].sum()
    worst_state = df[df['deaths']==df['deaths'].max()]['state'].iloc[0]
    


    # create visuals
    graphs = [
        {
            'data': [
                Bar(
                    x=states,
                    y=deaths
                )
            ],

            'layout': {
                'title': 'Mortes de Covid-19 por estado',
                'yaxis': {
                    'title': "Mortes"
                },
                'xaxis': {
                    'title': "Estado",
                    'tickangle' : 70
                },
                'margin' : {
                    'b' : 200
                }
            }
        },
        {
            'data': [
                Bar(
                    x=states,
                    y=cases
                )
            ],

            'layout': {
                'title': 'Casos de Covid-19 por estado',
                'yaxis': {
                    'title': "Casos"
                },
                'xaxis': {
                    'title': "Estado",
                    'tickangle' : 70
                },
                'margin' : {
                    'b' : 200
                }
            }
        },
        {
            'data': [
                Heatmap(
                    x=h_index,
                    y=h_index,
                    z=h_values
                )    
            ],

            'layout': {
                'title': 'Mapa de calor de correlação entre as categorias',
                'font': {
                    'size': 11
                        },
                'yaxis': {
                        'tickangle' : 30
                        },
                'xaxis': {
                        'tickangle' : 30
                        },
                'margin': {
                    'b' : 200
                }
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON, total_deaths=total_deaths, total_cases=total_cases, worst_state=worst_state, today_deaths=today_deaths)

def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()
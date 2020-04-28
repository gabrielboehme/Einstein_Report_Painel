#Import libs
import pandas as pd
import numpy as np
import requests

#Importing datasets
def load_data():
    df = pd.read_csv(r'hospital_capacity_by_us_state.csv')
    labels = df.columns[0].split(';')
    df = df.iloc[:52,0].str.split(';',expand=True)
    df.columns = labels



    covid_json = requests.get('https://corona.lmao.ninja/v2/states')
    covid_json = covid_json.text
    covid_data = pd.read_json(covid_json)
    covid_data.to_csv('covid_hospital_data.csv')
    covid_data = covid_data.iloc[:,1:4]
    states_abv = pd.read_csv('../Dados/states_abv.csv') 

    covid_data = covid_data.merge(states_abv,how='left',left_on='state',right_on='full_state').drop('state',axis=1)
    covid_data

    df_covid = df.merge(covid_data,how='left',left_on='state',right_on='State').drop('State',axis=1)
    for column in df_covid.columns:
        df_covid[column] = df_covid[column].astype('int64',errors='ignore')
    df_covid.to_csv('../Dados/covid_data.csv')

    return None

#Execute function
def main():

	load_data()
	print('Extracting from csv files...')

	print('Transforming data...')

	print('Saving data into new csv files...')

if __name__ == '__main__':
	main()
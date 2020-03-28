#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
file: analysis_COVID19.py
author: Sebastian Wildowicz
created: 24.03.2020
"""
from prettytable import PrettyTable
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import os

# format date support function
def format_date(date: datetime.date):
    if os.name == "nt":
        return date.strftime('%yy-%m-%m')
    else:
        return date.strftime('%Y-%m-%d')
        
# prepare date for upload the newest date about COVID19
current_date = format_date(datetime.date.today())
# prepare proper URL and load updated data
# load confirmed COVID19 data
url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
covid19_confirmed_data_raw = pd.read_csv(url, error_bad_lines=False)
# load deaths from COVID19 data
url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
covid19_deaths_data_raw = pd.read_csv(url, error_bad_lines=False)
# load recovered from COVID19 data
url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
covid19_recovered_data_raw = pd.read_csv(url, error_bad_lines=False)
# load country data
csv_file = "countries of the world.csv"
countries_data = pd.read_csv(csv_file, error_bad_lines=False)

def get_country_polulation(country_name):
    countries = countries_data.loc[:,['Country']].values
    for i ,name in zip(range(len(countries)), countries):
        if name[0][:-1] == country_name:
            return int(countries_data.loc[:,['Population']].values[i])

def get_country_area(country_name):
    countries = countries_data.loc[:,['Country']].values
    for i ,name in zip(range(len(countries)), countries):
        if name[0][:-1] == country_name:
            return int(countries_data.loc[:,['Area (sq. mi.)']].values[i])

def find_the_bigest_countries(number_of_countires):
    list_to_return = []
    the_bigest_countries = countries_data.sort_values(by = ['Area (sq. mi.)'], ascending=True)
    for country_name in list(the_bigest_countries.loc[:,'Country'].tail(number_of_countires)):
        list_to_return.append(country_name[:-1])
    return list(reversed(list_to_return))

def find_the_most_populated_countries(number_of_countires):
    list_to_return = []
    the_most_populated_countries = countries_data.sort_values(by = ['Population'], ascending=True)
    for country_name in list(the_most_populated_countries.loc[:,'Country'].tail(number_of_countires)):
        list_to_return.append(country_name[:-1])
    return list(reversed(list_to_return))

def clean_covid_data(raw_data_file):
    cleaned_data_file = raw_data_file.melt(id_vars=['Province/State','Country/Region','Lat','Long'],value_name='Cases',var_name='Date')
    cleaned_data_file = cleaned_data_file.set_index(['Country/Region','Province/State','Date'])
    return cleaned_data_file 

# get country Data
def get_covid_data(df_cleaned,oldname,newname):
    df_country = df_cleaned.groupby(['Country/Region','Date'])['Cases'].sum().reset_index()
    df_country = df_country.set_index(['Country/Region','Date'])
    df_country.index = df_country.index.set_levels([df_country.index.levels[0], pd.to_datetime(df_country.index.levels[1])])
    df_country = df_country.sort_values(['Country/Region','Date'],ascending=True)
    df_country = df_country.rename(columns={oldname:newname})
    return df_country
  
def print_information(country_name_array):
    x = PrettyTable()
    x.field_names = ["Country name", "Area [sq. mi.]", "Population"]
    for country_name in country_name_array:
        x.add_row([country_name, str(get_country_area(country_name)), str(get_country_polulation(country_name))])
    for field_name in x.field_names:
        x.align[field_name] = "l"
    print(x)

def plot_data(ax, country_array, covid19_data, title_name):
    plt.subplot(3, 1, ax)
    for country_name in country_array:
        if (country_name == 'United States'):
            country_name = 'US'
        covid19_data_temp = covid19_data.loc[country_name]
        plt.plot(covid19_data_temp,label=country_name, marker='o')
    plt.gca().legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(title_name)

def plot_total_data_bar(ax, country_array, covid19_data, title_name):
    bar_array = []
    plt.subplot(3, 1, ax)
    for country_name in country_array:
        if (country_name == 'United States'):
            country_name = 'US'
        bar_array.append(int(covid19_data.loc[country_name].values[-1]))
    bar1 = plt.bar(country_array, bar_array, color=['red', 'black', 'green', 'blue', 'cyan'])
    for rect in bar1:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom')
    plt.title(title_name)
    plt.tight_layout()

def plot_total_data_pie(fig, ax, country_array, covid19_data, title_name):
    pie_array = []
    for country_name in country_array:
        if (country_name == 'United States'):
            country_name = 'US'
        pie_array.append(int(covid19_data.loc[country_name].values[-1]))
    fig.add_trace(go.Pie(labels=country_array, values=pie_array, textinfo='label + value', name=title_name,hole=.3),
              1, ax)    
   
# prepare data 
covid19_confirmed_data_cleaned = clean_covid_data(covid19_confirmed_data_raw)
covid19_deaths_data_cleaned = clean_covid_data(covid19_deaths_data_raw)
covid19_recovered_data_cleaned = clean_covid_data(covid19_recovered_data_raw)

covid19_confirmed_data = get_covid_data(covid19_confirmed_data_cleaned,'Cases','Total Confirmed Cases')
covid19_recovered_data = get_covid_data(covid19_recovered_data_cleaned,'Cases','Total Recoveries')
covid19_deaths_data = get_covid_data(covid19_deaths_data_cleaned,'Cases','Total Deaths')

NUM_COUNTRIES_TO_ANALYSES = 10
# find 10 the bigest countries
the_bigest_countries = find_the_bigest_countries(NUM_COUNTRIES_TO_ANALYSES)
# find 10 the most populated countries
the_most_populated_countries = find_the_most_populated_countries(NUM_COUNTRIES_TO_ANALYSES)

#print information
print("$> 10 the bigest countries")
print_information(the_bigest_countries)
print("$> 10 the most populated countries")
print_information(the_most_populated_countries)

# create the plots
plt.figure(1)
plot_data(1, the_bigest_countries, covid19_confirmed_data, "Najwieksze kraje - potwierdzone przypadki COVID19")
plot_data(2, the_bigest_countries, covid19_recovered_data,"Najwieksze kraje - wyleczone przypadki z COVID19")
plot_data(3, the_bigest_countries, covid19_deaths_data, "Najwieksze kraje - potwierdzone zgony na COVID19")

plt.figure(2)
plot_data(1, the_most_populated_countries, covid19_confirmed_data, "Najludniejsze kraje - potwierdzone przypadki COVID19")
plot_data(2, the_most_populated_countries, covid19_recovered_data,"Najludniejsze kraje - wyleczone przypadki z COVID19")
plot_data(3, the_most_populated_countries, covid19_deaths_data, "Najludniejsze kraje - potwierdzone zgony na COVID19")

plt.figure(3)
plot_total_data_bar(1, the_bigest_countries, covid19_confirmed_data, "Najwieksze kraje - suma potwierdzonych przypadków COVID19")
plot_total_data_bar(2, the_bigest_countries, covid19_recovered_data,"Najwieksze kraje - suma wyleczonych przypadków z COVID19")
plot_total_data_bar(3, the_bigest_countries, covid19_deaths_data, "Najwieksze kraje - suma potwierdzonych zgonów na COVID19")

plt.figure(4)
plot_total_data_bar(1, the_most_populated_countries, covid19_confirmed_data, "Najludniejsze kraje - suma potwierdzonych przypadków COVID19")
plot_total_data_bar(2, the_most_populated_countries, covid19_recovered_data,"Najludniejsze kraje - suma wyleczonych przypadków z COVID19")
plot_total_data_bar(3, the_most_populated_countries, covid19_deaths_data, "Najludniejsze kraje - suma potwierdzonych zgonów na COVID19")
plt.show()

fig = make_subplots(rows=1, cols=3, specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]])
plot_total_data_pie(fig, 1, the_bigest_countries, covid19_confirmed_data, "Najwieksze kraje - suma potwierdzonych przypadków COVID19")
plot_total_data_pie(fig, 2, the_bigest_countries, covid19_recovered_data,"Najwieksze kraje - suma wyleczonych przypadków z COVID19")
plot_total_data_pie(fig, 3, the_bigest_countries, covid19_deaths_data, "Najwieksze kraje - suma potwierdzonych zgonów na COVID19")
fig.show()

fig = make_subplots(rows=1, cols=3, specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]])
plot_total_data_pie(fig, 1, the_most_populated_countries, covid19_confirmed_data, "Najludniejsze kraje - suma potwierdzonych przypadków COVID19")
plot_total_data_pie(fig, 2, the_most_populated_countries, covid19_recovered_data,"Najludniejsze kraje - suma wyleczonych przypadków z COVID19")
plot_total_data_pie(fig, 3, the_most_populated_countries, covid19_deaths_data, "Najludniejsze kraje - suma potwierdzonych zgonów na COVID19")
fig.show()
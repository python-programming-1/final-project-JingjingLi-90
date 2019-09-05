#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 20:21:00 2019

@author: jingjingli
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
pd.set_option('display.max_columns', None)
#r = requests.get('https://data.ftb.ca.gov/api/views/mriu-wsxf/')
#data_info = r.json()

#data_info['columns'][7]['cachedContents']['average']

data = pd.read_csv('Personal_Income_Tax_Statistics_By_Zip_Code.csv')
#data.head()
data_year_total_AGI = data.groupby(['Taxable Year','Zip Code'])['CA AGI'].sum()
data_year_total_AGI
data['Avg AGI']=data['CA AGI']/data['Returns']
data['Avg Tax Liability']=data['Total Tax Liability']/data['Returns']
data.head()

data_year_county = data.groupby(['Taxable Year','County'])['Avg AGI'].mean()
data_year_county_form=data_year_county.unstack()
fig, ax = plt.subplots(figsize=(15,7))
data_year_county_form.plot(ax=ax)

LA=data[data.County=='Los Angeles']
#LA.head()


LA_year_trend = LA.groupby(['Taxable Year','City'])['Avg AGI'].mean()
LA_year_trend
fig, ax = plt.subplots(figsize=(15,7))
LA_year_trend.unstack().plot(ax=ax, legend= False)

plt.subplots(figsize=(12,30))
LA_Return=LA.groupby('City').size().reset_index(name='count').sort_values(by='count',ascending=False)

ax=sns.barplot(y='City',x='count',data=LA_Return,palette="coolwarm").set_title("LA Returns by City")
plt.xticks(rotation=90)


LA.rename(columns={'Taxable Year':'Year'}, inplace=True)
LA_2017 = LA[LA.Year==2017]
LA_2017.head()
data.rename(columns={'Taxable Year':'Year'}, inplace=True)
data_2017 = data[data.Year==2017]
new = data_2017["Location"].str.split("\n", n = 1, expand = True) 
new[1] =  new[1].apply(lambda x: x.replace('(','').replace(')',''))
site= new[1].str.split(',',n=1,expand=True)
site.head()
data_2017['Latitude']=site[0]
data_2017['Longitude']=site[1]


data_2017.dropna()
data_2017.head()
from bokeh.plotting import figure, show,output_file

from bokeh.models import ColumnDataSource, HoverTool, CategoricalColorMapper

from bokeh.palettes import plasma,inferno,magma
from bokeh.layouts import gridplot
from bokeh.tile_providers import get_provider, Vendors
#import math

#def lgn2x(a):
#    return a * (math.pi/180) * 6378137

#def lat2y(a):
 #   return math.log(math.tan(a * (math.pi/180)/2 + math.pi/4)) * 6378137
#data_2017['x'] = data_2017.Longitude.apply(lambda row: lgn2x(row))
#data_2017['y'] = data_2017.Latitude.apply(lambda row: lat2y(row))
data_2017_map = data_2017[['Zip Code','City','County','Avg AGI','Avg Tax Liability','Latitude','Longitude']].sort_values(by='Avg AGI')
data_2017_map.head()
data_2017_map['dot_size']=data_2017_map['Avg AGI']/100000
data_2017_map['dot_size'].values[data_2017_map['dot_size']<0]=0.01
#data_2017_map.head(20)
cds = ColumnDataSource(data_2017_map)
hover = HoverTool(tooltips=[('City', '@City'),
                            ('Zip Code', '@Zip Code'),
                           ('Avg AGI', '@Avg AGI'),
                           ('Avg Tax Liability', '@Avg Tax Liability')],
                  mode='mouse')
up = figure(title='Avg Personal Income in CA',
           plot_width=2000, plot_height=2000,
           x_axis_location=None, y_axis_location=None, 
           tools=['pan', 'wheel_zoom', 'tap', 'reset', 'crosshair', hover])
tile_provider=get_provider(Vendors.CARTODBPOSITRON_RETINA)
up.add_tile(tile_provider)
mapper = CategoricalColorMapper(factors=data_2017_map.City.unique(), 
                                palette=plasma(256)+inferno(256))

scatter = up.circle('Longitude', 'Latitude', source=cds, size='dot_size',
                    color={'field': 'City','transform': mapper}, alpha=.5,
                    selection_color='black',
                    nonselection_fill_alpha=.1,
                    nonselection_fill_color='gray',)
down = figure(title='Personal Income (Click bar below)',
              x_range=data_2017_map.County.unique(),
              plot_width=1000, plot_height=200,
              tools=['tap', 'reset'])
down.vbar(x='County', top='Avg AGI', source=cds, width=.4,
            color={'field': 'County','transform': mapper},
            selection_color='black',
            nonselection_fill_alpha=.1,
            nonselection_fill_color='gray',)
down.xgrid.grid_line_color = None
down.xaxis.major_label_orientation = 'vertical'
down.xaxis.axis_label = 'County'
down.yaxis.axis_label = 'AGI'
p = gridplot([[up], [down]], toolbar_location='left',)
output_file=('Income html')
show(p)


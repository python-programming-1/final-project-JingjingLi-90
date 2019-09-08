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

#pd.set_option('display.max_columns', None)
#r = requests.get('https://data.ftb.ca.gov/api/views/mriu-wsxf/')
#data_info = r.json()
#data_info['columns'][7]['cachedContents']['average']



###import data###
data = pd.read_csv('Personal_Income_Tax_Statistics_By_Zip_Code.csv')
data.head()
###Rename Columns
data.rename(columns={'Taxable Year':'Taxable_Year','Zip Code':'Zip_Code'}, inplace=True)
###check zip code total AGI by year###
data_year_total_AGI = data.groupby(['Taxable_Year','Zip_Code'])['CA AGI'].sum()
data_year_total_AGI
###get avg AGI and tax liability by returns###
data['Avg_AGI']=data['CA AGI']/data['Returns']
data['Avg_Tax_Liability']=data['Total Tax Liability']/data['Returns']
#data.head()


###look into some details in LA county###
LA=data[data.County=='Los Angeles']
#LA.head()

###time trend of Avg AGI and tax liability by city###
LA_AGI_trend = LA.groupby(['Taxable_Year','City'])['Avg_AGI'].mean()
fig, ax1 = plt.subplots(figsize=(15,7))
ax1.set_title('LA Personal Income Trend by City')
ax1.annotate('peak to investigate', xy=(2010, 15782502.22313417), xytext=(2013, 1.6+1e7),
            arrowprops=dict(facecolor='black', shrink=0.03),
            )
LA_AGI_trend.unstack().plot(ax=ax1, legend= False)

LA_Tax_trend = LA.groupby(['Taxable_Year','City'])['Avg_Tax_Liability'].mean()
fig, ax2 = plt.subplots(figsize=(15,7))
ax2.set_title('LA Tax Trend by City')
LA_Tax_trend.unstack().plot(ax=ax2,legend= False)


###LA returns count by city for the whole periods###
plt.subplots(figsize=(12,30))
LA_Return=LA.groupby('City').size().reset_index(name='count').sort_values(by='count',ascending=False)

ax=sns.barplot(y='City',x='count',data=LA_Return,palette="coolwarm").set_title("LA Returns by City")
plt.xticks(rotation=90)



###look into data of 2017 for map plotting###


###split location column with separate lat,lng data###
data_2017 = data[data.Taxable_Year==2017]
new = data_2017["Location"].str.split("\n", n = 1, expand = True) 
new[1] =  new[1].apply(lambda x: x.replace('(','').replace(')',''))
site= new[1].str.split(',',n=1,expand=True)
#site.head()
data_2017['Latitude']=site[0]
data_2017['Longitude']=site[1]



from bokeh.plotting import figure, show, output_file

from bokeh.models import ColumnDataSource, HoverTool, CategoricalColorMapper

from bokeh.palettes import Category20b, Category20c, Spectral,Plasma,Viridis,Inferno,Magma
from bokeh.layouts import gridplot
from bokeh.tile_providers import get_provider, Vendors

import math

###convert lat,lng to x,y coordinates###
def lgn2x(a):
    return a * (math.pi/180) * 6378137

def lat2y(a):
    return math.log(math.tan(a * (math.pi/180)/2 + math.pi/4)) * 6378137
data_2017['x'] = data_2017.Longitude.astype(float).apply(lambda row: lgn2x(row))
data_2017['y'] = data_2017.Latitude.astype(float).apply(lambda row: lat2y(row))

#data_2017.head()
data_2017_map = data_2017[['Zip_Code','City','County','Avg_AGI',
                           'Avg_Tax_Liability','x','y']].sort_values(by='Avg_AGI')
#data_2017_map.head()

###create dot size according to AGI for the map###
data_2017_map['dot_size']=data_2017_map['Avg_AGI']/30000
data_2017_map['dot_size'].values[data_2017_map['dot_size']<0]=0.01
data_2017_map['dot_size'].values[data_2017_map['dot_size']>80]=80
#data_2017_map.sort_values(by='dot_size', ascending=False)
output_file('map_of_personal_income.html')
cds = ColumnDataSource(data_2017_map)

hover = HoverTool(tooltips=[('City', '@City'),
                            ('Zip Code', '@Zip_Code'),
                           ('Avg AGI', '@Avg_AGI'),
                           ('Avg Tax Liability', '@Avg_Tax_Liability')],
                  mode='mouse')
up = figure(title='Avg Personal Income in CA',
           plot_width=1000, plot_height=1000,
           x_axis_location=None, y_axis_location=None, 
           tools=['pan', 'wheel_zoom', 'tap', 'reset', 'crosshair', hover])
tile_provider=get_provider(Vendors.CARTODBPOSITRON_RETINA)
up.add_tile(tile_provider)
mypalette=Category20b[20]+Category20c[20]+Spectral[4]+Plasma[256]+Viridis[256]+Inferno[256]+Magma[256]

mapper = CategoricalColorMapper(factors=data_2017_map.County, 
                                palette=mypalette)

scatter = up.circle('x', 'y', source=cds, size='dot_size',
                    color={'field': 'City','transform': mapper}, alpha=.4,
                    selection_color='black',
                    nonselection_fill_alpha=.1,
                    nonselection_fill_color='gray',)
down = figure(title='Personal Income (Click bar below)',
              x_range=data_2017_map.County.unique(),
              plot_width=1000, plot_height=500,
              tools=['tap', 'reset'])
down.vbar(x='County', top='Avg_AGI', source=cds, width=.4,
            color={'field': 'County','transform': mapper},
            selection_color='black',
            nonselection_fill_alpha=.1,
            nonselection_fill_color='gray',)
down.xgrid.grid_line_color = None
down.xaxis.major_label_orientation = 'vertical'
down.xaxis.axis_label = 'County'
down.yaxis.axis_label = 'AGI'
p = gridplot([[up], [down]], toolbar_location='left',)

show(p)


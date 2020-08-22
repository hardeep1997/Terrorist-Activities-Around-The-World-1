#!/usr/bin/env python
# coding: utf-8

# # Terrorist Activites Around The World
# <p> According to a survey, about 218 million people are affected by calamities, natural and man-made, per annum and about 68000 people loose their lives every year. The frequency of natural disasters like earthquakes, volcanoes, etc have remained broadly, but the number of terrorist activities have grown over the period.
#     The aim of this notebook is to explore the terrorist events around the world. Interactive Plots and Animations are used in this notebook, for making the exploration easy and more informative. This is my first try on <b> Folium </b>, which is a wrapper over the Leaflet. js API. Some things that we will explore are the trends in terrorism over the year, the terrorism prone areas, etc. Since it is a geographic dataset, you will see lot of geomaps.
# 
# <b> Note: I have only used first 5000 rows for folium maps. The reason is the notebook or script crashes a lot and it kills the kernal due to long execution time.

# In[2]:


from IPython.display import HTML

HTML('''<script>
code_show=true; 
function code_toggle() {
 if (code_show){
 $('div.input').hide();
 } else {
 $('div.input').show();
 }
 code_show = !code_show
} 
$( document ).ready(code_toggle);
</script>
<form action="javascript:code_toggle()"><input type="submit" value="Click here to on/off the raw code."></form>''')


# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
plt.style.use('fivethirtyeight')
import plotly.offline as py
py.init_notebook_mode(connected=True)
import plotly.tools as tls
import plotly.graph_objs as go
#from mpl_toolkits.basemap2.lib.mpl_toolkits.basemap import Basemap
from basemap1.basemap4.lib.mpl_toolkits.basemap import Basemap
import folium
import folium.plugins
from matplotlib import animation,rc
import io
import base64
from IPython.display import HTML, display
import warnings
warnings.filterwarnings('ignore')
from scipy.misc import imread
import codecs
from subprocess import check_output


# In[12]:


terror = pd.read_csv(r'D:\download from kangle\globalterrorismdb_0718dist.csv', encoding = 'ISO-8859-1')


# In[13]:


terror.head()


# In[14]:


terror.rename(columns={ 'iyear':'Year', 'imonth':'Month', 'iday':'Day', 'country_txt': 'Country', 'region_txt': 'Region','attacktype1_txt': 'AttackType','target1':'Target','nkill' : 'Killed', 'nwound':'Wounded','summary':'Summary','gname':'Group','targtype1_txt':'Target_type','weaptype1_txt':'Weapon_type','motive':'Motive'},inplace=True)
terror = terror[['Year','Month', 'Day', 'Country', 'Region','city','latitude','longitude','AttackType','Killed','Wounded','Target','Summary','Group','Target_type','Weapon_type','Motive']]
terror['casualities']=terror['Killed']+terror['Wounded']


# In[15]:


terror.head()


# # Find Null Values

# In[16]:


terror.isnull().sum()


# # Some Basic Analysis

# In[17]:


print('Country with Highest Terrorist Attacks:', terror['Country'].value_counts().index[0])
print('Regions with Highest Terrorist Attacks:', terror['Region'].value_counts().index[0])
print('Maximum people killed in an attack are:', terror['Killed'].max(),'that took place in ', terror.loc[terror['Killed'].idxmax()].Country)
print('Attack type use with Terrorists:', terror['AttackType'].value_counts().index[0])
print('Most time Terrorist Attacks on this :', terror['Target'].value_counts().index[0])


# # Number of Terrorist Activities Each Year

# In[18]:


plt.subplots(figsize=(16,8))
sns.countplot('Year', data=terror, palette='RdYlGn_r', edgecolor=sns.color_palette('dark',7))

plt.xticks(rotation=90)
plt.title('Number of Terrorist Activites Each Yeat')
plt.show()


# Clearly the number of terrorist activities have gone up after 2000.
# 
# 

# # Attacking Methods by Terrorists

# In[19]:


plt.subplots(figsize=(16,8))
sns.countplot('AttackType', data=terror, palette='inferno', order=terror['AttackType'].value_counts().index)
plt.xticks(rotation=90)
plt.title('Attacking Methods by Terrorists')
plt.show()


# # Favorite Targets

# In[20]:


plt.subplots(figsize=(15,6))
sns.countplot(terror['Target_type'], palette='inferno', order=terror['Target_type'].value_counts().index)
plt.xticks(rotation=90)
plt.title('Favorite Targets')
plt.show()


# # Global Terrorist Attacks

# In[21]:


m3 = Basemap(projection='mill',llcrnrlat=-80,urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c',lat_0=True,lat_1=True)
lat_100=list(terror[terror['casualities']>=75].latitude)
long_100=list(terror[terror['casualities']>=75].longitude)
x_100,y_100=m3(long_100,lat_100)
m3.plot(x_100, y_100,'go',markersize=5,color = 'r')
lat_=list(terror[terror['casualities']<75].latitude)
long_=list(terror[terror['casualities']<75].longitude)
x_,y_=m3(long_,lat_)
m3.plot(x_, y_,'go',markersize=2,color = 'b',alpha=0.4)
m3.drawcoastlines()
m3.drawcountries()
m3.fillcontinents(lake_color='aqua')
m3.drawmapboundary(fill_color='aqua')
fig=plt.gcf()
fig.set_size_inches(10,6)
plt.title('Global Terrorist Attacks')
plt.legend(loc='lower left',handles=[mpatches.Patch(color='b', label = "< 75 casualities"),
                    mpatches.Patch(color='red',label='> 75 casualities')])
plt.show()


# The above basemap shows the places of attacks. The red circles are those that had more than 75 casualities(Wounded+Killed). And blue circles are those that had less than 75 casualities. Lets make an interactive map with Folium and get more information for each location. 

# In[22]:


terror_fol=terror.copy()
terror_fol.dropna(subset=['latitude','longitude'],inplace=True)
location_fol=terror_fol[['latitude','longitude']][:5000]
country_fol=terror_fol['Country'][:5000]
city_fol=terror_fol['city'][:5000]
killed_fol=terror_fol['Killed'][:5000]
wound_fol=terror_fol['Wounded'][:5000]
def color_point(x):
    if x>=30:
        color='red'
    elif ((x>0 and x<30)):
        color='blue'
    else:
        color='green'
    return color   
def point_size(x):
    if (x>30 and x<100):
        size=2
    elif (x>=100 and x<500):
        size=8
    elif x>=500:
        size=16
    else:
        size=0.5
    return size   
map2 = folium.Map(location=[30,0],tiles='CartoDB dark_matter',zoom_start=2)
for point in location_fol.index:
    info='<b>Country: </b>'+str(country_fol[point])+'<br><b>City: </b>: '+str(city_fol[point])+'<br><b>Killed </b>: '+str(killed_fol[point])+'<br><b>Wounded</b> : '+str(wound_fol[point])
    iframe = folium.IFrame(html=info, width=200, height=200)
    folium.CircleMarker(list(location_fol.loc[point].values),popup=folium.Popup(iframe),radius=point_size(killed_fol[point]),color=color_point(killed_fol[point])).add_to(map2)
map2


# The color and size of each point is according to the number of people killed in the attack. Click on each point to get more information about attack.

# # Terrorist By Region

# In[23]:


plt.subplots(figsize = (15,7))
sns.countplot('Region', data = terror, palette = 'RdYlGn', edgecolor = sns.color_palette('dark',7), order = terror['Region'].value_counts().index)
plt.xticks(rotation = 90)
plt.title('Number of Terrorist Activities By Region')
plt.show()


# Middle East and North Africa are the most Terrorit prone regions followed by South Asia. The Australian Region have experienced very few terrorist events. Collectively we can say that, the African and Asian Continent experience the highest terrorist attacks. But why are these regions prone to terrorism? Dose this have any relation to the mindset of the people? or any other readon??

# # Trend in Terrorist Activities

# In[24]:


terror_region = pd.crosstab(terror.Year, terror.Region)
terror_region.plot(color = sns.color_palette('Set2',12))
fig = plt.gcf()
fig.set_size_inches(18,6)
plt.title('Trend in Terrorist Activities')
plt.show()


# As seen already, Middle-East, North African, South Asia have seen a shoot in the number of terrorist activities over the years.

# # Attack Type vS Region

# In[25]:


pd.crosstab(terror.Region, terror.AttackType).plot.barh(stacked = True, width = 1, color = sns.color_palette('RdYlGn',9))
fig = plt.gcf()
fig.set_size_inches(12,8)
plt.show()


# Armed Assault and Bombing, as seen above are the most prominet type of Attack irrespective of Regions.
# 

# # Terrorism By Country

# In[26]:


plt.subplots(figsize = (18,6))
sns.barplot(terror['Country'].value_counts()[:15].index, terror['Country'].value_counts()[:15].values,palette = 'inferno')
plt.title('Top Affected Countries')
plt.show()


# Iraq has witnessed a very large number of terrorist activites followed by Pakistan. One thing to note is the countries with highest attacks, are mostly densely populated countries, thus it will eventually claim many lives. Let's check

# # Attacks vs Killed

# In[27]:


coun_terror = terror['Country'].value_counts()[:15].to_frame()
coun_terror.columns = ['Attacks']
coun_kill = terror.groupby('Country')['Killed'].sum().to_frame()
coun_terror.merge(coun_kill, left_index = True, right_index = True, how = 'left').plot.bar(width = 0.9)
fig = plt.gcf()
fig.set_size_inches(18,6)
plt.show()


# Damm!! Look at the <b> Killed </b> bar for Iraq. The number of killed is almost 3 folds more than attacks for Iraq. Thus the densely populated theory holds good.

# # Most Notorious Groups
# 

# In[28]:


sns.barplot(terror['Group'].value_counts()[1:15].values, terror['Group'].value_counts()[1:15].index, palette = ('inferno'))
plt.xticks(rotation = 90)
fig = plt.gcf()
fig.set_size_inches(10,8)
plt.title('Terrorist Groups with Highest Terror Attacks')
plt.show()


# # Activity of Top Terrorist Groups

# In[29]:


top_groups10 = terror[terror['Group'].isin(terror['Group'].value_counts()[1:15].index)]
pd.crosstab(top_groups10.Year, top_groups10.Group).plot(color = sns.color_palette('Paired',10))
fig = plt.gcf()
fig.set_size_inches(18,6)
plt.show()


# The Irish Republican Army(IRA), is the oldest terrorist group started back in the 1960-1979, maybe after the World War 2 due to the mass killing. However, it has probably stopped its activities in the late 90's. some of the groups that have started lately in 2000's like the ISIL and Taliban, have shown a shoot in the number of attacks in the past years.

# 
# # Regions Attacked By Terrorist Groups

# In[30]:


top_groups=terror[terror['Group'].isin(terror['Group'].value_counts()[:14].index)]
m4 = Basemap(projection='mill',llcrnrlat=-80,urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c',lat_0=True,lat_1=True)
m4.drawcoastlines()
m4.drawcountries()
m4.fillcontinents(lake_color='aqua')
m4.drawmapboundary(fill_color='aqua')
fig=plt.gcf()
fig.set_size_inches(22,10)
colors=['r','g','b','y','#800000','#ff1100','#8202fa','#20fad9','#ff5733','#fa02c6',"#f99504",'#b3b6b7','#8e44ad','#1a2b3c']
group=list(top_groups['Group'].unique())
def group_point(group,color,label):
    lat_group=list(top_groups[top_groups['Group']==group].latitude)
    long_group=list(top_groups[top_groups['Group']==group].longitude)
    x_group,y_group=m4(long_group,lat_group)
    m4.plot(x_group,y_group,'go',markersize=3,color=j,label=i)
for i,j in zip(group,colors):
    group_point(i,j,i)
legend=plt.legend(loc='lower left',frameon=True,prop={'size':10})
frame=legend.get_frame()
frame.set_facecolor('white')
plt.title('Regional Activities of Terrorist Groups')
plt.show()


# The basemap clearly shows the regions of activity by the groups. ISIL is looks to be the notorious group in Iran and Iraq or boradly Middle-East. Similarly Taliban is concentrated in Afghanistan and Pakistan.<br>
# 
# The Unknown markers, are maybe due to be an individual attack due to any resentment or personal grudges or any non-famous groups.

# # Terrorist Activities in India

# In[31]:


terror_india = terror[terror['Country'] == 'India']
terror_india_fol = terror_india.copy()
terror_india_fol.dropna(subset = ['latitude', 'longitude'], inplace = True)
location_ind = terror_india_fol[['latitude', 'longitude']][:5000]
city_ind = terror_india_fol['city'][:5000]
killed_ind = terror_india_fol['Killed'][:5000]
wound_ind = terror_india_fol['Wounded'][:5000]
target_ind = terror_india_fol['Target_type'][:5000]

map4 = folium.Map(location = [20.60, 78.96], tiles = 'CartoDB dark_matter',zoom_start = 5.0)
for point in location_ind.index:
    folium.CircleMarker(list(location_ind.loc[point].values), popup = '<b> City: </b>' +str(city_ind[point])+ '<br><b> Killed: </b>' +str(killed_ind[point])+'<br><b> Injured: </b> '+str(wound_ind[point])+'<br><b> Target: </b>' +str(target_ind[point]), radius = point_size(killed_ind[point]), color = color_point(killed_ind[point]),fill_color = color_point(killed_ind[point])).add_to(map4)

map4


# Click on markers for more information.
# 

# # Most Notorious Groups in India and Favorite Attack Types

# In[32]:


f, ax = plt.subplots(1,2,figsize = (25,12))
ind_groups = terror_india['Group'].value_counts()[1:11].index
ind_groups = terror_india[terror_india['Group'].isin(ind_groups)]
sns.countplot(y = 'Group', data = ind_groups, ax = ax[0])
ax[0].set_title('Top Terrorist Groups')
sns.countplot(y = 'AttackType', data = terror_india, ax = ax[1])
ax[1].set_title('Favorite Attack Types')
plt.subplots_adjust(hspace = 0.3, wspace = 0.6)
ax[0].tick_params(labelsize = 15)
ax[1].tick_params(labelsize = 15)
plt.show()


# How did terrorism spread in india(Animation)

# In[33]:


fig = plt.figure(figsize = (10,8))
def animate(Year):
    ax = plt.axes()
    ax.clear()
    ax.set_title('Terrorism In India '+'\n'+'Year:' +str(Year))
    m5 = Basemap(projection='lcc',resolution='l',llcrnrlon=67,llcrnrlat=5,urcrnrlon=99,urcrnrlat=37,lat_0=28,lon_0=77)
    lat_gif=list(terror_india[terror_india['Year']==Year].latitude)
    long_gif=list(terror_india[terror_india['Year']==Year].longitude)
    x_gif,y_gif=m5(long_gif,lat_gif)
    m5.scatter(x_gif, y_gif,s=[killed+wounded for killed,wounded in zip(terror_india[terror_india['Year']==Year].Killed,terror_india[terror_india['Year']==Year].Wounded)],color = 'r')
    m5.drawcoastlines()
    m5.drawcountries()
    m5.fillcontinents(color='coral',lake_color='aqua', zorder = 1,alpha=0.4)
    m5.drawmapboundary(fill_color='aqua')
ani = animation.FuncAnimation(fig,animate,list(terror_india.Year.unique()), interval = 1500)    
ani.save('animation.gif', writer='imagemagick', fps=1)
plt.close(1)
filename = 'animation.gif'
video = io.open(filename, 'r+b').read()
encoded = base64.b64encode(video)
HTML(data='''<img src="data:image/gif;base64,{0}" type="gif" />'''.format(encoded.decode('ascii')))


# The size of the marker is relative to the number of people killed + wounded.<br>
# 
# The North-Eastern and the Northern part of India are the most terrorism prone areas. Jammu and Kashmir has witnessed highest attacks, and the numbers have gone up substantially since 1980's. The worst attack till date in India is the Mumbai Attack in 2006, which Killed more than 200 people.

# # Terror Activites in USA
# 

# In[34]:


terror_usa = terror[terror['Country'] == 'United States']
terror_usa_fol = terror_usa.copy()
terror_usa_fol.dropna(subset = ['latitude', 'longitude'], inplace = True)
location_usa = terror_usa_fol[['latitude', 'longitude']]
city_usa = terror_usa_fol['city']
killed_usa = terror_usa_fol['Killed']
wound_usa = terror_usa_fol['Wounded']
target_usa = terror_usa_fol['Target_type']

map5 = folium.Map(location = [39.50, -98.35], tiles = 'CartoDB dark_matter', zoom_start = 3.5)
for point in location_usa.index:
    info = '<b> City: </b>' +str(city_usa[point]) + '<br> <b> Killed: </b> '+str(killed_usa[point])+'<br> <b> Wounded: </b> ' + str(wound_usa[point])+ '<br> <b> Target</b> '+ str(target_usa[point])
    iframe = folium.IFrame(html = info, width = 200, height = 200)
    folium.CircleMarker(list(location_usa.loc[point].values),popup= folium.Popup(iframe), radius = point_size(killed_usa[point]), color= color_point(killed_usa[point])).add_to(map5)

map5


# # Most Notorious Groups in USA and Favorite Attack Type

# In[35]:


f, ax = plt.subplots(1,2, figsize = (25,12))
usa_groups = terror_usa['Group'].value_counts()[1:11].index
usa_groups = terror_usa[terror_usa['Group'].isin(usa_groups)]
sns.countplot(y= 'Group', data = usa_groups, ax = ax[0])
sns.countplot(y= 'AttackType', data = terror_usa, ax = ax[1])
plt.subplots_adjust(hspace = 0.3, wspace = 0.6)
ax[0].set_title('Top Terrorist Groups')
ax[1].set_title('Favorite Attack Types')
ax[0].tick_params(labelsize = 15)
ax[1].tick_params(labelsize = 15)
plt.show()


# # How did Terrorism Spread in USA(Animation)

# In[36]:


fig = plt.figure(figsize = (10,8))
def animate(Year):
    ax = plt.axes()
    ax.clear()
    ax.set_title('Terrorism In USA '+'\n'+'Year:' +str(Year))
    m6 = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
        projection='lcc',lat_1=33,lat_2=45,lon_0=-95)
    lat_gif1=list(terror_usa[terror_usa['Year']==Year].latitude)
    long_gif1=list(terror_usa[terror_usa['Year']==Year].longitude)
    x_gif1,y_gif1=m6(long_gif1,lat_gif1)
    m6.scatter(x_gif1, y_gif1,s=[killed+wounded for killed,wounded in zip(terror_usa[terror_usa['Year']==Year].Killed,terror_usa[terror_usa['Year']==Year].Wounded)],color ='r') 
    m6.drawcoastlines()
    m6.drawcountries()
    m6.fillcontinents(color='coral',lake_color='aqua', zorder = 1,alpha=0.4)
    m6.drawmapboundary(fill_color='aqua')
ani = animation.FuncAnimation(fig,animate,list(terror_usa.Year.unique()), interval = 1500)    
ani.save('animation.gif', writer='imagemagick', fps=1)
plt.close(1)
filename = 'animation.gif'
video = io.open(filename, 'r+b').read()
encoded = base64.b64encode(video)
HTML(data='''<img src="data:image/gif;base64,{0}" type="gif" />'''.format(encoded.decode('ascii')))


# USA doesn't witness many terror attacks as compared to India. There are very few attacks that have claimed a very large number of lives. Also the number of casusalities on an average is less as compared to that of India.<br>
# 
# It has however witnessed one of the worst terrorist attacks in 2001 in New-York, which killed more than 1500 people.

# # Terrorist Attacks in Pakistan

# In[40]:


terror_pak = terror[terror['Country'] == 'Pakistan']
terror_pak_fol = terror_pak.copy()
terror_pak_fol.dropna(subset = ['latitude','longitude'], inplace = True)
location_pak = terror_pak_fol[['latitude', 'longitude']]
city_pak = terror_pak_fol['city']
killed_pak = terror_pak_fol['Killed']
wound_pak = terror_pak_fol['Wounded']
target_pak = terror_pak_fol['Target_type']

map5 = folium.Map(location = [30.37,69.64], tiles = 'CartoDB dark_matter', zoom_start = 3.5)
for point in location_pak.index:
    info = '<b> City: </b>' + str(city_pak[point]) + '<br> <b> Killed: </b>' + str(killed_pak[point]) + '<br> <b> Wounded: </b>' +str(wound_pak[point]) + '<br> <b> Target: </b>'+str(target_pak[point])
    iframe = folium.IFrame(html = info, width = 200,height = 200)
    folium.CircleMarker(list(location_pak.loc[point].values),popup= folium.Popup(iframe),radius = point_size(killed_pak[point]),color = color_point(killed_pak[point])).add_to(map5)

map5


# # Most Notorious Groups in Pakistan and Favorite Attack Type

# In[38]:


f, ax = plt.subplots(1,2, figsize = (25,12))
pak_groups = terror_pak['Group'].value_counts()[1:11].index
pak_groups = terror_pak[terror_pak['Group'].isin(pak_groups)]
sns.countplot(y = 'Group', data = pak_groups, ax = ax[0])
sns.countplot(y = 'AttackType', data = terror_pak , ax = ax[1])
plt.subplots_adjust(hspace = 0.3, wspace = 0.6)
ax[0].set_title('Top Terrorist Group')
ax[1].set_title('Favorite Attack Types')
ax[0].tick_params(labelsize = 15)
ax[1].tick_params(labelsize = 15)
plt.show()


# # Terrorist Attacks in Afghanistan

# In[43]:


terror_afg = terror[terror['Country'] == 'Afghanistan']
terror_afg_fol = terror_afg.copy()
terror_afg_fol.dropna(subset = ['latitude','longitude'], inplace = True)
location_afg = terror_afg_fol[['latitude', 'longitude']]
city_afg = terror_afg_fol['city']
killed_afg = terror_afg_fol['Killed']
wound_afg = terror_afg_fol['Wounded']
target_afg = terror_afg_fol['Target_type']

map5 = folium.Map(location = [33.93,67.71], tiles = 'CartoDB dark_matter', zoom_start = 3.5)
for point in location_afg.index:
    info = '<b> City: </b>' + str(city_afg[point]) + '<br> <b> Killed: </b>' + str(killed_afg[point]) + '<br> <b> Wounded: </b>' +str(wound_afg[point]) + '<br> <b> Target: </b>'+str(target_afg[point])
    iframe = folium.IFrame(html = info, width = 200,height = 200)
    folium.CircleMarker(list(location_afg.loc[point].values),popup= folium.Popup(iframe),radius = point_size(killed_afg[point]),color = color_point(killed_afg[point])).add_to(map5)

map5


# # Most Notorious Groups in Afghanistan and Favorite Attack Type

# In[44]:


f, ax = plt.subplots(1,2, figsize = (25,12))
afg_groups = terror_afg['Group'].value_counts()[1:11].index
afg_groups = terror_afg[terror_afg['Group'].isin(afg_groups)]
sns.countplot(y = 'Group', data = afg_groups, ax = ax[0])
sns.countplot(y = 'AttackType', data = terror_afg , ax = ax[1])
plt.subplots_adjust(hspace = 0.3, wspace = 0.6)
ax[0].set_title('Top Terrorist Group')
ax[1].set_title('Favorite Attack Types')
ax[0].tick_params(labelsize = 15)
ax[1].tick_params(labelsize = 15)
plt.show()


# # World Terrorism Spread(Animation)

# In[41]:


fig = plt.figure(figsize = (10,6))
def animate(Year):
    ax = plt.axes()
    ax.clear()
    ax.set_title('Animation Of Terrorist Activities'+'\n'+'Year:' +str(Year))
    m6 = Basemap(projection='mill',llcrnrlat=-80,urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
    lat6=list(terror[terror['Year']==Year].latitude)
    long6=list(terror[terror['Year']==Year].longitude)
    x6,y6=m6(long6,lat6)
    m6.scatter(x6, y6,s=[(kill+wound)*0.1 for kill,wound in zip(terror[terror['Year']==Year].Killed,terror[terror['Year']==Year].Wounded)],color = 'r')
    m6.drawcoastlines()
    m6.drawcountries()
    m6.fillcontinents(zorder = 1,alpha=0.4)
    m6.drawmapboundary()
ani = animation.FuncAnimation(fig,animate,list(terror.Year.unique()), interval = 1500)    
ani.save('animation.gif', writer='imagemagick', fps=1)
plt.close(1)
filename = 'animation.gif'
video = io.open(filename, 'r+b').read()
encoded = base64.b64encode(video)
HTML(data='''<img src="data:image/gif;base64,{0}" type="gif" />'''.format(encoded.decode('ascii')))


# The size of the marker is relative to number of casualities(Killed+Wounded).
# 
# It is visible that the Middle-East and South-Asia are the regions with highest terrorist activites, not only in numbers, but also in casualities. It is spreading largely across the globe but in the past few tears, <b> India , Pakistan </b> and <b> Afghanistan</b> have witnessed an increase in such nubmer of activities.
# 
# 
# Lastly I Would like to thank all of you for having a look at this notebook.
# 
#     
#   

# In[ ]:





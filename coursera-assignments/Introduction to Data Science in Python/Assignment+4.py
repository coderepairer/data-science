
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[65]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[76]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[142]:


def get_list_of_university_towns():
  '''Returns a DataFrame of towns and the states they are in from the 
  university_towns.txt list. The format of the DataFrame should be:
  DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
  columns=["State", "RegionName"]  )
  
  The following cleaning needs to be done:

  1. For "State", removing characters from "[" to the end.
  2. For "RegionName", when applicable, removing every character from " (" to the end.
  3. Depending on how you read the data, you may need to remove newline character '\n'. '''
  import re
  
  def identify_states_regions(rec):
      global state
      region = None
      if bool(re.match(r'^[a-zA-Z\s]+$',rec)):
          state = rec
      else:
          region = re.sub("(\\(.*\\)?){0,}(\\[\d+]){0,}","",rec).rstrip()
          return [state,region]
  
  
  towns_df = pd.read_csv(
         "university_towns.txt", 
          delimiter="\[edit]",
          header=None,
          usecols=[0]
         )
  towns_df[0] = towns_df[0].apply(lambda x: identify_states_regions(x))
  towns_df.dropna(inplace=True)
  towns_df['State']=towns_df[0].apply(lambda x: x[0])
  towns_df['RegionName']=towns_df[0].apply(lambda x: x[1])
  towns_df.drop(0,axis=1,inplace=True)
  
  return towns_df


# In[68]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    gdplev_df = pd.read_excel(
           "gdplev.xls", 
            skiprows=219,
            names=['Quarter', 'GDP'],
            usecols=[4,5]
           )
    
    for i in range(2,len(gdplev_df)):
        if ((gdplev_df['GDP'][i-2] > gdplev_df['GDP'][i-1]) and (gdplev_df['GDP'][i-1] > gdplev_df['GDP'][i])):
            return gdplev_df['Quarter'][i-2]


# In[69]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    gdplev_df = pd.read_excel(
           "gdplev.xls", 
            skiprows=219,
            names=['Quarter', 'GDP'],
            usecols=[4,5]
           )
    
    start = get_recession_start()
    start_index = gdplev_df[gdplev_df['Quarter'] == start].index[0]
    
    for i in range(start_index+2,len(gdplev_df)):
        if ((gdplev_df['GDP'][i-2] < gdplev_df['GDP'][i-1]) and (gdplev_df['GDP'][i-1] < gdplev_df['GDP'][i])):
            return gdplev_df['Quarter'][i]


# In[70]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdplev_df = pd.read_excel(
           "gdplev.xls", 
            skiprows=219,
            names=['Quarter', 'GDP'],
            usecols=[4,5]
           )
    start = get_recession_start()
    start_index = gdplev_df[gdplev_df['Quarter'] == start].index[0]
    
    end = get_recession_end()
    end_index = gdplev_df[gdplev_df['Quarter'] == end].index[0]
    
    gdplev=gdplev_df.iloc[start_index:end_index+1]
    return gdplev[gdplev['GDP'] == gdplev['GDP'].min()]['Quarter'].values[0]


# In[82]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    def get_state_name(statecode):
        return states[statecode]

    homes_df = pd.read_csv(
           "City_Zhvi_AllHomes.csv", 
            converters = {2:get_state_name},
            index_col = ['State','RegionName'],
           )
    homes_df.drop(homes_df.columns[0:49],inplace=True,axis=1)


    for (i,j) in enumerate(homes_df.columns):
        year_col = j.split("-")
        new_year_col = year_col[0]
        
        if(year_col[1] in ('01','02','03')):
            new_year_col+='q1'            
            
        if(year_col[1] in ('04','05','06')): 
            new_year_col+='q2'
            
        if(year_col[1] in ('07','08','09')): 
            new_year_col+='q3'
            
        if(year_col[1] in ('10','11','12')): 
            new_year_col+='q4'
           
        homes_df.rename(columns = {j:new_year_col}, inplace = True)
        homes_df[new_year_col] = homes_df[[new_year_col]].mean(axis=1)

    homes_df = homes_df.loc[:,~homes_df.columns.duplicated()]
    return homes_df


# In[143]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    def cal_price_ratio(row):
        if(row[recession_start] >0):
            return (row[recession_start]-row[recession_bottom])/row[recession_start]
        else:
            return 0

    def is_uni(row):
        if (row['RegionName'] in uni_towns):
            return 1
        else:
            return 0
    
    def better():
        if uni_data.mean() < non_uni_data.mean():
            return "university town"
        else: 
            return "non-university town"
    
    
    def different():
        if p_val<0.01:
            return True
        else: 
            return False
        
    data = convert_housing_data_to_quarters().copy()
    recession_start = get_recession_start()
    recession_bottom = get_recession_bottom()

    data = data.loc[:,recession_start:recession_bottom]
    data = data.reset_index()
    data['price_ratio'] = data.apply(cal_price_ratio,axis=1)

    uni_towns = set(get_list_of_university_towns()['RegionName'])

    data['is_uni'] = data.apply(is_uni,axis=1)

    uni_data = data[data['is_uni'] ==1]['price_ratio'].dropna()
    non_uni_data = data[data['is_uni'] ==0]['price_ratio'].dropna()

    p_val = list(ttest_ind(uni_data, non_uni_data))[1]
  
    return (different(),p_val,better())


# In[ ]:




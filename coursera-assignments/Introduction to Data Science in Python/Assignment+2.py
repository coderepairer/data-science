
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.2** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# # Assignment 2 - Pandas Introduction
# All questions are weighted the same in this assignment.
# ## Part 1
# The following code loads the olympics dataset (olympics.csv), which was derrived from the Wikipedia entry on [All Time Olympic Games Medals](https://en.wikipedia.org/wiki/All-time_Olympic_Games_medal_table), and does some basic data cleaning. 
# 
# The columns are organized as # of Summer games, Summer medals, # of Winter games, Winter medals, total # number of games, total # of medals. Use this dataset to answer the questions below.

# In[170]:

import pandas as pd

df = pd.read_csv('olympics.csv', index_col=0, skiprows=1)

for col in df.columns:
    if col[:2]=='01':
        df.rename(columns={col:'Gold'+col[4:]}, inplace=True)
    if col[:2]=='02':
        df.rename(columns={col:'Silver'+col[4:]}, inplace=True)
    if col[:2]=='03':
        df.rename(columns={col:'Bronze'+col[4:]}, inplace=True)
    if col[:1]=='№':
        df.rename(columns={col:'#'+col[1:]}, inplace=True)

names_ids = df.index.str.split('\s\(') # split the index by '('

df.index = names_ids.str[0] # the [0] element is the country name (new index) 
df['ID'] = names_ids.str[1].str[:3] # the [1] element is the abbreviation or ID (take first 3 characters from that)

df = df.drop('Totals')
df.head()


# ### Question 0 (Example)
# 
# What is the first country in df?
# 
# *This function should return a Series.*

# In[171]:

# You should write your whole answer within the function provided. The autograder will call
# this function and compare the return value against the correct solution value
def answer_zero():
    # This function returns the row for Afghanistan, which is a Series object. The assignment
    # question description will tell you the general format the autograder is expecting
    return df.iloc[0]

# You can examine what your function returns by calling it in the cell. If you have questions
# about the assignment formats, check out the discussion forums for any FAQs
answer_zero() 


# ### Question 1
# Which country has won the most gold medals in summer games?
# 
# *This function should return a single string value.*

# In[175]:

def answer_one():
    return df['Gold'].sort_values(ascending=False).index[0]


# ### Question 2
# Which country had the biggest difference between their summer and winter gold medal counts?
# 
# *This function should return a single string value.*

# In[181]:

def answer_two():
    return abs(df['Gold']-df['Gold.1']).sort_values(ascending=False).index[0]


# ### Question 3
# Which country has the biggest difference between their summer gold medal counts and winter gold medal counts relative to their total gold medal count? 
# 
# $$\frac{Summer~Gold - Winter~Gold}{Total~Gold}$$
# 
# Only include countries that have won at least 1 gold in both summer and winter.
# 
# *This function should return a single string value.*

# In[255]:

def answer_three():
    df['Diff'] = abs(df['Gold']-df['Gold.1'])
    df['TotalGold'] = df['Gold']+df['Gold.1']    
    return (df['Diff']/df['TotalGold'])[(df['Gold']>=1) & (df['Gold.1'] >=1)].sort_values(ascending=False).index[0]


# ### Question 4
# Write a function that creates a Series called "Points" which is a weighted value where each gold medal (`Gold.2`) counts for 3 points, silver medals (`Silver.2`) for 2 points, and bronze medals (`Bronze.2`) for 1 point. The function should return only the column (a Series object) which you created, with the country names as indices.
# 
# *This function should return a Series named `Points` of length 146*

# In[193]:

def answer_four():
    df['Points'] = (df['Gold.2']*3)+(df['Silver.2']*2)+(df['Bronze.2']*1)
    points = pd.Series(df['Points'].values,index=df.index.values,name='Points')
    return points


# ## Part 2
# For the next set of questions, we will be using census data from the [United States Census Bureau](http://www.census.gov). Counties are political and geographic subdivisions of states in the United States. This dataset contains population data for counties and states in the US from 2010 to 2015. [See this document](https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2015/co-est2015-alldata.pdf) for a description of the variable names.
# 
# The census dataset (census.csv) should be loaded as census_df. Answer questions using this as appropriate.
# 
# ### Question 5
# Which state has the most counties in it? (hint: consider the sumlevel key carefully! You'll need this for future questions too...)
# 
# *This function should return a single string value.*

# In[195]:

import pandas as pd
census_df = pd.read_csv('census.csv')
census_df.head()


# In[202]:

def answer_five():      
     return census_df.groupby(['STNAME'])['CTYNAME'].count().sort_values(ascending=False).index[0]


# ### Question 6
# **Only looking at the three most populous counties for each state**, what are the three most populous states (in order of highest population to lowest population)? Use `CENSUS2010POP`.
# 
# *This function should return a list of string values.*

# In[58]:

def answer_six():
    #Finds 3 highmost census for each state
    temp_df = census_df[['STNAME','COUNTY','CENSUS2010POP']][census_df['COUNTY'] > 0].sort_values(['CENSUS2010POP'],ascending=False).groupby('STNAME').apply(lambda x: x.head(3))

    #Finds top 3 states with highest population
    most_pop_df = temp_df.groupby('STNAME').mean().sort_values(['CENSUS2010POP'],ascending=False).head(3)
    
    return list(most_pop_df.index.values)


# ### Question 7
# Which county has had the largest absolute change in population within the period 2010-2015? (Hint: population values are stored in columns POPESTIMATE2010 through POPESTIMATE2015, you need to consider all six columns.)
# 
# e.g. If County Population in the 5 year period is 100, 120, 80, 105, 100, 130, then its largest change in the period would be |130-80| = 50.
# 
# *This function should return a single string value.*

# In[257]:

def answer_seven():
    # Prepare Subset of Dataframe with POPESTIMATE columns
    pop_estimate_df = census_df[['CTYNAME','POPESTIMATE2010','POPESTIMATE2011','POPESTIMATE2012','POPESTIMATE2013','POPESTIMATE2014','POPESTIMATE2015']][census_df['COUNTY'] > 0]

    # Calculate Absolute change in POPESTIMATE2010 through POPESTIMATE2015
    pop_estimate_df['ABSPOPESTIMATE']=pop_estimate_df.max(axis=1)-pop_estimate_df.min(axis=1)
    
    return pop_estimate_df.sort_values(['ABSPOPESTIMATE'],ascending=False)['CTYNAME'].values[0]


# ### Question 8
# In this datafile, the United States is broken up into four regions using the "REGION" column. 
# 
# Create a query that finds the counties that belong to regions 1 or 2, whose name starts with 'Washington', and whose POPESTIMATE2015 was greater than their POPESTIMATE 2014.
# 
# *This function should return a 5x2 DataFrame with the columns = ['STNAME', 'CTYNAME'] and the same index ID as the census_df (sorted ascending by index).*

# In[206]:

def answer_eight():
    #Prepare Subset of Dataframe with columns of interest
    subset_df = census_df[['REGION','STNAME','CTYNAME','POPESTIMATE2014','POPESTIMATE2015']]
    
    #Conditions
    cond1 = subset_df['REGION'].isin([1,2])
    cond2 = subset_df['CTYNAME'].str.startswith('Washington')
    cond3 = subset_df['POPESTIMATE2015'] > subset_df['POPESTIMATE2014']
    
    output_df = subset_df[ cond1 & cond2 & cond3].head()
    
    return output_df[['STNAME','CTYNAME']]


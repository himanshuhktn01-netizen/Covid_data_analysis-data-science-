import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
confirm=pd.read_csv('covid_19_confirmed_v1.csv')
death= pd.read_csv('covid_19_deaths_v1.csv')
recover= pd.read_csv('covid_19_recovered_v1.csv')

i=confirm['5/29/21'].idxmax()
M=confirm.loc[i,'Province/State']
m=confirm.iloc[i,:1][0]#[0] is for only name otherwise other things will also show in output  




d=confirm.groupby('Country/Region').sum().iloc[:,3:]

tc=d.iloc[:,-1].nlargest(3).index

d_top=d.loc[tc].T.rolling(window=7).mean()
d_top.index=pd.to_datetime(d_top.index,format='%m/%d/%y')
# print(d_top)
# print(d_top.columns)
plt.figure(figsize=(12,12))
plt.plot(d_top.index,d_top.values,label=d_top.columns)
plt.xticks(rotation=90)
plt.legend(title='Country')
plt.title('Covid-19 confirmed cases in top 3 countries')
plt.xlabel('dates')
plt.ylabel('Cumilative confirmed cases')

# plt.show()


# plot for china confirmed cases  over time 
d_china=d.loc['China']
d_china.index=pd.to_datetime(d_china.index,format='%m/%d/%y')

plt.figure(figsize=(10,12))
plt.plot(d_china.index,d_china.values,label='china')
plt.legend(title='country')
plt.xticks(rotation=90)
plt.title('China cases over time')
plt.xlabel('Dates')
plt.ylabel('no. of cases')

# plt.show()


# Data cleaning
n_confirm=confirm.isnull().any().any()# it check if data has null or not and return true false 
n_death=death.isnull().any().any()
n_recover=recover.isnull().any().any()
# print(n_confirm,n_recover,n_death)

# Empty string can also be in data which will not count in null checking so need to check seperately

l=[confirm,death,recover]
for i in l:
    i.replace('',pd.NA,inplace=True)# this will change all empty string to null


# fill null
# ffill for time-series
# provience/state-"All proviences"or mode
# misssing value with moving avg


death.columns=death.iloc[0]
recover.columns=recover.iloc[0]
# row and column has same thing so first row need to be get remove 
death=death.iloc[1:].reset_index(drop=True)
recover=recover.iloc[1:].reset_index(drop=True)

# filling
categorical_data=['Province/State','Country/Region']# removed all the other colums in order to get only timeseries
non_time_series_number=['Lat','Long']
timeseries=confirm.columns.difference(categorical_data + non_time_series_number)

confirm[timeseries]=confirm[timeseries].fillna(method='ffill')
death[timeseries]=death[timeseries].fillna(method='ffill')
recover[timeseries]=recover[timeseries].fillna(method='ffill')

confirm[categorical_data]=confirm[categorical_data].fillna(confirm[categorical_data].mode().iloc[0])#iloc is here so that if multiple values of same occurence are there 
death[categorical_data]=death[categorical_data].fillna(confirm[categorical_data].mode().iloc[0])
recover[categorical_data]=recover[categorical_data].fillna(confirm[categorical_data].mode().iloc[0])



confirm[non_time_series_number]=confirm[non_time_series_number].fillna(confirm[non_time_series_number].rolling(window=5,min_periods=1,center=True).mean())
death[non_time_series_number]=death[non_time_series_number].fillna(confirm[non_time_series_number].rolling(window=5,min_periods=1,center=True).mean())
recover[non_time_series_number]=recover[non_time_series_number].fillna(confirm[non_time_series_number].rolling(window=5,min_periods=1,center=True).mean())
# checking if data is correct or not 
n_confirm=confirm.isnull().sum().sum()
n_death=death.isnull().sum().sum()
n_recover=recover.isnull().sum().sum()
print(n_confirm,n_recover,n_death)


#Graph for daily new cases in 3 country 
C=['Germany','France','Italy']

diff=d.diff(axis=1).fillna(0)

diff.columns=pd.to_datetime(diff.columns,format='%m/%d/%y')
new_case={}
for i in C:
    new_case[i]=diff.loc[i]
# print(new_case)
peak={}
for country,high in new_case.items():
    maxdate=high.idxmax()
    max=high.max()
    peak[country]=(maxdate.strftime('%Y-%m-%d'),int(max))# int and strftime is for removing timestamp and float from the output
# print(peak)

plt.figure(figsize=(10,10))

for i in C:
    plg=diff.loc[i]
    plt.plot(plg.index,plg.values,label=i)
plt.legend(title='country')
plt.xlabel('date')
plt.ylabel('daily new cases')
plt.title('Daily new cases of covid-19 in Germany,France,Italy')
plt.xticks(rotation=45)
# plt.show()



# Mortality rates in top 3 countries of confirmed cases 
# print(death.head(5))
c_t=['US','India','Brazil']
mortal={}
for c in c_t:
    death_data=death[death['Country/Region']==c].iloc[:,-1].sum(axis=0)# sum because i want number only
    confirm_data=confirm[confirm['Country/Region']==c].iloc[:,-1].sum(axis=0)
    mortality=int(death_data)*100/int(confirm_data)
    mortal[c]=mortality
# print(mortal)


# Recovery rate of australia and canada
co=['Canada','Australia']
# print(recover.loc[:,'12/31/20'])

cols = recover.columns[4:]#for conversting numerical string data into numeric form
recover[cols] = recover[cols].apply(pd.to_numeric, errors='coerce')
confirm[cols] = confirm[cols].apply(pd.to_numeric, errors='coerce')
death[cols] = death[cols].apply(pd.to_numeric, errors='coerce')

rc={}
for c in co:
    recover_data=recover[recover['Country/Region']==c].loc[:,'12/31/20'].sum(axis=0)
    confirm_r_data=confirm[confirm['Country/Region']==c].loc[:,'12/31/20'].sum(axis=0)

    recover_rate=(recover_data)/(confirm_r_data)
    rc[c]=recover_rate

# print(rc)



# DISTRIBUTION OF DEATH RATES (DEATH/CONFIRM)
# AMONG PROVIENCES IN CANADA
# PROVIENCES WITH HIGH AND LOW DEATHS RATE AS OF THE LATEST DATE 

# Canada data with required columns
canada_d_data=death[death['Country/Region']=='Canada'].drop(columns=['Country/Region','Long','Lat'])
canada_c_data=confirm[confirm['Country/Region']=='Canada'].drop(columns=['Country/Region','Long','Lat'])

#  group by with provience
canada_d_data=canada_d_data.groupby('Province/State').sum().iloc[:,-1]
canada_c_data=canada_c_data.groupby('Province/State').sum().iloc[:,-1]




# death_rate calculation
death_rate=pd.Series(0.0,index=canada_d_data.index)
death_rate[canada_c_data !=0]=canada_d_data.div(canada_c_data[canada_c_data!=0])
# print(death_rate)
# max min 
death_max=death_rate.idxmax()
death_min=death_rate.idxmin()

# print(f"highest rate of death in canada: {death_max} ({death_rate[death_max]:.2%})")
# print(f"highest rate of death in canada: {death_min} ({death_rate[death_min]:.2%})")


# graph
plt.figure(figsize=(10,12))
death_rate.plot(kind='bar',color='blue',alpha=0.7)#alpha decide the opacity of bars
plt.title(f"Death rate by provience in canada  ")
plt.xlabel('provience')
plt.ylabel('Death rate')
plt.xticks(rotation=45)

# plt.show()



# Merge
# merge the data and transform datasets (death,confirm and recover) on country/ region and date coulmns 
# to create comprehensive view of impact 

# will use 
# Melt-it will reshape data from wide format to long format

merge_c=confirm.melt(id_vars=['Province/State','Country/Region','Lat','Long'],
                    var_name='Date',
                    value_name='Confirm'
                      )
merge_d=death.melt(id_vars=['Province/State','Country/Region','Lat','Long'],
                    var_name='Date',
                    value_name='death'
                      )

merge_r=recover.melt(id_vars=['Province/State','Country/Region','Lat','Long'],
                    var_name='Date',
                    value_name='recover'
                      )
    
merge_c['Date']=pd.to_datetime(merge_c['Date'],format='%m/%d/%y')
merge_d['Date']=pd.to_datetime(merge_d['Date'],format='%m/%d/%y')
merge_r['Date']=pd.to_datetime(merge_r['Date'],format='%m/%d/%y')

# t=pd.concat([merge_c,merge_d,merge_r])
# merge is better than concat we will get clean data 
merge_c['Lat']=merge_c['Lat'].astype(str)
merge_c['Long']=merge_c['Long'].astype(str)

mer=pd.merge(merge_c,merge_d,on=['Province/State','Country/Region','Lat','Long','Date'],how='outer')
merge=pd.merge(mer,merge_r,on=['Province/State','Country/Region','Lat','Long','Date'],how='outer')
# print(merge)


# Analyze the montly sum of confirmed cases ,death and recovery to understand progression(from merged data)

g=merge[merge['Country/Region'].isin(['US','Italy','Brazil'])].groupby([merge['Country/Region'],merge['Date'].dt.to_period('M')]).max(numeric_only=True).reset_index()# .dt.to_period('M') this line is used to get month and year
# or
# g=merge[merge['Country/Region'].isin(['USA','Italy','Brazil'])].groupby(merge['Date'].dt.month)[['Confirm','death','recover']].sum()
# print(g)

# plot of the above data with seaborn

plt.figure(figsize=(12,16))
g['Date']=g['Date'].astype(str)

palette = {
    'US': 'red',
    'Italy': 'green',
    'Brazil': 'blue'
}



for i in ['Confirm','death','recover']:
    sns.lineplot(data=g,x='Date',y=i,hue='Country/Region',marker='o',linestyle='-',palette=palette)

plt.title('Monthly data of covid 19 ')
# plt.show()

# identify countries with highest average death rate 
mega_g=merge.groupby([merge['Country/Region'],merge['Date'].dt.to_period('M')]).max(numeric_only=True).reset_index()
av=(mega_g.groupby('Country/Region')['death'].sum()/mega_g.groupby('Country/Region')['Confirm'].sum()).sort_values(ascending=False).head(3)
# print(av)
plt.figure(figsize=(10,10))
av.plot(kind='bar',color='red')
# plt.show()

# identify countries with highest average recovery rate 
av_r=(mega_g.groupby('Country/Region')['recover'].sum()/mega_g.groupby('Country/Region')['Confirm'].sum()).sort_values(ascending=False).head(3)
# print(av_r)
plt.figure(figsize=(10,10))
av_r.plot(kind='bar',color='green')
# plt.show()


# Automation to find death and recovery for any country 

def retodea(countryname):
    tr=mega_g[mega_g['Country/Region']==countryname]['recover'].sum() 
    td=mega_g[mega_g['Country/Region']==countryname]['death'].sum() 
    plt.figure(figsize=(10,10))
    plt.bar(['Total recovery','Total death'],[tr,td],color=['green','red'])
    plt.title(f"total recovery vs total death of {countryname}")
    # plt.show()

retodea('South Africa')

# MONTH WISE RECOVERY RATIO OF A COUNTRY
def rectocof(country):
    tr=merge[merge['Country/Region']==country].groupby(merge['Date'].dt.to_period('M'))['recover'].sum()
    tc=merge[merge['Country/Region']==country].groupby(merge['Date'].dt.to_period('M'))['Confirm'].sum()

    rr=tr*100/tc
    plt.figure(figsize=(10,10))
    plt.plot(rr.index.astype(str),rr,marker='o',color='blue')
    plt.xticks(rotation=45)
    # plt.show()
rectocof('Canada')

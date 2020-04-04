#!/usr/bin/python3

import pandas as pd #Data manipulation
import numpy as np #Remove NaNs
import requests #Send HTTP requests and access response data
import json #Read JSON formatted date
import urllib #Fetch URLs
import sqlalchemy #Connect and  push data to sql db
from sqlalchemy import create_engine
import re #Extract characters from strings
from simple_salesforce import Salesforce #Querying Salesfroce
import datetime #Filtering dataframes by date
from datetime import datetime, timedelta

#Import config files
from config import API_User_Key, email, password, sf_username, sf_password, sf_security_token, dbuser, dbpwd, dbhost, dbport, dbname

#Generate api key for pardot 
url = 'https://pi.pardot.com/api/login/version/3'
api_key =  requests.post(url, data={'email':email,
                        'password':password,
                        'user_key':API_User_Key,
                        'format':'json'}).json()['api_key']

auth = "Pardot api_key={}, user_key={}".format(api_key,API_User_Key)

#Query Pardot 'Prospects'

#Pardot only allows retrieval of 200 records at a time. To retrieve all the records, the offset parameter is increased by 200 each time

i=0
prospects = pd.DataFrame()

prospect_url = "https://pi.pardot.com/api/prospect/version/3/do/query?output=bulk&format=json&sort_by=&src=&offset="+str(i)

while requests.get(prospect_url, headers={"Authorization": auth}).json()['result'] is not None:
    
    try:
        prospect_url = "https://pi.pardot.com/api/prospect/version/3/do/query?output=bulk&format=json&sort_by=&src=&offset="+str(i)
        data = pd.DataFrame.from_dict(requests.get(prospect_url, headers={"Authorization": auth}).json()['result']['prospect'])
        prospects = prospects.append(data,ignore_index=True)
    except TypeError:
        pass
    
    i=i+200

#Create a dataframe with personas and list ids
Persona = ["Dan","Claire","Lynn","Rey","Maya"]
ID = [104733,104731,104727,104749,104719]
List_Ids = pd.DataFrame(list(zip(Persona, ID)), 
            columns =['Persona', 'Id'])

#Query Pardto 'List Memberships' to get all people with in each persona customer segment
list_memberships = pd.DataFrame()

for index, row in List_Ids.iterrows():

    list_id = row['Id']

    i=0

    list_mem_url = "https://pi.pardot.com/api/listMembership/version/3/do/query?list_id={}&output=bulk&format=json&offset=".format(list_id) + str(i)

    while requests.get(list_mem_url, headers={"Authorization": auth}).json()['result'] is not None:

        try:
            list_mem_url = "https://pi.pardot.com/api/listMembership/version/3/do/query?list_id={}&output=bulk&format=json&offset=".format(list_id) + str(i)
            data = pd.DataFrame.from_dict(requests.get(list_mem_url, headers={"Authorization": auth}).json()['result']['list_membership'])
            list_memberships = list_memberships.append(data)


        except:
            pass

        i=i+200

#Merge list names (personas)
list_memberships = pd.merge(list_memberships,List_Ids,left_on='list_id',right_on='Id')

#Merge prospect fields (e.g., campaign)
prospects = prospects[['id','created_at','campaign','is_do_not_email','opted_out','crm_contact_fid','crm_lead_fid']]
list_memberships = pd.merge(list_memberships,prospects,left_on='prospect_id',right_on='id')

#Recode NaNs to 0
list_memberships['is_do_not_email'] = list_memberships['is_do_not_email'].replace(np.nan, 0)

#Rename dates colums
list_memberships.rename(columns = {'created_at_x':'join_date','created_at_y':'created_date','opted_out_x':'opted_out'}, inplace = True)

#Keep certain columns
list_memberships = list_memberships[['prospect_id','created_date','opted_out','campaign','is_do_not_email','Persona','join_date','crm_contact_fid','crm_lead_fid']]

#Recode values
list_memberships['opted_out'] = list_memberships['opted_out'].replace({False: 0,True:1})

#Traverse through prospects and extract the campaign name (third set of quotes)
campaigns =[]

for index, row in list_memberships.iterrows():
    campaigns.append(re.findall("'([^']*)'", str(row['campaign']))[2])
list_memberships['campaign'] = campaigns

#Remove unmailable prospects
list_memberships = list_memberships[list_memberships['is_do_not_email']==0]

#Subset dataframe and rename column
prospects = list_memberships[['prospect_id','created_date','opted_out','campaign','is_do_not_email','Persona','join_date']]
prospects.rename(columns = {'Persona':'persona'},inplace=True)

#Query Salesforce 'Engagements' object
sf = Salesforce(username=sf_username, password=sf_password, security_token=sf_security_token)
Engagements = pd.DataFrame(sf.query_all("SELECT Contact_18_Digit_Id__c,Date_of_Interaction__c,Type_Detail__c,Marketing_Interaction_Type__c,Lead_18_Digit_Id__c FROM Engagements__c WHERE Date_of_Interaction__c>2016-12-31")['records'])

#Remove attributes column
del Engagements['attributes']
#Rename columns
Engagements.rename(columns = {'Contact_18_Digit_Id__c':'Contact',
                            'Lead_18_Digit_Id__c':'Lead',
                            'Date_of_Interaction__c':'Date',
                            'Type_Detail__c':'Engagement',
                            'Marketing_Interaction_Type__c':'Engagement_Type'}, inplace = True)
#Reorder columns
Engagements = Engagements[['Contact', 'Lead', 'Date', 'Engagement', 'Engagement_Type']]

#Change 'None' values to np.nan
cols = ["Contact","Lead"]
Engagements[cols] = Engagements[cols].replace({'None':np.nan,None:np.nan})

#Query 'Working Groups' (other form of engagement stored in seperate Salesforce object)
WGMembers = pd.DataFrame(sf.query_all("SELECT Contact__c,Higher_Logic_Group__c FROM Higher_Logic_Group_Member__c WHERE Status__c='Active' AND Account_18_Digit_ID__c!='001o000000ivYo7AAE'")['records'])
del WGMembers['attributes']

#Retrieve group names from different Salesforce object
WorkingGroups = pd.DataFrame(sf.query_all("SELECT Higher_Logic_Group_18_Digit_ID__c,Name FROM Higher_Logic_Group__c")['records'])
del WorkingGroups['attributes']

#Associate group members with group name 
WGMembers = WGMembers.merge(WorkingGroups, left_on='Higher_Logic_Group__c',right_on='Higher_Logic_Group_18_Digit_ID__c')

del WGMembers['Higher_Logic_Group__c']
del WGMembers['Higher_Logic_Group_18_Digit_ID__c']

WGMembers.rename(columns = {'Contact__c':'Contact',
                            'Name':'Engagement'}, inplace = True)

#Add columns to match engagements table
WGMembers["Lead"] = np.nan
WGMembers["Date"] = np.nan
WGMembers["Engagement_Type"] = "Working Group"

WGMembers = WGMembers[['Contact', 'Lead', 'Date', 'Engagement', 'Engagement_Type']]

#Combine WG with engagements
Engagements = pd.concat([Engagements,WGMembers])

#Retrieve SETS events participants (other form of engagement)
SETSParticipants = pd.DataFrame(sf.query_all("SELECT Contact__c,Lead__c,SETS_Event__c FROM Event_Participant__c")['records'])
del SETSParticipants['attributes']
SETSParticipants.rename(columns = {'Contact__c':'Contact',
                            'Lead__c':'Lead'}, inplace = True)

#Remove events participants not tied to a Salesforce contact or lead
cols = ["Contact","Lead"]
SETSParticipants[cols] = SETSParticipants[cols].replace({None:np.nan,'None':np.nan})

#Retrieve names and dates for events
SETSEvents = pd.DataFrame(sf.query_all("SELECT SETS_Event_18_Digit_ID__c,Name,Start_Event_Date__c FROM SETS_Event__c")['records'])
del SETSEvents['attributes']
SETSEvents.rename(columns = {'Start_Event_Date__c':'Date','Name':'Engagement'}, inplace = True)

SETSParticipants = SETSParticipants.merge(SETSEvents, left_on='SETS_Event__c',right_on='SETS_Event_18_Digit_ID__c')
del SETSParticipants['SETS_Event__c']
del SETSParticipants['SETS_Event_18_Digit_ID__c']

SETSParticipants["Engagement_Type"] = "Event"
SETSParticipants = SETSParticipants[['Contact','Lead','Date','Engagement','Engagement_Type']]

#Remove test events
SETSParticipants = SETSParticipants[SETSParticipants["Engagement"] != 'Test Conference (Test0120) - January 2020']

#Combine with engagements
Engagements = pd.concat([Engagements,SETSParticipants])

#Change engagement type values
Engagements["Engagement_Type"].unique()
Engagements["Engagement_Type"] =Engagements["Engagement_Type"].replace({'Downloaded OnDemand Webinar':'Event',
                                                                        'Downloaded Publication':'Publication',
                                                                    'Event Attended':'Event'})

list_memberships[["crm_contact_fid","crm_contact_fid"]] = list_memberships[["crm_contact_fid","crm_contact_fid"]].replace({None:np.nan,'None':np.nan})

#If contact is blank replace with lead (create a single column of ids)
list_memberships.crm_contact_fid.fillna(list_memberships.crm_lead_fid, inplace=True)
Engagements.Contact.fillna(Engagements.Lead, inplace=True)

#Delete lead and rename contact to sf_id
del list_memberships['crm_lead_fid']
del Engagements['Lead']
list_memberships.rename(columns = {'crm_contact_fid':'sf_id'}, inplace = True)
Engagements.rename(columns = {'Contact':'sf_id'}, inplace = True)
id_match = list_memberships[['sf_id','prospect_id','Persona']]
Engagements = Engagements.merge(id_match, on='sf_id')
Engagements = Engagements[Engagements['prospect_id'].notna()]
del Engagements['sf_id']

#Final name changes
Engagements.rename(columns = {'Date':'engagement_date','Engagement':'engagement','Engagement_Type':'engagement_type','Persona':'persona'}, inplace = True)

#SQL DB CONNECTION
engine = create_engine(f"postgresql://{dbuser}:{dbpwd}@{dbhost}:{dbport}/{dbname}")
conn = engine.connect()

###Transform data so it is in a format that is ready to plot in js

##Population
#Calcualte the number of prospects is each persona
population = prospects.groupby(['persona']).size().reset_index()
population.rename(columns={0:'count'},inplace=True)
population.to_sql(name='population', if_exists='replace', con=conn, method='multi', chunksize=500, index=False)

##Pop Growth
pop_growth = prospects
pop_growth['count']=1
#Remove prospects created before before 2017
pop_growth.set_index("created_date", inplace = True)
pop_growth.index = pd.to_datetime(pop_growth.index)
pop_growth = pop_growth.loc['2017-01-01':datetime.today().strftime('%Y-%m-%d')]
#Count the number of prospects created for each persona by quarter
pop_growth = pd.DataFrame(pop_growth.groupby([pd.Grouper(freq='Q'), 'persona'])['count'].count().reset_index())
#Transpose data frame
pop_growth = pop_growth.pivot(index='persona', columns='created_date', values='count').reset_index()
#Remove last column (quarter is not complete yet)
pop_growth.drop(pop_growth.columns[len(pop_growth.columns)-1], axis=1, inplace=True)
pop_growth.columns = pop_growth.columns.astype(str)
pop_growth.to_sql(name='pop_growth', if_exists='replace', con=conn, method='multi', chunksize=500, index=False)

#Avg Engage 
avg_engage = Engagements
#Count number of engagements per prospect
avg_engage = avg_engage.groupby(['prospect_id','persona'])['engagement'].count().reset_index()
#Assign prsopects with no engagements a 0
no_engage = prospects[~prospects['prospect_id'].isin(Engagements['prospect_id'])]
no_engage['engagement'] = 0
no_engage = no_engage[['prospect_id','persona','engagement']]
avg_engage  = pd.concat([avg_engage,no_engage])
#Calculate mean engagements by persona
avg_engage = avg_engage.groupby(['persona'])['engagement'].mean().reset_index()
avg_engage.to_sql(name='avg_engage', if_exists='replace', con=conn, method='multi', chunksize=500, index=False)

#Engage Type
#Count the number of engagements persona groups have by category (e.g., event, working group)
engage_type = Engagements.groupby(['persona','engagement_type']).size().reset_index()
#Transpose data frame so engagements have own column
engage_type = engage_type.pivot(index='persona', columns='engagement_type', values=0).reset_index()
cols = ['Event', 'Publication', 'Working Group']
engage_type[cols] = engage_type[cols].div(engage_type[cols].sum(axis=1), axis=0).multiply(100)
engage_type.rename(columns={'Working Group':'WorkingGroup'}, inplace = True)
engage_type.to_sql(name='engage_type', if_exists='replace', con=conn, method='multi', chunksize=500, index=False)

#Top Items
#Remove nones
top_items = Engagements[Engagements['engagement'].notnull()]
top_items['engagement_date'] = pd.to_datetime(top_items['engagement_date'])
top_items.set_index('engagement_date', inplace=True)
#Remove engagements past 6 months ago
six_ago = (datetime.today() - timedelta(6*365/12))
top_items = top_items.loc[str(six_ago):str(datetime.today())]
top_items['count'] =1
#Sum the number of engagements with each item (e.g., utility conference, ev report)
item_count = top_items.groupby(['persona','engagement'])['count'].sum().reset_index()
top_items = item_count.groupby(['persona'])['count'].nlargest(5).reset_index()
top_items = top_items.merge(item_count, left_on='level_1',right_index=True)
top_items = top_items[['persona_y','engagement','count_y']]
top_items= top_items.rename(columns={'persona_y':'persona','count_y':'count'})
top_items.to_sql(name='top_items', if_exists='replace', con=conn, method='multi', chunksize=500, index=False)

#Top Campaigns
#Subset prospects created in the last 6 months
new_prospects = prospects.loc[str(six_ago):str(datetime.today())]
#Aggregate by persona and campaign
campaigns_count = pd.DataFrame({'count' : new_prospects.groupby([new_prospects['persona'], new_prospects['campaign']]).size()}).reset_index()
campaigns_count.sort_values(by=['count'], inplace=True, ascending=False)
#Remove outbound sources (spi)
outbounds = ['Created in Salesforce','SPI2019','Solar Power Northeast']
campaigns_count = campaigns_count[~campaigns_count['campaign'].isin(outbounds)]
#Get top 5 campaigns per persona
top_campaigns = pd.DataFrame({'count' : campaigns_count.groupby(campaigns_count['persona'])['count'].nlargest(5)}).reset_index()
top_campaigns = top_campaigns.merge(campaigns_count,left_on='level_1',right_on=None,right_index=True)
top_campaigns = top_campaigns[['persona_x','campaign','count_y']]
top_campaigns.rename(columns = {'persona_x':'persona','count_y':'count'}, inplace = True)
top_campaigns.to_sql(name='top_campaigns', if_exists='replace', con=conn, method='multi', chunksize=500, index=False)

#Recfreq (status of prospects (e.g., active, lost))
engagements = Engagements
#Calculate days since engagements
engagements['R'] = pd.Timestamp.now().normalize() - pd.to_datetime(engagements['engagement_date'])
engagements['R'] = engagements['R'].astype(str).apply(lambda x: x.split()[0])
engagements = engagements[engagements['R'] != "NaT"]
engagements['R'] = pd.to_numeric(engagements['R'])
engagements['F']=1
#Aggregate engagements, taking the sum of engagements and most recent engagement date for each prospect
recfreq = engagements.groupby(['prospect_id','persona']).agg({'F':'sum','R':'min'}).reset_index()
#Repeat process for prospects with no engagements
prospects2 = prospects
prospects2 = prospects2.reset_index()
prospects2['R'] = pd.Timestamp.now().normalize() - pd.to_datetime(prospects2['created_date'])
prospects2['R'] = prospects2['R'].astype(str).apply(lambda x: x.split()[0])
prospects2 = prospects2[prospects2['R'] != "NaT"]
prospects2['R'] = pd.to_numeric(prospects2['R'])
prospects2['F']=0
no_engage = prospects2[~prospects2['prospect_id'].isin(recfreq['prospect_id'])]
no_engage = no_engage[['prospect_id','persona','F','R']]
#Concatenate 0 engagement prospects
recfreq = pd.concat([recfreq,no_engage])
#Remove person with 1815 engagements
recfreq = recfreq[recfreq['F'] != 1814]
#Categorize prospects based on receny and frequency of engagements
recfreq['status']=''
recfreq.loc[((recfreq['F'] > 1) & (recfreq['R'] <= 180)),'status'] = 'Active'
recfreq.loc[((recfreq['F'] <= 1) & (recfreq['R'] <= 180)),'status'] = 'New'
recfreq.loc[((recfreq['R'] > 180) & (recfreq['R'] <= 365)),'status'] = 'Lapsed'
recfreq.loc[recfreq['R'] > 365,'status'] = 'Lost'
recfreq = recfreq.groupby(['persona','status']).size().reset_index()
recfreq = recfreq.pivot(index='persona', columns='status', values=0).reset_index()
cols = ['Active', 'Lapsed', 'Lost', 'New']
recfreq[cols] = recfreq[cols].div(recfreq[cols].sum(axis=1), axis=0).multiply(100)
recfreq.to_sql(name='recfreq', if_exists='replace', con=conn, method='multi', chunksize=500, index=False)
import streamlit as st
import msal
import requests
import pandas as pd
import datetime

def requestToken():
    tenantID = st.secrets['TENANT_ID']
    clientID = st.secrets['CLIENT_ID']
    clientSecret = st.secrets['CLIENT_SECRET']
    auth='https://login.microsoftonline.com/'+tenantID    
    scope = ['https://graph.microsoft.com/.default']
    client = msal.ConfidentialClientApplication(clientID, authority=auth, client_credential=clientSecret)
    token_result = client.acquire_token_silent(scope, account=None)
    if token_result:
        access_toke = 'Bearer ' + token_result['access_token']
        #print('loaded from cache')
        return access_toke
    if not token_result:
        token_result = client.acquire_token_for_client(scope)
        #print(token_result)
        access_toke = 'Bearer ' + token_result['access_token']
        #print('New access token acquired')
        return access_toke

def requestPantryData(token, df):
    siteID = st.secrets['SITE_ID']
    url = 'https://graph.microsoft.com/v1.0/sites/'+siteID+'/drive/root:/KnightsHarvestData.xlsx:/workbook/tables/PantryData/rows'
    headers ={'Authorization': token}
    response = requests.get(url, headers=headers)
    pantryData = response.json()
    row = pantryData['value']
    #print(len(value))
    #print(value)
    for entry in row:
        #print(entry['values'])
        #print(entry['values'][0])
        df.loc[len(df)] = entry['values'][0]
    return cleanPantryData(df)

def requestClosetData(token, df):
    siteID = st.secrets['SITE_ID']
    url = 'https://graph.microsoft.com/v1.0/sites/'+siteID+'/drive/root:/KnightsHarvestData.xlsx:/workbook/tables/ClosetData/rows'
    headers ={'Authorization': token}
    response = requests.get(url, headers=headers)
    closetData = response.json()
    row = closetData['value']
    #print(len(value))
    #print(value)
    for entry in row:
        #print(entry['values'])
        #print(entry['values'][0])
        df.loc[len(df)] = entry['values'][0]
    return cleanClosetData(df)

#@st.cache_data
def requestVisitorData(token, series):
    siteID = st.secrets['SITE_ID']
    url = 'https://graph.microsoft.com/v1.0/sites/'+siteID+'/drive/root:/KnightsHarvestData.xlsx:/workbook/tables/UniqueVisitors/rows'
    headers ={'Authorization': token}
    response = requests.get(url, headers=headers)
    visitorData = response.json()
    #print(visitorData)
    row = visitorData['value']
    for entry in row:
        #print(entry['values'])
        #print(entry['values'][0])
        series.loc[len(series)] = entry['values'][0][0]
    #print(visitors)
    return series

def requestOrderData(token, df):
    siteID = st.secrets['SITE_ID']
    url = 'https://graph.microsoft.com/v1.0/sites/'+siteID+'/drive/root:/KnightsHarvestData.xlsx:/workbook/tables/OrderData/rows'
    headers ={'Authorization': token}
    response = requests.get(url, headers=headers)
    orderData = response.json()
    row = orderData['value']
    for entry in row:
        df.loc[len(df)] = entry['values'][0]
    order = df['OrderDate']
    pickup = df['PickupDate']
    #df.drop(columns=['OrderDate', 'PickupDate'],inplace=True)
    newDate = []
    for num in order:
        newDate.append(toDate(num))
    df.drop(columns=['OrderDate'], inplace=True)
    df.insert(1, column='OrderDate', value=newDate)
    newDate.clear()
    for num in pickup:
        newDate.append(toDate(num))
    df.drop(columns=['PickupDate'], inplace=True)
    df.insert(3, column='PickupDate', value=newDate)
    return df
    

def toDate(serial):
    delta = datetime.datetime(1899,12,30) + datetime.timedelta(days=serial)
    return delta.date()

def pantryVisitors(df):
    date = datetime.date.today()
    startDate = datetime.date(date.year, date.month, 1)
    endDate = datetime.date(date.year, date.month+1, 1)
    filtered = df[(df['VisitDate'] >= startDate) & (df['VisitDate'] < endDate)]
    st.session_state['pantryVisits'] = filtered['VisitID'].count()
    st.session_state['pantryVisitors'] = filtered.value_counts('BellarmineID').count()

def closetVisitors(df):
    date = datetime.date.today()
    startDate = datetime.date(date.year, date.month, 1)
    endDate = datetime.date(date.year, date.month+1, 1)
    filtered = df[(df['VisitDate'] >= startDate) & (df['VisitDate'] < endDate)]
    st.session_state['closetVisits'] = filtered['VisitID'].count()
    st.session_state['closetVisitors'] = filtered.value_counts('BellarmineID').count()

def cleanPantryData(df):
    df.replace('', 0, inplace=True)
    #print(df)
    #df['BellarmineID'].astype(str)
    date = df['VisitDate']
    newDate = []
    for num in date:
        newDate.append(toDate(num))
    df.drop(columns=['VisitDate'],inplace=True)
    df.insert(1, column='VisitDate', value=newDate)
    pantryVisitors(df)
    st.session_state['newVisitors'] = pd.Series(df['BellarmineID'])
    df.drop(columns=['VisitorName', 'BellarmineID', 'ProduceTaken'], inplace=True)
    #print(df)
    return df.convert_dtypes()

def cleanClosetData(df):
    #df.replace('', 0, inplace=True)
    #print(df)
    
    #df['BellarmineID'].astype(str)
    date = df['VisitDate']
    newDate = []
    for num in date:
        newDate.append(toDate(num))
    df.drop(columns=['VisitDate'],inplace=True)
    df.insert(1, column='VisitDate', value=newDate)
    df['ItemsTaken'] = df['ItemsTaken'].str.extract(r'([a-zA-Z]+[a-zA-Z/ ]*)')
    closetVisitors(df)
    return df.drop(columns=['VisitorName', 'BellarmineID'])

if 'token' not in st.session_state:
    st.session_state['token'] = requestToken()

if 'pantryDf' not in st.session_state:
    colNames = {'VisitID':[], 'VisitDate':[], 'FirstTimeVisitor':[], 'VisitorName':[], 'BellarmineID':[], 'Num_ToFeed':[], 'Num_0-5':[],'Num_6-17':[], 'Num_18-59':[], 'Num_60Plus':[], 'ProduceTaken':[], 'Num_ProduceTaken':[], 'Veteran':[]}
    df = pd.DataFrame(data=colNames)
    st.session_state['pantryDf'] = requestPantryData(st.session_state['token'], df)

if 'closetDf' not in st.session_state:
    colNames = {'VisitID':[], 'VisitDate':[], 'VisitorName':[], 'BellarmineID':[], 'ClothingType':[], 'ItemsTaken':[],'TotalNumberTaken':[], 'ItemRequests':[]}
    df = pd.DataFrame(data=colNames)
    st.session_state['closetDf'] = requestClosetData(st.session_state['token'], df)

if 'orderData' not in st.session_state:
    colNames = {'OrderID':[], 'OrderDate':[], 'Poundage':[], 'PickupDate': []}
    df = pd.DataFrame(colNames)
    st.session_state['orderData'] = requestOrderData(st.session_state['token'], df)

if 'uniqueVisitors' not in st.session_state:
    series = pd.Series(dtype=str)
    st.session_state['uniqueVisitors'] = requestVisitorData(st.session_state['token'], series)

if 'allTimeVisitors' not in st.session_state:
    st.session_state['allTimeVisitors'] = pd.concat([st.session_state['newVisitors'],st.session_state['uniqueVisitors']], sort=False, ignore_index=True).value_counts().count()
    #print(st.session_state['allTimeVisitors'])

if 'pantryMetrics' not in st.session_state:
    colNames = {'Total # of People Served':[0], 'Total # Served 0-5':[0], 'Total # Served 6-17':[0], 'Total # Served 18-59':[0], 'Total # Served 60+':[0], 'Total # of Veterans Served':[0], 'Produce Only Total # Served':[0]}
    st.session_state['pantryMetrics'] = pd.DataFrame(colNames)
#if 'pantryVisitors' not in st.session_state:
    #st.session_state['pantryVisitors'] = pantryVisitors(st.session_state['pantryDf'])
#if 'closetVisitors' not in st.session_state:
    #st.session_state['closetVisitors'] = closetVisitors(st.session_state['closetDf'])

Homepage = st.Page('Dashboard.py', title='KnightsHarvest Dashboard', icon=":material/home:")
Pantry = st.Page('KnightsPantry.py', title='Knight\'s Pantry Data', icon=":material/restaurant:")
Closet = st.Page('KnightsCloset.py', title='Knight\'s Closet Data', icon=":material/checkroom:")
home = st.navigation([Homepage, Pantry, Closet])
home.run()
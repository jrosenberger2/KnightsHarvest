import streamlit as st
import datetime
import pandas as pd

def getMetrics(date, df):
    fresh = st.session_state['pantryMetrics']
    #fresh.drop(fresh.index, inplace=True)
    startDate = datetime.date(date.year, date.month, 1)
    endDate = datetime.date(date.year, date.month+1, 1)
    #print(df['VisitDate'].dtypes)
    #print(type(date))
    filtered = df[(df['VisitDate'] >= startDate) & (df['VisitDate'] < endDate)]
    #print(metrics)
    row = []
    row.append(filtered['Num_ToFeed'].sum())
    #row.append(filtered.value_counts('VisitorName'))
    row.append(filtered['Num_0-5'].sum())
    row.append(filtered['Num_6-17'].sum())
    row.append(filtered['Num_18-59'].sum())
    row.append(filtered['Num_60Plus'].sum())
    row.append(len(filtered[filtered['Veteran'] == 'Yes']))
    row.append(filtered['Num_ProduceTaken'].sum())
    fresh.loc[0] = row
    #print(fresh)
    #print(metrics['Num_ToFeed'].sum())
    #print(metrics['Num_0-5'].sum())
    #print(metrics['Num_6-17'].sum())
    #print(metrics['Num_18-59'].sum())
    #print(metrics['Num_60Plus'].sum())
    st.session_state['pantryMetrics'] = fresh

st.set_page_config(layout='wide')

st.header('Monthly Totals', divider='red')
date = st.date_input(label='Please Choose the Month you Would like Metrics for:', value=datetime.date(datetime.date.today().year, datetime.date.today().month,1), format='MM/DD/YYYY')
st.write('The following metrics are totalled from the date selected untill the 1st of the following month.')
getMetrics(date, st.session_state['pantryDf'])
st.dataframe(st.session_state['pantryMetrics'], hide_index=True)

st.container(height=50,border=False)

st.header('Knight\'s Pantry Data', divider='red')
st.dataframe(st.session_state['pantryDf'], hide_index=True)
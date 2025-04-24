import streamlit as st

st.set_page_config(layout='centered')
st.title('KnightsHarvest Dashboard')
st.write('This dashboard will function until 3/27/2027')

st.container(height=50,border=False)

st.header('Visitor Totals', divider='red')
col1, col2 = st.columns(2)

with col1:
    st.subheader('Knight\'s Pantry')
    st.write('- ' + str(st.session_state['pantryVisits']) +' Visits to Knight\'s Pantry this Month.')
    st.write('- ' + str(st.session_state['pantryVisitors']) +' Different People have Visited this Month.')
    st.write('- ' + str(st.session_state['allTimeVisitors']) + ' Unique all time Visitors')
    #1908
    #st.write('- 0000 All time Visitors')

with col2:
    st.subheader('Knight\'s Closet')
    st.write('- ' + str(st.session_state['closetVisits']) + ' Visits this Month')
    st.write('- ' + str(st.session_state['closetVisitors']) + ' Visitors this Month')
    #st.write('- 0000 All time Visitors')

st.container(height=50,border=False)

st.header('Order Data', divider='red')
st.dataframe(st.session_state['orderData'], hide_index=True)
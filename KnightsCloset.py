import streamlit as st

st.set_page_config(layout='wide')

st.header('Knight\'s Closet Data')
st.dataframe(st.session_state['closetDf'], hide_index=True)
import streamlit as st
   
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
   
with st.sidebar:
    st.write("SIDEBAR TEST")
    st.button("Test Button")
   
st.write("Main content")
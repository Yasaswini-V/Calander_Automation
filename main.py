import streamlit as st
st.set_page_config(
    page_title="MAPCalendar",
    layout="wide"
)
from conn import connect_local
import pandas as pd
from st_on_hover_tabs import on_hover_tabs
from Functions.Display import display
from Functions.Modify import update_entry
from Functions.Insert_table import load_table


con=connect_local()
my_cur=con.cursor()      
                    
def main():
    st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)
    with st.sidebar:
        tabs = on_hover_tabs(tabName=['Calendar List','Update Holiday','Update Country'], 
                            iconName=['🗓️', '✏️','✏️'], default_choice=0)
    if tabs =='Calendar List':
        display()
    elif tabs == 'Update Holiday':
        update_entry()
    elif tabs=='Update Country':
        load_table()
      
if __name__=="__main__":
    main()

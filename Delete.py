import streamlit as st
import pandas as pd
from conn import connect_local
from datetime import date

con=connect_local()
my_cur=con.cursor()

def delete(rows,df):
    for i in rows:
        delete_statement=f"DELETE FROM SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL WHERE COUNTRY_CD='{df['COUNTRY_CD'][i]}' AND CALENDAR_DATE='{df['CALENDAR_DATE'][i]}';"
        out=my_cur.execute(delete_statement)
    if out!="":
        st.success("Deleted")
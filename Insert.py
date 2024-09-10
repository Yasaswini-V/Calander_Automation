import streamlit as st
import pandas as pd
from conn import connect_local
from datetime import date
import datetime
import pytz

con=connect_local()
my_cur=con.cursor()

def insert(insert_rec):
    if len(insert_rec)>0:
        with st.spinner("Inserting...."):
            for index,row in insert_rec.iterrows():
                if len(row['CALENDAR_NAME'].strip())!=0 and len(row['COUNTRY_CD'].strip())!=0 and len(row['CALENDAR_EVENT'].strip())!=0:
                    value=row['CALENDAR_DATE'].strftime("%m/%d/%Y")
                    row['CALENDAR_NAME']=row['CALENDAR_NAME'].replace("'","''")
                    row['CALENDAR_EVENT']=row['CALENDAR_EVENT'].replace("'","''")
                    insert_statement=f"INSERT INTO IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL VALUES ('{row['CALENDAR_NAME'].capitalize()}','{row['COUNTRY_CD'].upper()}','{row['CALENDAR_EVENT'].capitalize()}','{value}','{datetime.datetime.now()}');"
                    my_cur.execute(insert_statement)
                else:
                    return False
            return True



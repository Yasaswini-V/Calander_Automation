import streamlit as st
from conn import connect_local
import datetime
import re
import pytz
import pandas as pd
from io import BytesIO
from io import StringIO
from dateutil.parser import parse
import chardet

con=connect_local()
my_cur=con.cursor()

def detect_encoding(file):
    raw_data = file.getvalue()
    result = chardet.detect(raw_data)
    return result['encoding']

def read_csv_file(uploaded_file):
    try:
        encoding = detect_encoding(uploaded_file)
        df = pd.read_csv(uploaded_file, encoding=encoding)
        return df
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None

def date_check(date_str):
    try:
        dt = pd.to_datetime(date_str)
        return dt.strftime('%m/%d/%Y')
    except Exception as e:
        st.error(f"The date {date_str} is not in DD-MM-YYYY format")
        return date_str

def call():
    @st.dialog("Upload Bulk",width="large")
    def upload():
        st.title('Upload Your File')
        uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = read_csv_file(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file,parse_dates=False, engine='openpyxl', dtype=str)
            
            if df is None:
                return
            
            df['CALENDAR_DATE'] = df['CALENDAR_DATE'].apply(date_check)
            
            st.dataframe(df)
            df.insert(4,'LAST_UPDATED_TIMESTAMP',datetime.datetime.now().replace(microsecond=0))
            
            if st.button("Insert"):
                with st.spinner("Inserting..."):
                    try:
                        for j in range(len(df)):
                            insert_statement='INSERT INTO SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL (CALENDAR_NAME,COUNTRY_CD,CALENDAR_EVENT,CALENDAR_DATE,LAST_UPDATED_TIMESTAMP) VALUES ('
                            count=0
                            for i in df.columns:
                                if i=='LAST_UPDATED_TIMESTAMP':
                                    date=str(df[i][j])
                                    insert_statement+=f"'{date}');"
                                    count+=1
                                else:
                                    if "'" in str(df[i][j]):
                                        value=str(df[i][j]).replace("'","''")
                                        insert_statement+=f"'{value}',"
                                        count+=1
                                    else:
                                        insert_statement+=f"'{str(df[i][j])}',"
                                        count+=1
                            if count==len(df.columns):
                                out=my_cur.execute(insert_statement)
                        st.success("Inserted...")
                    except Exception as e:
                        st.error(f"Error during insertion: {e}")
        else:
            st.info("Please upload a file.")
        
            
    upload()

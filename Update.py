import streamlit as st
import pandas as pd
from conn import connect_local
from datetime import date
import random
import datetime


con=connect_local()
my_cur=con.cursor()

def update(df):
    df=df.drop(["Delete"], axis=1)
    with st.spinner("Updating..."):
        my_cur.execute('''CREATE OR REPLACE TEMPORARY TABLE EG_DEV_WRKS_ENGR_DB.SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL_TEMP (CALENDAR_NAME VARCHAR(5000),
                                                                                                COUNTRY_CD VARCHAR(5000),
                                                                                                CALENDAR_EVENT VARCHAR(1000),
                                                                                                CALENDAR_DATE VARCHAR(500),
                                                                                                LAST_UPDATED_TIMESTAMP TIMESTAMP_NTZ(9));''')
        for ind,row in df.iterrows():
            statement=f"INSERT INTO EG_DEV_WRKS_ENGR_DB.SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL_TEMP VALUES("
            count=0
            for j in df.columns:
                if count<len(df.columns)-1:
                    count+=1
                    if "'" in row[j]:
                        text="''"
                        ind=row[j].index("'")
                        value=row[j][:ind] + text + row[j][ind+1:]
                        statement+=f"'{value}',"
                    else:
                        statement+=f"'{row[j]}',"

                else:
                    count+=1
                    statement+=f"'{datetime.datetime.now().replace(microsecond=0)}');"
                    my_cur.execute(statement)
            my_cur.execute('''MERGE INTO SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL USING (SELECT DISTINCT * FROM SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL_TEMP) AS TEMP
                        ON IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL.COUNTRY_CD = TEMP.COUNTRY_CD AND IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL.CALENDAR_DATE = TEMP.CALENDAR_DATE
                        WHEN MATCHED AND sha2_binary(IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL.CALENDAR_NAME||IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL.CALENDAR_EVENT) !=sha2_binary(TEMP.CALENDAR_NAME||TEMP.CALENDAR_EVENT) THEN
                            UPDATE SET
                    IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL.CALENDAR_NAME=TEMP.CALENDAR_NAME,IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL.CALENDAR_EVENT = TEMP.CALENDAR_EVENT,IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL.LAST_UPDATED_TIMESTAMP=TEMP.LAST_UPDATED_TIMESTAMP
                        WHEN NOT MATCHED THEN
                            INSERT (CALENDAR_NAME,COUNTRY_CD,CALENDAR_EVENT,CALENDAR_DATE,LAST_UPDATED_TIMESTAMP) VALUES (TEMP.CALENDAR_NAME,TEMP.COUNTRY_CD,TEMP.CALENDAR_EVENT,TEMP.CALENDAR_DATE,TEMP.LAST_UPDATED_TIMESTAMP);''')
        return True
    
import streamlit as st
import pandas as pd
from conn import connect_local
from Functions.Common_functions import get_df
import time
import datetime
from datetime import date
import random
import pytz

con=connect_local()
my_cur=con.cursor()


def insert(rec):
    out=[]
    rows=[]
    new_rec=rec.insert(6,'LAST_UPDATED_TIMESTAMP',datetime.datetime.now().replace(microsecond=0))
    if len(rec)>0:
        for index,row in rec.iterrows():
            rows.append(dict(row))
    with st.spinner("Inserting...."):
        for i in rows:
            insert_statement='INSERT INTO SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL VALUES ('
            for key,value in i.items():
                if value!="" and len(str(value).strip()) != 0:
                    if key=='CALENDER_FISCAL_START_YEAR':
                        if len(value)<4 or len(value)>4:
                            st.error("Please enter a valid year")
                        else:
                            insert_statement+=f"'{value}');"
                    elif key=='FISCAL_START_MONTH':
                        insert_statement+=f'{value},'
                    elif key=='LAST_UPDATED_TIMESTAMP':
                        insert_statement+=f"'{value}',"
                    elif key=='WEEKEND':
                        insert_statement+=f"'{value.capitalize()}',"
                    else:
                        insert_statement+=f"'{value.upper()}',"
                else:
                    return False
            try:
                out.append(my_cur.execute(insert_statement))
            except Exception as e:
                st.write(e)
        if len(out)>0:
            return True



def Update_table(df):
    with st.spinner("Updating..."):
        my_cur.execute('''CREATE OR REPLACE TEMPORARY TABLE EG_DEV_WRKS_ENGR_DB.SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL_TEMP (CALENDAR_DESC VARCHAR(5000),
                                                                                                                COUNTRY_DESC VARCHAR(5000),
                                                                                                                COUNTRY_CD VARCHAR(5000),
                                                                                                                FISCAL_START_MONTH NUMBER(2,0),
                                                                                                                FISCAL_YEAR_FLAG VARCHAR(2),
                                                                                                                WEEKEND VARCHAR(15),
                                                                                                                LAST_UPDATED_TIMESTAMP TIMESTAMP_NTZ(9),
                                                                                                                CALENDER_FISCAL_START_YEAR VARCHAR(16777216));''')
        for ind,row in df.iterrows():
            statement=f"INSERT INTO EG_DEV_WRKS_ENGR_DB.SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL_TEMP VALUES('{row['CALENDAR_DESC']}','{row['COUNTRY_DESC']}','{row['COUNTRY_CD']}','{row['FISCAL_START_MONTH']}','{row['FISCAL_YEAR_FLAG']}','{row['WEEKEND']}','{row['LAST_UPDATED_TIMESTAMP']}','{row['CALENDER_FISCAL_START_YEAR']}');"
            my_cur.execute(statement)
        my_cur.execute('''MERGE INTO SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL USING (SELECT DISTINCT * FROM SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL_TEMP) AS TEMP
                            ON SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.CALENDAR_DESC=TEMP.CALENDAR_DESC AND 
                            SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.COUNTRY_CD = TEMP.COUNTRY_CD
                            WHEN MATCHED AND sha2_binary(SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.COUNTRY_DESC||SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.FISCAL_START_MONTH||SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.FISCAL_YEAR_FLAG||SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.WEEKEND||SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.CALENDER_FISCAL_START_YEAR) !=sha2_binary(TEMP.COUNTRY_DESC||TEMP.FISCAL_START_MONTH||TEMP.FISCAL_YEAR_FLAG||TEMP.WEEKEND||TEMP.CALENDER_FISCAL_START_YEAR) THEN
                            UPDATE SET
                            IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.COUNTRY_DESC=TEMP.COUNTRY_DESC,
                            IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.FISCAL_START_MONTH=TEMP.FISCAL_START_MONTH,
                            IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.FISCAL_YEAR_FLAG=TEMP.FISCAL_YEAR_FLAG,
                            IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.WEEKEND=TEMP.WEEKEND,
                            IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL.CALENDER_FISCAL_START_YEAR=TEMP.CALENDER_FISCAL_START_YEAR
                            WHEN NOT MATCHED THEN INSERT (CALENDAR_DESC,COUNTRY_CD,COUNTRY_DESC,FISCAL_START_MONTH,FISCAL_YEAR_FLAG,WEEKEND,CALENDER_FISCAL_START_YEAR) VALUES (CALENDAR_DESC,COUNTRY_CD,COUNTRY_DESC,FISCAL_START_MONTH,FISCAL_YEAR_FLAG,WEEKEND,CALENDER_FISCAL_START_YEAR);''')
        return True

def update_value():
    st.session_state.new_df=random.randrange(100)

def count_val():
    st.session_state.toggle=True
    st.session_state.count+=1
def minus_val():
    st.session_state.count-=1

def load_table():
    st.title(":blue[UPDATE COUNTRY]")
    if 'toggle' not in st.session_state:
        st.session_state.toggle=False
    if 'count' not in st.session_state:
        st.session_state.count=0
    if 'new_df' not in st.session_state:
        st.session_state.new_df='old_df'
    df=get_df('DESC')
    changed_df=st.data_editor(df,column_config={
        "CALENDER_FISCAL_START_YEAR":"CALENDER FISCAL START YEAR",
        "CALENDAR_DESC":"CALENDAR DESC",
        "COUNTRY_CD":"COUNTRY CD",
        "FISCAL_START_MONTH":st.column_config.SelectboxColumn("FISCAL START MONTH",width='medium',options=[i for i in range(1,13)],required=True),
        "FISCAL_YEAR_FLAG":st.column_config.SelectboxColumn("FISCAL YEAR FLAG",options=[-1,0],required=True),
        "LAST_UPDATED_TIMESTAMP":None
    },disabled=['CALENDAR_DESC','COUNTRY_CD'],key=st.session_state.new_df,hide_index=True,use_container_width=True)
    col1,col2,_,col3,col4=st.columns([0.75,0.75,10,4,4])
    col1.button('➕',on_click=count_val)
    col2.button('➖',on_click=minus_val)
    if st.session_state.count==0:
        st.session_state.toggle=False

    if col3.button("Update"):
        Update_table(changed_df)


    new_row={}
    for i in df.columns:
        new_row[i]=[]
    if st.session_state.toggle:
        for i in new_row.keys():
            for j in range(st.session_state.count):
                new_row[i].append('')    
        new_row_df=pd.DataFrame(new_row)
        new_row_df=new_row_df.drop(['LAST_UPDATED_TIMESTAMP'], axis=1)
        insert_rec=st.data_editor(new_row_df,column_config={
        "CALENDER_FISCAL_START_YEAR":"CALENDER FISCAL START YEAR",
        "CALENDAR_DESC":"CALENDAR DESC",
        "COUNTRY_CD":"COUNTRY CD",
        "FISCAL_START_MONTH":st.column_config.SelectboxColumn("FISCAL START MONTH",width='medium',options=[i for i in range(1,13)],required=True),
        "FISCAL_YEAR_FLAG":st.column_config.SelectboxColumn("FISCAL YEAR FLAG",options=[-1,0],required=True)
    },use_container_width=True,hide_index=True,
    )
        if st.button('Insert'):
            st.session_state.count=0
            if insert(insert_rec):
                st.success("Inserted")
            else:
                st.info("You cant enter empty values")
            st.session_state.toggle=False
    col4.button('Refresh',on_click=update_value)

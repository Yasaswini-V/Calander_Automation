import streamlit as st
import pandas as pd
from conn import connect_local
from Functions.Insert import insert
from datetime import date
import datetime
import random
from Functions.Upload import call
from Functions.Delete import delete
from Functions.Update import update
from Functions.Generate_Calendar import gen_calendar
from Functions.Common_functions import filter_df,get_df,get_year
import time


con=connect_local()
my_cur=con.cursor()

def upload_button():
    st.session_state.upload=True

def convert_df(df):
    return df.to_csv().encode("utf-8")

def update_value():
    st.session_state.new_df=random.randrange(100)
    filter_df.clear()

def down_upload(df,download,upload,ref):
    download_dict={}
    for i in df.columns:
        download_dict[i]=""
    down_df=pd.DataFrame([download_dict]).set_index('CALENDAR_NAME')
    down_df.pop('LAST_UPDATED_TIMESTAMP')
    csv = convert_df(down_df)
    download.download_button(
        label="Bulk Upload Template",
        data=csv,
        file_name="Upload.csv",
        mime="text/csv",
    )
    ref.button("Refresh",on_click=update_value)
    upload.button('Upload',on_click=upload_button)
    if st.session_state.upload:
        call()
        st.session_state.upload=False
    else:
        return None

def update_gen():
    st.session_state.gen_ai=True

def count_val():
    st.session_state.toggle=True
    st.session_state.count+=1

def minus_val():
    st.session_state.count-=1

def update_entry():
    st.title(":blue[UPDATE HOLIDAYS]")
    if 'gen_ai' not in st.session_state:
        st.session_state.gen_ai=False
    if 'new_df' not in st.session_state:
        st.session_state.new_df='old_df'
    if 'toggle' not in st.session_state:
        st.session_state.toggle=False
    if 'count' not in st.session_state:
        st.session_state.count=0
    if 'upload' not in st.session_state:
        st.session_state.upload=False
    # if 'df' not in st.session_state:
    #     st.session_state.df=pd.DataFrame()
    if 'new_dict' not in st.session_state:
        st.session_state.new_dict={}

    df=get_df('COUNTRY')
    for i in df.columns:
        st.session_state.new_dict[i]=[]
    download,_,upload,ref=st.columns(4)
    down_upload(df,download,upload,ref)
    col1,col2=st.columns(2)
    
    country_cd=col1.multiselect("Select the country code:",options=df["COUNTRY_CD"].unique())
    with st.spinner("Loading data......."):
        if len(country_cd)==0:
            year_df=get_year(df)
            user_date=col2.multiselect("Select the year",options=year_df)
            new_df=filter_df(country_cd,user_date)
            new_df.insert(0, "Delete", False)
            edited_df=st.data_editor(new_df,column_config={"Delete": st.column_config.CheckboxColumn(required=True),"CALENDAR_EVENT":"CALENDAR EVENT","CALENDAR_NAME":"CALENDAR NAME"},disabled={"CALENDAR_DATE":"CALENDAR DATE","LAST_UPDATED_TIMESTAMP":"LAST UPDATED TIME STAMP","COUNTRY_CD":"COUNTRY CD"},use_container_width=True,hide_index=True,key=st.session_state.new_df)
        elif len(country_cd)>0:
            select_statement='SELECT * FROM IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL WHERE '
            for i in range(len(country_cd)):
                    if i==len(country_cd)-1:
                        select_statement+=f" COUNTRY_CD='{country_cd[i]}'"
                    else:
                        select_statement+=f" COUNTRY_CD='{country_cd[i]}' OR"
            fil_df=pd.DataFrame(my_cur.execute(select_statement),columns=['CALENDAR_NAME','COUNTRY_CD','CALENDAR_EVENT','CALENDAR_DATE','LAST_UPDATED_TIMESTAMP'])
            year_df=get_year(fil_df)
            user_date=col2.multiselect("Select The Year",options=year_df)
            new_df=filter_df(country_cd,user_date)
            new_df.insert(0, "Delete", False)
            edited_df=st.data_editor(new_df,column_config={"Delete": st.column_config.CheckboxColumn(required=True),"CALENDAR_EVENT":"CALENDAR EVENT","CALENDAR_NAME":"CALENDAR NAME"},disabled={"CALENDAR_DATE":"CALENDAR DATE","LAST_UPDATED_TIMESTAMP":"LAST UPDATED TIME STAMP","COUNTRY_CD":"COUNTRY CD"},use_container_width=True,hide_index=True,key=st.session_state.new_df)
        else:
            new_df.insert(0, "Delete", False)
            edited_df=st.data_editor(new_df,column_config={"Delete": st.column_config.CheckboxColumn(required=True),"CALENDAR_EVENT":"CALENDAR EVENT","CALENDAR_NAME":"CALENDAR NAME"},disabled={"CALENDAR_DATE":"CALENDAR DATE","LAST_UPDATED_TIMESTAMP":"LAST UPDATED TIME STAMP","COUNTRY_CD":"COUNTRY CD"},use_container_width=True,hide_index=True,key=st.session_state.new_df)

    st.warning("WARNING: COUNTRY_CD and CALENDAR_DATE cannot be modified, in case of updating kindly delete the existing entry then insert a new entry.")
    rows = edited_df[edited_df.Delete].index
    col1,col2,_,col3=st.columns([0.75,0.75,10,4])
    if len(rows)>0:
        if col3.button('Delete'):
            with st.spinner("Deleting..."):
                delete(rows,edited_df)
    else:
        if col3.button('Update'):
            if update(edited_df):
                st.success("Updated")
    col1.button('➕',on_click=count_val)
    col2.button('➖',on_click=minus_val)
    if st.session_state.count==0:
        st.session_state.toggle=False
    if st.session_state.toggle:
        for i in st.session_state.new_dict.keys():
            for j in range(st.session_state.count):
                    if i=='CALENDAR_DATE':
                        st.session_state.new_dict[i].append(date.today())
                    else:
                        st.session_state.new_dict[i].append('')    
        df=pd.DataFrame(st.session_state.new_dict)
        df=df.drop(["LAST_UPDATED_TIMESTAMP"], axis=1)
        df=st.data_editor(df,column_config={
        "CALENDAR_DATE": st.column_config.DateColumn(
            "CALENDAR_DATE",
            format="DD.MM.YYYY",
            step=1
        )
    },hide_index=True,use_container_width=True)
        if st.button('Insert'):
            st.session_state.count=0
            if insert(st.session_state.df):
                st.success("Inserted")
                st.session_state.toggle=False 
            else:
                st.error("Cannot insert empty values")
                st.session_state.toggle=False 
    st.button("Generate holiday by AI",on_click=update_gen)
    if st.session_state.gen_ai:
        gen_calendar()
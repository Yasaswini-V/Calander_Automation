import streamlit as st
from conn import connect_local
import pandas as pd


con=connect_local()
my_cur=con.cursor()      

@st.cache_data
def filter_df(country_cd,date):
    df=pd.DataFrame(my_cur.execute('SELECT * FROM SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL;'),columns=['CALENDAR_NAME','COUNTRY_CD','CALENDAR_EVENT','CALENDAR_DATE','LAST_UPDATED_TIMESTAMP'])
    new_df=list()
    final_df=pd.DataFrame()
    if len(country_cd)==0 and len(date)==0:
        return df
    
    elif len(country_cd)>0 and len(date)>0:
        for index in df.index:
            for i in country_cd:
                if i==df['COUNTRY_CD'][index] :
                    for j in date:
                        if df['CALENDAR_DATE'][index] is not None :
                            if j in df['CALENDAR_DATE'][index]:
                                new_df.append(df.iloc[index])
        final_df=pd.concat([final_df,pd.DataFrame(new_df)],ignore_index=True)
        return pd.DataFrame(final_df)
    
    elif len(country_cd)>0:
        for index in df.index:
            for i in country_cd:
                if i==df['COUNTRY_CD'][index]:
                    new_df.append(df.iloc[index])
        final_df=pd.concat([final_df,pd.DataFrame(new_df)],ignore_index=True)
        return pd.DataFrame(final_df)
    
    elif len(date)>0:
        for index in df.index:
            for i in date:
                if df['CALENDAR_DATE'][index] is not None:
                    if i in df['CALENDAR_DATE'][index]:
                        new_df.append(df.iloc[index])
        final_df=pd.concat([final_df,pd.DataFrame(new_df)],ignore_index=True)
        return final_df
    
def get_year(df):
    year=[]
    dd=mm=yy=""
    for i in df['CALENDAR_DATE']:
        if i is not None:
            dd,mm,yy=i.split('/')
            if yy not in year:
                year.append(yy)
            
    return year



def get_df(table_name):
    if table_name=='COUNTRY':
        return pd.DataFrame(my_cur.execute(f'SELECT * FROM SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_{table_name}_MANUAL;').fetch_pandas_all())
    else:
        return pd.DataFrame(my_cur.execute(f'SELECT * FROM SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL;').fetch_pandas_all())

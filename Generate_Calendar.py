import streamlit as st
import pandas as pd
import datetime
from conn import connect_local
from Functions.Common_functions import get_df
import time


conn=connect_local()
my_cur=conn.cursor()


def get_calendar_list(df,index):
    calendar_df=pd.DataFrame(my_cur.execute("SELECT * FROM SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL").fetch_pandas_all())
    calendar_list={}
    for i in calendar_df['COUNTRY_CD'].unique():
        calendar_list[i]=[]
    try:
        for i in index:
            for ind,row in calendar_df.iterrows():
                if row['COUNTRY_CD']==df['CALENDAR_DESC'][i]:
                    if row['CALENDAR_NAME'] not in calendar_list[row['COUNTRY_CD']]:
                        calendar_list[row['COUNTRY_CD']].append(row['CALENDAR_NAME'])
        return calendar_list
    except Exception as e:
        st.info(e)

def auto_gen_list(df,index):
    with st.spinner("Inserting..."):
        calendar_list=get_calendar_list(df,index)
        try:
            for i in index:
                insert_statement='INSERT INTO SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL VALUES('
                if len(calendar_list[df['CALENDAR_DESC'].loc[i]])>1:
                    insert_statement+=f"'{calendar_list[df['CALENDAR_DESC'].loc[i]][0]}',"
                elif len(calendar_list[df['CALENDAR_DESC'].loc[i]])==1:
                    insert_statement+=f"'{calendar_list[df['CALENDAR_DESC'].loc[i]]}'"
                name = df['NAME'].loc[i].replace("'", "''")
                insert_statement+=f"'{df['CALENDAR_DESC'].loc[i]}','{name}','{str((df['DATE'].loc[i]).strftime('%m/%d/%Y')).replace('-','/')}','{datetime.datetime.now().replace(microsecond=0)}');"
                try:
                    st.session_state.select=False
                    my_cur.execute(insert_statement)
                except Exception as e:
                    st.info(e)
                    return st.error("Falied to insert")
            return st.success("Inserted successfully....")
        except Exception as e:
            st.info(e)
            
  

@st.cache_data
def execute_query(query):
    return pd.DataFrame(my_cur.execute(query).fetch_pandas_all())

def update_session():
    st.session_state.select=True


def update_button(opt,selected_index=[]):
    if opt==True:
        st.session_state.df['Insert']=True
    else:
        for i in selected_index:
            st.session_state.df['Insert'][i] = False
        return st.session_state.df

def rerun():
    st.rerun()

def gen_calendar():
    if 'select' not in st.session_state:
        st.session_state.select=False
    if 'df' not in st.session_state:
        st.session_state.df=pd.DataFrame()
    if 'index' not in st.session_state:
        st.session_state.index=0

    final_df=list()
    country_df=get_df('DESC')
    country,year,_=st.columns(3)
    countries=list(country_df['CALENDAR_DESC'].sort_values())
    countries.remove('US')
    countries.insert(0,'US')
    country_desc=country.selectbox("Select a country",options=countries)
    gen_year=year.selectbox("Select a year to generate Calendar",options=(datetime.datetime.today().year+i for i in range(0,3)))
    query=f"""SELECT
                CAST(GET_PATH (value, 'name') AS TEXT) AS name,
                try_to_date(CAST(GET_PATH (value, 'date') AS TEXT),'dd-mm-yyyy') AS date,
                CAST(GET_PATH (value, 'country') AS TEXT) AS country,
                calendar_desc,
                js
                FROM
                (
                select SNOWFLAKE.CORTEX.complete('llama3-8b', concat('generate {gen_year} holiday for given holiday events ',h.ls,' for country',C.COUNTRY_DESC,''' in json format 
                {{
                "holidays": [
                {{
                "name": "< as per holiday events given >",
                "date": "01-01-2025",
                "country":"<Country name >"
                }}
                ]
                }}
                holiday name and date in (dd-mm-yyyy) and properly enclose all date values in double quotes ''')) as ai,replace(ai,'\n','') as aii,regexp_instr( aii, '{{') AS sp,replace(aii,substr(aii,0,sp-1),'') as fh ,
                regexp_instr( fh, '}}',1,regexp_count(fh,'}}')) as lp , try_parse_json(substr(fh,0,lp)) as  json  ,calendar_desc,substr(fh,0,lp) as js
                from SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL as c left join (select concat('(''',listagg(distinct calendar_event,''','''),''')') as ls,country_cd from  SHARED_COMMON.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL  where  country_cd in (select distinct calendar_desc from SHARED_COMMON.IA_CALENDAR_COUNTRIES_WITH_DESC_MANUAL) and year(to_date(calendar_date,'mm/dd/yyyy'))=2024 and calendar_event<>'Historic Holiday' group by country_cd ) h on h.country_cd=c.calendar_desc where calendar_desc <>'ROW'
                ),
                LATERAL FLATTEN (input => GET_PATH (json, 'holidays')) AS _flattened (SEQ, KEY, PATH, INDEX, VALUE, THIS);"""
    try:
        calendar_df_1=execute_query(query)
    except Exception as e:
        st.info(e)
    calendar_df=calendar_df_1.drop(['JS'], axis=1)
    final_df=calendar_df[calendar_df.CALENDAR_DESC==country_desc]
    columns=final_df.columns
    st.session_state.df=pd.DataFrame(final_df)
    st.session_state.df.insert(0,'Insert',False)

    temp_container = st.empty()
    st.session_state.df=temp_container.data_editor(st.session_state.df,column_config={"Insert": st.column_config.CheckboxColumn("Insert", required=True)},hide_index=True,use_container_width=True)
    selected_index = st.session_state.df[st.session_state.df.Insert].index.tolist()
    
    sel,select_all, res = st.columns(3)

    if sel.button("Insert Selected"):
        if len(selected_index):
            auto_gen_list(st.session_state.df, selected_index)
        else:
            st.warning("No rows selected")

    # select_all.button("Select All",on_click=update_session)
    # if st.session_state.select:
    #     update_button(True,selected_index)
    #     st.info("Selected all, Click insert to insert the data")
    #     temp_container.empty() 
    #     temp_container.data_editor(st.session_state.df,column_config={"Insert":st.column_config.CheckboxColumn("Insert",required=True)},hide_index=True,use_container_width=True,disabled=columns,key='Select all')
    #     selected_index=list(st.session_state.df[st.session_state.df.Insert].index)
    #     if st.button("Insert",key="Insert"):
    #         auto_gen_list(st.session_state.df,selected_index)


    # if res.button("Reset"):
    #     st.session_state.select = False
    #     update_button(False,selected_index)
    #     selected_index.clear()
    #     temp_container.empty() 
    #     temp_container.data_editor(st.session_state.df,column_config={"Insert": st.column_config.CheckboxColumn("Insert", required=True)},hide_index=True,use_container_width=True,key='Reset',disabled=columns)
    #     # rerun()
    
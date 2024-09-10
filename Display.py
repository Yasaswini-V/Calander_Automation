import streamlit as st
from streamlit_calendar import calendar 
import pandas as pd
from conn import connect_local
import json
from Functions.Common_functions import filter_df,get_year,get_df

conn=connect_local()

def display():
    # st.write(st.session_state)
    icon,title_col=st.columns([2,10])
    title_col.title(":blue[MAPCalendar]")
    with icon:
        st.write("")
        st.image('icons/App_Icon.png')
    try:
        df =pd.DataFrame(conn.cursor().execute("select * from eg_dev_wrks_engr_db.shared_common.calender_ui_json;").fetch_pandas_all())
        calendar_list=list(df['COUNTRY_DESC'].unique())
        calendar_list.remove('UNITED STATES')
        calendar_list.insert(0,'UNITED STATES')
        s1=st.selectbox('Country',calendar_list)#COUNTRY_DESC
        df2=df[df.COUNTRY_DESC==s1] #COUNTRY_DESC
        calendar_options = {
            "editable": "false",
            "selectable": "true",
            #,
            "initialView" :"multiMonthYear",
            ''
            "multiMonthMaxColumns " : "3",
            "multiMonthMinWidth" : "10"
        }

        calendar_events = json.loads("["+ df2['JS'].values[0]+"]")
        custom_css="""
            .fc-event-past {
                opacity: 0.8;
            }
            .fc-event-time {
                font-style: italic;
            }
            .fc-event-title {
                font-weight: 700;
            }
            .fc-toolbar-title {
                font-size: 2rem;
            }
        """
        calendar_df = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)
    except Exception as e:
        st.info(e)
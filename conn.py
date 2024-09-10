import streamlit as st
import snowflake.connector

@st.cache_resource(ttl=8600,show_spinner=False)
def connect_local():
  #st.text ('Local connect')
  conn = snowflake.connector.connect(
    account='ecolab.east-us-2.azure',
    user='YASASWINI.V@ECOLAB.COM',
    warehouse='EG_DEV_SVC_ETL_HRMY_WH',
    role='EG_DEV_ENGR_HRMY_FR',
    database='EG_DEV_WRKS_ENGR_DB',
    schema='SHARED_COMMON',
    authenticator='externalbrowser',
    client_session_keep_alive = 'true'
    )
  return conn;
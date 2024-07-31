import streamlit as st
import snowflake.connector

@st.cache_resource(ttl=8600,show_spinner=False)
def connect_local():
  #st.text ('Local connect')
  conn = snowflake.connector.connect(
    account='ecolab.east-us-2.azure',
    user='YASASWINI.V@ECOLAB.COM',
    warehouse='EG_TST_SVC_ETL_HRMY_WH',
    role='EG_TST_ENGR_HRMY_FR',
    database='EG_TST_PREP_DB',
    schema='INTEGRATION',
    authenticator='externalbrowser',
    client_session_keep_alive = 'true'
    )
  return conn;
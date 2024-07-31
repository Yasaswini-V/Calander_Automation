import streamlit as st
import pandas as pd
from io import BytesIO


uploaded_files = st.file_uploader(
    "Choose a CSV file", accept_multiple_files=True
)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    df = pd.read_csv(BytesIO(bytes_data))
    st.write("filename:", uploaded_file.name)
    # df=pd.DataFrame(bytes_data)
    st.dataframe(df)
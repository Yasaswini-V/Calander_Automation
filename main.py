import streamlit as st
st.set_page_config(
    page_title="Calendar Automation",
    layout="wide"
)
from conn import connect_local
import pandas as pd
from st_on_hover_tabs import on_hover_tabs



con=connect_local()
my_cur=con.cursor()

def Get_rows(df):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Delete", False)
    df_with_selections.pop('DEACTIVATE')
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Delete": st.column_config.CheckboxColumn(required=True),"ID": None,"PROJECT_NAME":"PROJECT NAME","OBJECT_MODIFIED":"OBJECT MODIFIED","OBJECT_IMPACTED":"OBJECT IMPACTED","UAT_ENV":"UAT ENV","UAT_TIMELINE":"UAT TIMELINE","DEPLOYMENT_DATE":"DEPLOYMENT DATE","GRAIN_CHANGED":"GRAIN CHANGED","PRIMARY_CONTACT":"PRIMARY CONTACT","INSERTED_ON":"INSERTED ON","UPDATED_ON":"UPDATED ON","DEACTIVATE":None},
        disabled=df.columns,
    )
    rows = edited_df[edited_df.Delete].index
    return rows

def convert_df(df):
    return df.to_csv().encode("utf-8")

def filter_df(country_cd,date):
    df=pd.DataFrame(my_cur.execute('SELECT * FROM EG_TST_PREP_DB.INTEGRATION.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL;'),columns=['CALENDAR_NAME','COUNTRY_CD','CALENDAR_EVENT','CALENDAR_DATE','LAST_UPDATED_TIMESTAMP'])
    new_df=list()
    final_df=pd.DataFrame()
    if len(country_cd)==0 and len(date)==0:
        return df
    
    elif len(country_cd)>0 and len(date)>0:
        for index in df.index:
            for i in country_cd:
                if i==df['COUNTRY_CD'][index] :
                    for j in date:
                        if j==df['CALENDAR_DATE'][index]:
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
                if i==df['CALENDAR_DATE'][index]:
                    new_df.append(df.iloc[index])
        final_df=pd.concat([final_df,pd.DataFrame(new_df)],ignore_index=True)
        return final_df

def changed_df(df_old,df):
    changed_rows = []
    # count=0
    st.dataframe(df_old)
    st.dataframe(df)
    for index,row in df.iterrows():
        row=dict(row)
        for i in row.keys():
            if row[i]!= df_old.loc[index][i]:
                changed_rows.append({i:row[i]})
    return changed_rows
                # count+=1

    # count=0

def display():
    col1,col2=st.columns(2)
    df=pd.DataFrame(my_cur.execute('SELECT * FROM EG_TST_PREP_DB.INTEGRATION.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL;'),columns=['CALENDAR_NAME','COUNTRY_CD','CALENDAR_EVENT','CALENDAR_DATE','LAST_UPDATED_TIMESTAMP'])
    country_cd=col1.multiselect("Select the Country Code",options=df['COUNTRY_CD'].unique())
    if len(country_cd)>0:
        select_statement='SELECT * FROM EG_TST_PREP_DB.INTEGRATION.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL WHERE '
        for i in range(len(country_cd)):
                if i==len(country_cd)-1:
                    select_statement+=f" COUNTRY_CD='{country_cd[i]}'"
                else:
                    select_statement+=f" COUNTRY_CD='{country_cd[i]}' OR"
        fil_df=pd.DataFrame(my_cur.execute(select_statement),columns=['CALENDAR_NAME','COUNTRY_CD','CALENDAR_EVENT','CALENDAR_DATE','LAST_UPDATED_TIMESTAMP'])
        date=col2.multiselect("Select The Year",options=fil_df['CALENDAR_DATE'].unique())
        new_df=filter_df(country_cd,date)
        st.dataframe(new_df,hide_index=True)
    else:
        st.dataframe(df,hide_index=True)

def count_val():
    st.session_state.toggle=True
    st.session_state.count+=1

def update_entry():
    if 'toggle' not in st.session_state:
        st.session_state.toggle=False
    if 'count' not in st.session_state:
        st.session_state.count=0
    _,_,download=st.columns(3)
    download_dict={}
    df_old=pd.DataFrame(my_cur.execute('SELECT * FROM EG_TST_PREP_DB.INTEGRATION.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL;'),columns=['CALENDAR_NAME','COUNTRY_CD','CALENDAR_EVENT','CALENDAR_DATE','LAST_UPDATED_TIMESTAMP'])
    for i in df_old.columns:
        download_dict[i]=""
    df=pd.DataFrame([download_dict])
    csv = convert_df(df)

    st.download_button(
        label="Download File as CSV",
        data=csv,
        file_name="Upload.csv",
        mime="text/csv",
    )
    df_old.insert(0, "Delete", False)
    df=st.data_editor(df_old,column_config={"Delete": st.column_config.CheckboxColumn(required=True)},hide_index=True)
    rows = df[df.Delete].index
    col1,col2=st.columns(2)
    if len(rows)>0:
        if col2.button('Delete'):
            for i in rows:
                delete_statement=f"DELETE FROM EG_TST_PREP_DB.INTEGRATION.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL WHERE COUNTRY_CD='{df['COUNTRY_CD'][i]}' AND CALENDAR_DATE='{df['CALENDAR_DATE'][i]}';"
                my_cur.execute(delete_statement)
    else:
        if col2.button('Update'):
            changed=changed_df(df_old,df)
            if len(changed)>0:
                for i in changed:
                    st.write(i)
                    update_statement=f"UPDATE TABLE EG_TST_PREP_DB.INTEGRATION.IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL SET WHERE COUNTRY_CD='{df['COUNTRY_CD'][i]}' AND CALENDAR_DATE='{df['CALENDAR_DATE'][i]}' "
                    my_cur.execute(update_statement)
    col1.button('➕',on_click=count_val)
    new_row={}
    for i in df_old.columns:
        new_row[i]=[]
    if st.session_state.toggle:
        rows=[]
        for i in new_row.keys():
            for j in range(st.session_state.count):
                new_row[i].append('')    
        new_row_df=pd.DataFrame(new_row)
        new_row_df.pop("Delete")
        insert_rec=st.data_editor(new_row_df)
        if st.button('insert'):
            st.session_state.count=0
            count=0
            if len(insert_rec)>0:
                for index,row in insert_rec.iterrows():
                    rows.append(dict(row))
            with st.spinner("Inserting...."):
                for i in rows:
                    insert_statement='INSERT INTO IA_CALENDAR_HOLIDAYS_BY_COUNTRY_MANUAL VALUES ('
                    for key,value in i.items():
                        if len(value)>0:
                            count+=1
                            if count<len(i.keys()):
                                insert_statement+=f"'{value}',"
                            else:
                                insert_statement+=f"'{value}');"
                                count=0
                                try:
                                    my_cur.execute(insert_statement)
                                    st.session_state.toggle=False
                                except Exception as e:
                                    st.write(e)
        
                    
def main():
    st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)
    with st.sidebar:
        tabs = on_hover_tabs(tabName=['Calendar List','Update Entry'], 
                            iconName=['economy', 'economy'], default_choice=0)
    if tabs =='Calendar List':
        display()
    elif tabs == 'Update Entry':
        update_entry()
      
if __name__=="__main__":
    main()

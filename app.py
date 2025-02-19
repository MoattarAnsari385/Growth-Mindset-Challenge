import streamlit as st
import pandas as pd
import os
from io import BytesIO
import time
import plotly.express as px

st.set_page_config(page_title="🚀 Data Transformer", layout="wide")
st.title("🚀 Data Transformer")
st.write("Effortlessly switch between CSV and Excel formats while cleaning and visualizing your data!")

upload_files = st.file_uploader("Upload Your File (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if upload_files:
    for file in upload_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        try:
            with st.spinner(f"Processing {file.name}..."):
                
                if file_ext == ".csv":
                    df = pd.read_csv(file)
                elif file_ext == ".xlsx":
                    df = pd.read_excel(file)
                else:
                    st.error(f"Unsupported file type {file_ext}")
                    continue
            
            st.success(f"{file.name} uploaded successfully!")
            
            st.write(f"**File Name:** {file.name}")
            st.write(f"**File Size:** {file.size / 1024:.2f} KB")
            
            if st.toggle(f"Preview Data for {file.name}"):
                st.dataframe(df.head())
            
            st.subheader("🛠 Data Cleaning Options")

            if st.checkbox(f"Clean data for {file.name}", key=f"clean_{file.name}"):                
                if st.checkbox(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates Removed!")
            
                if st.checkbox(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("✅ Missing Values Filled!")
        
            st.subheader("📑 Select Columns to Convert")
            columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]
            
            st.subheader("📊 Data Visualization")
            if st.checkbox(f"Show Visualization for {file.name}"):
                numeric_data = df.select_dtypes(include='number').columns
                if not numeric_data.empty:
                    x_axis = st.selectbox("Select X-axis", numeric_cols)
                    y_axis = st.selectbox("Select Y-axis", numeric_cols)
                    fig = px.bar(df, x=x_axis, y=y_axis, title=f"Bar Chart for {file.name}")
                    st.plotly_chart(fig)
                else:
                    st.write("⚠ No numeric data available for visualization.")
            
            st.subheader("🔄 Conversion Options")
            conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
            if st.button(f"Convert {file.name}"):
                buffer = BytesIO()
                
                progress = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.05)
                    progress.progress(percent_complete + 1)
                st.success("🎉 Conversion Completed!")
                
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                
                buffer.seek(0)
                st.download_button(
                    label=f"Download {file.name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
                st.success(f"✅ {file.name} successfully converted to {conversion_type}!")
                
        except Exception as e:
            st.error(f"❌ Error processing {file.name}: {e}")

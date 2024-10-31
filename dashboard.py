import streamlit as st
import xlrd
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout='wide')

st.title(" :bar_chart: Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))

if fl is not None:
    filename= fl.name
    st.write(filename)
    df = pd.read_csv(filename, sep=';' , encoding = 'ISO-8859-1')

else:
    os.chdir(r"C:\Users\gorkem.azder\Desktop\Gorkem\streamlit_dashboard")
    df = pd.read_csv("Superstore.csv", sep=';' , encoding = 'ISO-8859-1', on_bad_lines='skip')
    df.rename(columns={'ï»¿Row ID': 'Row ID'}, inplace=True)


col1, col2 = st.columns((2))

df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d.%m.%Y')

#Getting the min and max date

startDate = pd.to_datetime(df['Order Date'], format='%d.%m.%Y').min()
endDate = pd.to_datetime(df['Order Date'], format='%d.%m.%Y').max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

#sidebar creation

st.sidebar.header("Choose your filter: ")

region = st.sidebar.multiselect("Pick the Region", df["Region"].sort_values().unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]


#Create a filer for State

state = st.sidebar.multiselect("Pick the State", df2['State'].sort_values().unique())

if not state:
     df3 = df2.copy()

else:
    df3 = df2[df2["State"].isin(state)]

#Create a filter for City

city = st.sidebar.multiselect("Pick the State", df3['City'].sort_values().unique())


def filter_data(df, region, state, city):
    if region:
        df = df[df["Region"].isin(region)]
    
    if state:
        df = df[df['State'].isin(state)]
    
    if city:
        df = df[df["City"].isin(city)]

    return df

filtered_df = filter_data(df, region, state, city)

#st.write(filtered_df.columns)
#st.write(filtered_df['ï»¿Row ID'])

#filtered_df = filtered_df.iloc[:, 1:]
filtered_df['Sales'] = filtered_df['Sales'].str.replace('.','').str.replace(',','.').astype(float)
filtered_df['Quantity'] = filtered_df['Quantity'].astype(int)
filtered_df['Discount'] = filtered_df['Discount'].str.replace('.','').str.replace(',','.').astype(float)
filtered_df['Profit'] = filtered_df['Profit'].str.replace('.','').str.replace(',','.').astype(float)

category_df = filtered_df.groupby(by = ['Category'], as_index=False)['Sales'].sum()

with col1:
    st.subheader('Category wise Sales')
    fig = px.bar(category_df, x= 'Category', y = 'Sales', text = [f'${x:.2f}' for x in category_df['Sales']],
                 template= "seaborn")
    
    st.plotly_chart(fig, use_container_width=True, height = 200)


with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = 'Sales', names = 'Region', hole = 0.5)
    fig.update_traces(text = filtered_df['Region'], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)

with cl1:
    with st.expander('Category_ViewData'):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name= "Category.csv",
                           mime = "text/csv", help = "Click here to download the data as a CSV file")
        

with cl2:
    with st.expander('Region_ViewData'):
        region = filtered_df.groupby(by="Region", as_index=False)['Sales'].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name="Region.csv", mime ="txt/csv",
                           help = "Click here to download data as a CSV file")
        


filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime("%Y : %m"))['Sales'].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={'Sales':'Amount'}, height=500, width=1000, template='gridon')
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Download Time Series Data"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv=linechart.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data = csv, file_name="TimeSeries.csv", mime='texxt/csv')

#Create a treem based on Region, category, sub-Category

st.subheader('Hierachical view of Sales using TreeMap')
fig3 = px.treemap(filtered_df, path = ["Region", "Category", "Sub-Category"], values = "Sales", hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns(2)

with chart1:
    st.subheader("Segment wise Sales")
    fig = px.pie(filtered_df, values = 'Sales', names = 'Segment', template = "plotly_dark")
    fig.update_traces(text = filtered_df['Segment'], textposition = 'inside')
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Category wise Sales")
    fig = px.pie(filtered_df, values = 'Sales', names = 'Category', template = "gridon")
    fig.update_traces(text = filtered_df['Category'], textposition = 'inside')
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary Table"):
    df_sample = df[0:5][['Region', 'State', 'City', 'Category', 'Sales', 'Profit', 'Quantity']]
    fig = ff.create_table(df_sample, colorscale= "Peach")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise Sub-Category Table")
    filtered_df["month"] = filtered_df['Order Date'].dt.month_name()
    sub_categpry_Year = pd.pivot_table(data=filtered_df, values="Sales", index= ['Sub-Category'], columns = 'month')
    st.write(sub_categpry_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x= "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship between Sales and Profit using Scatter Plot",
                       titlefont= dict(size=20), xaxis = dict(title="Sales", titlefont=dict(size=19)),
                       yaxis = dict(title="Profit", titlefont = dict(size=19)))

st.plotly_chart(data1, use_container_width=True)


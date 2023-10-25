import streamlit as st
import pandas as pd
import plotly.express as px

#Open the Data
schoolData = pd.read_csv("data/schoolData.csv")
frpl = pd.read_csv("data/frpl.csv")


#Cleaning School data
#Only keep those rows in which school_name contains total
mask = schoolData["school_name"].str.contains('Total')
schoolData=schoolData[mask]

#change the school_name to remove the "Total"
schoolData['school_name']=schoolData['school_name'].str.replace(' Total','')

#Remove this column "school_group", "grade", "pi_pct" and "blank_col"
schoolData=schoolData.drop(columns=["school_group", "grade", "pi_pct","blank_col"])

#Remove the school name "Grand" because it was "Grand Total"
mask = schoolData["school_name"]!="Grand"
mask = ~(schoolData['school_name']=='Grand')
schoolData=schoolData[mask]

#Remove the percentage from the percentage columns
def removePercentageSing(dataframe,column_name):
    dataframe[column_name]=dataframe[column_name].str.replace('%',"")

removePercentageSing(schoolData,"na_pct")
removePercentageSing(schoolData,"aa_pct")
removePercentageSing(schoolData,"as_pct")
removePercentageSing(schoolData,"hi_pct")
removePercentageSing(schoolData,"wh_pct")

#Clean Free Lunch
#Remove rows without school name
frpl = frpl.dropna(subset=["school_name"])






#Remove school names that have "ELM K_08", "Mid Schl", "High Schl", "Alt HS", "Spec Ed Total", "Cont Alt Total", "Hospital Site Total", "Dist Total"
mask = ~frpl["school_name"].isin(["ELM K_08", "Mid Schl", "High Schl", "Alt HS", "Spec Ed Total", "Cont Alt Total", "Hospital Sites Total", "Dist Total"])
frpl = frpl[mask]

#Remove the percentage on the percentge column
removePercentageSing(frpl,"frpl_pct")

#Joining the two dataset
joined_dataset=schoolData.merge(frpl,on=["school_name"],how="left")



#create Interface
st.set_page_config(layout='wide')
st.title("School Data about Race and Poverty")
st.sidebar.title("Filters")

#Select the visualization
vis = st.sidebar.radio("Select a visualization",
                       options=["Race / Ethnicity Charts",
                                "Poverty Charts",
                                "Relation Between Race and Poverty"])

st.subheader(vis)
#Select the size of the schools
size = st.sidebar.slider("Select the size of the schools:",
                  min_value=joined_dataset["tot"].min(),
                  max_value=joined_dataset["tot"].max(),
                  value=[joined_dataset["tot"].min(),joined_dataset["tot"].max()]
                  )

#Filter the data according to the size of the school
mask = (joined_dataset["tot"]>=size[0]) & (joined_dataset["tot"]<=size[1])
joined_dataset=joined_dataset[mask]

#Create a selector for the name of schools

schools=st.sidebar.multiselect("Select the schools that you want to include:",
                       options=joined_dataset["school_name"].unique(),
                       default=joined_dataset["school_name"].unique(),
                    )

#Filter only the schools that are selected
mask=joined_dataset["school_name"].isin(schools)
joined_dataset=joined_dataset[mask]

#Convert the free lunch percentage to number
joined_dataset["frpl_pct"]=pd.to_numeric(joined_dataset["frpl_pct"])

#Mark all schools with frpl bigger than 75% as "High Poverty"
joined_dataset["high_poverty"]=joined_dataset["frpl_pct"]>75

#Convert from a wide dataset to a long dataset
long_dataset = joined_dataset.melt(
    id_vars=["school_name", "high_poverty"], #column that uniquely identifies a
    value_vars=['na_num', 'aa_num', 'hi_num', 'wh_num'],
    var_name='race_ethnicity', #name fr
    value_name='population',
)
long_dataset['race_ethnicity']=long_dataset["race_ethnicity"].replace({
    "na_num":"Native American",
    "aa_num":"African American",
    "hi_num":"Hispanic",
    "wh_num":"White"
})

if vis=="Race / Ethnicity Charts":
    col1, col2 = st.columns(2)
    with col1:
        fig=px.pie(long_dataset,values="population",names="race_ethnicity",
               title="Percentage of Races in the School District")
    st.plotly_chart(fig)
    with col2:
        fig=px.histogram(long_dataset,x="race_ethnicity",y="population",
                 title="Total Number of students per race")
    st.plotly_chart(fig)

elif vis=="Poverty Charts":
    col1, col2 = st.columns(2)
    with col1:
        fig=px.pie(long_dataset, values="population", names="high_poverty",
                   title="Percentage of Students in High Poverty Schools"
                   )
        st.plotly_chart(fig)

    with col2:
        fig=px.histogram(long_dataset, x="high_poverty", y="population",
                          title="Total Number of Students in High Poverty Schools")
        st.plotly_chart(fig)

elif vis == "Relation Between Race and Poverty":
    fig = px.pie(long_dataset, values="population", names="race_ethnicity",
                 facet_col="high_poverty",
                 title="Percentage of race in Schools According to Poverty"
                 )
    st.plotly_chart(fig)

st.dataframe(long_dataset)

#display dataframe

st.subheader("Joined Dataset")
st.dataframe(joined_dataset)

st.subheader("School Data")
st.dataframe(schoolData)

st.subheader("Free Lunch")
st.dataframe(frpl)
import pandas as pd
import streamlit as st
import plotly.express as px
from raceplotly.plots import barplot



data3 = pd.read_csv('WHO-COVID-19-global-data.csv')
data3['Date_reported'] = pd.to_datetime(
    data3['Date_reported']).dt.strftime('%Y-%m-%d')


data1 = pd.read_csv('WHO-COVID-19-global-data.csv')
data2=pd.read_csv("vaccination-data.csv")
data2 = data2.rename(columns={'COUNTRY': 'Country'})


st.title('COVID-19 Analysis')

data_world = data1.groupby('Date_reported')[
    ['New_cases', 'New_deaths', 'Cumulative_cases', 'Cumulative_deaths']].sum().reset_index()
world_options = [
    "Cumulative_cases", "Cumulative_deaths", 'New_cases', 'New_deaths']
world_dropdown = st.selectbox(
    'Select Case Type', world_options)

figWorld = px.line(data_world, "Date_reported", world_dropdown)
figWorld.update_layout(title="World wide "+world_dropdown+" vs Date reported")
figWorld.update_layout(width=1000)
st.plotly_chart(figWorld)

covid_data_world = data1[data1['Date_reported'] == "2023-04-06"]

# Create a world map using Plotly Express
fig_map_cases = px.choropleth(covid_data_world, locations='Country', locationmode='country names',
                    color='Cumulative_cases', hover_name='Country', projection='natural earth',
                        title='COVID-19 Cases by Country', color_continuous_scale='Blues')

fig_map_cases.update_layout(width=1000, height=800)
st.plotly_chart(fig_map_cases)

fig_map_deaths = px.choropleth(covid_data_world, locations='Country', locationmode='country names',
                               color='Cumulative_deaths', hover_name='Country', projection='natural earth',
                              title='COVID-19 Deaths by Country', color_continuous_scale='Reds')

fig_map_deaths.update_layout(width=1000, height=800)
st.plotly_chart(fig_map_deaths)

vaccine_count = {}
for vaccines in data2["VACCINES_USED"]:
    
    if not isinstance(vaccines, str):
        continue
    vaccines = vaccines.split(",")
    for vaccine in vaccines:
        if isinstance(vaccine, str):
            if vaccine in vaccine_count:vaccine_count[vaccine] += 1
            else:vaccine_count[vaccine] = 1


vaccine_df = pd.DataFrame.from_dict(vaccine_count, orient="index", columns=["count"])
vaccine_df.index.name = "vaccine"


figure = px.bar(vaccine_df, x=vaccine_df.index, y="count", labels={"x": "Vaccines Used", "y": "Number of Countries"},width=800,height=600)
figure.update_layout(title="Number of Countries Using Each Vaccine")
#st.plotly_chart(figure,use_container_width=True)




cummulative_case_type_options = ["Cumulative_cases","Cumulative_deaths"]
cummulative_case_type_dropdown = st.selectbox('Select Case Type', cummulative_case_type_options)

top_10_countries = data3.groupby(
    'Country')[cummulative_case_type_dropdown].max().sort_values(ascending=False).head(10)
top_10_data = data3[data3['Country'].isin(top_10_countries.index)]
top_10_data = top_10_data.groupby(['Country', 'Date_reported'])[
    cummulative_case_type_dropdown].sum().reset_index()


raceplot = barplot(top_10_data, item_column='Country',
                   value_column=cummulative_case_type_dropdown, time_column='Date_reported', top_entries=10)
fig0 = raceplot.plot(title='COVID-19 Cases in Top 10 Countries',frame_duration=10)
fig0.update_layout(width=1000,height=800)
st.plotly_chart(fig0)

country_list = list(data1['Country'].unique())
selected_countries = st.multiselect('Select countries to compare', country_list,default="India")

case_type_options = ["Cases","Deaths"]
case_type_dropdown = st.selectbox('Select Case Type', case_type_options)

if selected_countries:
    filtered_data_1 = data1[data1['Country'].isin(selected_countries)]

    country_mortality = pd.pivot_table(filtered_data_1, values=["Cumulative_cases","Cumulative_deaths"], index='Country', aggfunc='max')
    country_mortality['Mortality Rate'] = country_mortality["Cumulative_deaths"]*100 / country_mortality["Cumulative_cases"]
    country_mortality = country_mortality.sort_values(by="Cumulative_cases", ascending=False)
    print(country_mortality)

    
    if case_type_dropdown == "Cases":
        fig1_1 = px.line(filtered_data_1, x='Date_reported',
                         y="New_cases", color='Country')
    else:
        fig1_1 = px.line(filtered_data_1, x='Date_reported',
                         y="New_deaths", color='Country')
    
    fig1_1.update_traces(mode='lines')
    fig1_1.update_layout(clickmode='event+select')
    
    if case_type_dropdown == "Cases":
        fig1_3 = px.line(filtered_data_1, x='Date_reported',
                         y='Cumulative_cases', color='Country')
    else:
        fig1_3 = px.line(filtered_data_1, x='Date_reported',
                         y='Cumulative_deaths', color='Country')
    fig1_3.update_traces(mode='lines')
    fig1_3.update_layout(clickmode='event+select')

    @st.cache(suppress_st_warning=True)
    def update_opacity(trace, points, selector):
        selected_country = trace.name
        selected_points = points.point_inds
        if len(selected_points) > 0:
            
            for i, t in enumerate(fig1_1.data):
                if t.name == selected_country:
                    fig1_1.data[i].line.opacity = 1
                    fig1_3.data[i].line.opacity = 1
                else:
                    fig1_1.data[i].line.opacity = 0.1
                    fig1_3.data[i].line.opacity = 0.1
                    
    fig1_1.for_each_trace(lambda trace: trace.on_click(update_opacity))
    fig1_3.for_each_trace(lambda trace: trace.on_click(update_opacity))
    if case_type_dropdown=="Cases":
        fig1_1.update_layout(title="New_Cases vs Date_reported")
        fig1_3.update_layout(title="Cummulative_cases vs Date_reported")
    else:
        fig1_1.update_layout(title="New_Deaths vs Date_reported")
        fig1_3.update_layout(title="Cummulative_Deaths vs Date_reported")
       
    st.plotly_chart(fig1_3)
    st.plotly_chart(fig1_1)
    fig1_2 = px.bar(country_mortality, x=country_mortality.index,
                    y='Mortality Rate', color='Mortality Rate')
    fig1_2.update_layout(xaxis_title="Country", yaxis_title='Mortality Rate (%)',
                         coloraxis_showscale=False, plot_bgcolor='white')
    # st.write("Mortality Rate vs Countries")
    fig1_2.update_layout(title="Mortality Rate vs Countries ")
    st.plotly_chart(fig1_2)
    



    filtered_data_2 = data2[data2['Country'].isin(selected_countries)]
    

    chart_data_1 = filtered_data_2[['Country', 'PERSONS_FULLY_VACCINATED_PER100']].groupby('Country').max().reset_index()
    fig1 = px.bar(chart_data_1, x='Country', y='PERSONS_FULLY_VACCINATED_PER100', color='Country',width=600)
    fig1.update_layout(xaxis_title="Country", yaxis_title='PERSONS_FULLY_VACCINATED_PER100', coloraxis_showscale=False, plot_bgcolor='white')
    fig1.update_layout(title="PERSONS_FULLY_VACCINATED_PER100 vs Countries")
    

    chart_data_3 = filtered_data_2[['Country', 'PERSONS_BOOSTER_ADD_DOSE_PER100']].groupby('Country').max().reset_index()
    fig3 = px.bar(chart_data_3, x='Country', y='PERSONS_BOOSTER_ADD_DOSE_PER100', color='Country',width=600)
    fig3.update_layout(xaxis_title="Country", yaxis_title='PERSONS_BOOSTER_ADD_DOSE_PER100', coloraxis_showscale=False, plot_bgcolor='white')
    fig3.update_layout(title="PERSONS_BOOSTER_ADD_DOSE_PER100 vs Countries")


    
    st.plotly_chart(fig1,use_container_width=False)
    st.plotly_chart(fig3,use_container_width=False)
    sct_fig = px.scatter(filtered_data_2, x='FIRST_VACCINE_DATE',
                         y='Country', color='ISO3', hover_name='Country')

    sct_fig.update_layout(
        title='Starting Dates of Vaccination for Countries',
        xaxis_title='Start Date',
        yaxis_title='Country',
        legend_title='Region',
        font=dict(
            size=12
        )
    )

    # sct_fig = px.scatter(x=data2['FIRST_VACCINE_DATE'],y=[0]*len(data2))
    sct_fig.update_layout(title="First Vaccine Date of countries")
else:
    st.write('Please select at least one country.')
st.plotly_chart(sct_fig, use_container_width=True)
st.plotly_chart(figure,use_container_width=True)
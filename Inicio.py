import streamlit as st
st.set_page_config(page_title="COVID-19: análisis de datos reportados de pacientes y capacidad hospitalaria",page_icon=':bar_chart:',layout='wide')
import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots


pio.templates.default = "ggplot2"

st.set_page_config(page_title="COVID-19: análisis de datos reportados de pacientes y capacidad hospitalaria",page_icon=':bar_chart:',layout='wide')
st.title('COVID-19: análisis de datos reportados de pacientes y capacidad hospitalaria')

st.markdown('<b><u>Análisis</u>: Fernando Ashur Ramallo',unsafe_allow_html=True)
st.markdown("<hr>",unsafe_allow_html=True)

file = pd.read_csv(r"COVID-19_Reported_Patient_Impact_and_Hospital_Capacity_by_State_Timeseries.csv",sep=',')
data = pd.DataFrame(file)
df = data[['date','state','deaths_covid','inpatient_beds_used_covid','staffed_adult_icu_bed_occupancy','staffed_icu_adult_patients_confirmed_covid','staffed_icu_adult_patients_confirmed_and_suspected_covid']] 
states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

df['date'] = pd.to_datetime(df['date'])
df['state_name'] = df['state'].map(states)
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

# -- Sidebar -- 
st.sidebar.header('Por favor, seleccione aquí las fechas a considerar:')

date_ini = st.sidebar.date_input(
    'Seleccione la fecha de inicio del período a considerar',
    value=dt.date(2020,1,1),
    min_value=dt.date(2020,1,1),
    max_value=dt.date(2022,8,1),
    key=2,
)
date_fin = st.sidebar.date_input(
    'Seleccione la fecha de finalización del período a considerar',
    value=dt.date(2022,8,1),
    min_value=dt.date(2020,1,2),
    max_value=dt.date(2022,8,1),
    key=3,
)

if date_fin < date_ini:
    st.sidebar.error('La fecha de finalizacion no puede ser menor a la de inicio. Seleccione correctamente o se tomará el valor 2020-08-02 por defecto')
    date_fin = dt.date(2022,8,1)


#-- Mainpage --
st.title(":hospital: Dashboard situacional COVID-19 (EEUU)")
st.markdown("\n\n")  
cols = ['date','state','Muertos por COVID','Camas comunes usadas para COVID', 'Camas UCI adultos usadas para COVID']
df_sum = pd.DataFrame()
df_sum[cols] = df[['date','state','deaths_covid','inpatient_beds_used_covid','staffed_icu_adult_patients_confirmed_and_suspected_covid']]
df_sum = df_sum[(df_sum['date'].dt.date >= date_ini) & (df_sum['date'].dt.date <= date_fin)]

filter = st.selectbox('Seleccione un parametro a representar:',
                    options=['Muertos por COVID','Camas comunes usadas para COVID', 'Camas UCI adultos usadas para COVID'],
                    index=1

)

df_sum = df_sum.groupby('state').sum()
df_sum['state'] = df_sum.index
df_sum['Estado'] = df_sum.index.map(states)

text = (f"{filter} por estado entre {date_ini} y {date_fin}")

fig = px.choropleth(df_sum,
                    locations='state', 
                    locationmode="USA-states", 
                    scope="usa",
                    color= filter,
                    color_continuous_scale="Turbo",
                    title=text,
                    template='ggplot2')

fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6.0,
    mapbox_center={"lat": 46.8, "lon": 8.2},
    width=800,
    height=600,)
st.plotly_chart(fig)
st.markdown("<hr>",unsafe_allow_html=True)
#------
st.header('Uso de camas UCI por estado')

cols=['date','state','Muertes por COVID','staffed_adult_icu_bed_occupancy','staffed_icu_adult_patients_confirmed_covid']
df_uci = pd.DataFrame()
df_uci[cols] = data[['date','state','deaths_covid','staffed_adult_icu_bed_occupancy','staffed_icu_adult_patients_confirmed_covid']]
df_uci['date'] = pd.to_datetime(df_uci['date'])

df_uci = df_uci[(df_uci['date'].dt.date >= date_ini )&(df_uci['date'].dt.date <= date_fin)]
df_uci['Ocupacion UCI'] = round(df_uci['staffed_icu_adult_patients_confirmed_covid']/df_uci['staffed_adult_icu_bed_occupancy']*100,2)
df_uci = df_uci.groupby(by='state').agg({'Muertes por COVID':'sum','Ocupacion UCI':'mean'})
df_uci['Estado'] = df_uci.index.map(states)

fig = px.bar(df_uci.sort_values(by='Ocupacion UCI',ascending=False).head(10), x='Estado', y="Ocupacion UCI",color='Estado')
st.plotly_chart(fig)

with st.expander('Ver tabla completa'):
    st.table(df_uci.sort_values(by='Ocupacion UCI',ascending=False)[['Estado','Ocupacion UCI']])

df_oc_de = df_uci.sort_values(by='Ocupacion UCI',ascending=False).head(5)[['Estado','Ocupacion UCI','Muertes por COVID']]

with st.container():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df_oc_de['Estado'],y=df_oc_de['Ocupacion UCI'], name='%Ocupacion UCI'),
        secondary_y=False
    )
    fig.add_trace(
        go.Bar(x=df_oc_de['Estado'],y=df_oc_de['Muertes por COVID'],name='Muertos por COVID'),  
        secondary_y=True
    )
    fig.update_layout(
        title_text="Relacion entre (%) de ocupacion UCI (avg) y muertes en top 5 estados por Ocupacion UCI"
    )
    fig.update_xaxes(title_text="Estado")
    fig.update_yaxes(title_text="% ocupacion", secondary_y=False)
    fig.update_yaxes(title_text="Muertes COVID", secondary_y=True)
    st.plotly_chart(fig)

st.markdown("<hr>",unsafe_allow_html=True)

#------------------------------------------------------------------------------
st.header('Ranking de estados por ocupación hospitalaria')
st.markdown('A continuación se muestra el top 10 de estados según su porcentaje de ocupacion hospitalaria promedio en el período de tiempo seleccionado')

df_cap= data[['date','state','inpatient_bed_covid_utilization_numerator','adult_icu_bed_covid_utilization_numerator','inpatient_bed_covid_utilization_denominator','adult_icu_bed_covid_utilization_denominator']]
df_cap['date'] = pd.to_datetime(df_cap['date'])
df_cap=df_cap[(df['date'].dt.date >=date_ini )&(df['date'].dt.date<=date_fin)]
df_cap.set_index('date',inplace=True)
df_cap.dropna(inplace=True)
df_cap['Ocupacion'] = round((df_cap['inpatient_bed_covid_utilization_numerator']+df_cap['adult_icu_bed_covid_utilization_numerator'])/(df_cap['inpatient_bed_covid_utilization_denominator']+df_cap['adult_icu_bed_covid_utilization_denominator'])*100,2)
df_cap = df_cap.groupby(by='state').agg({'Ocupacion':'max'}).sort_values(by='Ocupacion',ascending=False)
df_cap['Estado'] = df_cap.index.map(states)

fig = px.bar(df_cap.head(10), x="Ocupacion", y="Estado", orientation='h',color='Estado')
st.plotly_chart(fig)
with st.expander("Ver ranking completo"):
    st.table(df_cap[['Estado','Ocupacion']])

st.markdown("<hr>",unsafe_allow_html=True)
st.header('Cantidad de camas ocupadas por COVID')
with st.container():
    df_hosp_state = df[(df['date'].dt.date >=date_ini )&(df['date'].dt.date<=date_fin)].groupby(by='state').sum()
    df_hosp_state['states'] = df_hosp_state.index
   
    title = (f"Cantidad de camas comunes por COVID, entre {date_ini} y {date_fin} (acumulado)")
    fig = px.choropleth(df_sum,
                        locations='state', 
                        locationmode="USA-states", 
                        scope="usa",
                        color='Camas comunes usadas para COVID',
                        color_continuous_scale="Viridis_r",
                        title=title)
    st.plotly_chart(fig)
    with st.expander("Ver tabla completa"):
        st.table(df_sum.sort_values(by='Camas comunes usadas para COVID',ascending=False)[['Estado','Camas comunes usadas para COVID']])
    

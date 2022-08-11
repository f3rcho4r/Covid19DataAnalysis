import streamlit as st
import pandas as pd
import os
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots
from Inicio import states
import plotly.io as pio

pio.templates.default = "plotly"
states_inverse = {v: k for k, v in states.items()}

@st.cache
def LoadData():
    file = pd.read_csv(r"../COVID-19_Reported_Patient_Impact_and_Hospital_Capacity_by_State_Timeseries.csv",sep=',')
    df = pd.DataFrame(file)
    df['date'] = pd.to_datetime(df['date'])
    return df

df = LoadData()

st.header('5 Estados con mayor ocupación hospitalaria por COVID en los 6 primeros meses del 2020')
st.markdown('Criterio de ocupación: por cama común, con pacientes confirmados')

#-----
st.sidebar.markdown("En base al cuestionario facilitado por el Team Leader, se responden en esta página algunas cuestiones especificas en torno al análisis de los datos brindados por la API")
top5 = df[df['date'].dt.date <= dt.date(2020,6,30)].groupby(by='state').sum().sort_values(by='inpatient_beds_used_covid', ascending=False).head(5)
top5.rename(columns={'inpatient_beds_used_covid':'Camas comunes usadas para pacientes COVID'},inplace=True)
top5['Estado'] = top5.index.map(states)
st.table(top5[['Estado','Camas comunes usadas para pacientes COVID']])

st.header("Ocupación de camas (común) por COVID en el Estado de Nueva York")
st.markdown('Período comprendido desde el inicio de la pandemia (2020) hasta el 2022-08-02')

#----
#Genero un dataframe sólo con datos del estado de Nueva York
df = LoadData()
df_ny = df[df['state'] == 'NY']
df_ny = df_ny.sort_values(by='date')

fig = px.line(df_ny,x='date',y='inpatient_beds_used_covid')
st.plotly_chart(fig)

path = os.path.dirname(__file__)
st.write(path)

with st.container():
    st.subheader('Primer intervalo de crecimiento')
    col1, col2 = st.columns(2)
    with col1:
        img=Image.open(r"./pages/ny_fecha1.png")
        st.image(img)

    with col2:
        st.markdown('Se observa un primer período de crecimiento a partir del mínimo marcado por el comienzo del registro de datos, con un pico en el día 2020-04-14 a partir del cual se da un proceso de decrecimiento')

    st.subheader('Segundo intervalo de crecimiento')
    col1, col2 = st.columns(2)
    with col1:
        img=Image.open(r"./pages/ny_fecha2.png")
        st.image(img)

    with col2:
        st.markdown('Se observa un segundo período de crecimiento con un pico en el día 2021-01-19 y un nuevo minimo en el día 2021-07-04')

    st.subheader('Tercer intervalo de crecimiento')
    col1, col2 = st.columns(2)
    with col1:
        img=Image.open(r"./pages/ny_fecha3.png")
        st.image(img)

    with col2:
        st.markdown('Se observa un ultimo período de crecimiento con un pico en el día 2022-01-12 y un nuevo minimo en el día 2022-03-26')

#---
st.header('TOP 5 estados que más camas UCI (Unidades de Cuidados Intensivos) utilizaron durante el año 2020')
st.markdown('En términos absolutos.')
#Genero un dataframe con datos de 2020
df_20 = df[df['date'].dt.date < dt.date(2021,1,1)]
df_20['Camas UCI'] = df_20['staffed_adult_icu_bed_occupancy'] + df_20['staffed_pediatric_icu_bed_occupancy']
df_20 = df_20.groupby(by='state').sum().sort_values(by='Camas UCI',ascending=False)
df_20['Estado'] = df_20.index.map(states)

st.table(df_20.head(5)[['Estado','Camas UCI']])
fig = px.pie(df_20.head(10), values='Camas UCI', names='Estado', title='Uso de camas UCI por estados, año 2020')
st.plotly_chart(fig)

#---
st.header("Cantidad de camas utilizadas para pacientes pediátricos con COVID durante el 2020, por estado. ")
#Genero un dataframe con datos de 2020
df_20 = df[df['date'].dt.date < dt.date(2021,1,1)]
#Renombro columna para mostrar en tabla
df_20.rename(columns={'total_pediatric_patients_hospitalized_confirmed_and_suspected_covid':'Camas pediatricas'},inplace=True)
#Agrupo por estado, sumando el campo target y ordeno en forma descendiente
df_20 = df_20.groupby(by='state').sum().sort_values(by='Camas pediatricas',ascending=False)
#Mapeo códigos de estado a nombres para mostrar
df_20['Estado'] = df_20.index.map(states)
st.table(df_20['Camas pediatricas'].head(5))
with st.expander('Ver ranking completo'):
    st.table(df_20['Camas pediatricas'])

fig = px.bar(df_20.head(5),x='Estado',y='Camas pediatricas',color='Estado',title='Top 5 Estados por camas pediatricas COVID, 2020')
st.plotly_chart(fig)

#----
st.header("Porcentaje de camas UCI correspondendientes a casos confirmados de COVID, por estado")
df_uci = df[['date','state','staffed_adult_icu_bed_occupancy','staffed_icu_adult_patients_confirmed_covid','staffed_icu_pediatric_patients_confirmed_covid','staffed_pediatric_icu_bed_occupancy']]
df_uci['Porcentaje UCI'] = (df_uci['staffed_icu_adult_patients_confirmed_covid']+df_uci['staffed_icu_pediatric_patients_confirmed_covid'])/(df_uci['staffed_adult_icu_bed_occupancy']+df_uci['staffed_pediatric_icu_bed_occupancy'])*100
df_uci= df_uci.groupby(by='state').mean().sort_values(by='Porcentaje UCI', ascending=False)
df_uci['Estado'] = df_uci.index.map(states)

fig = px.bar(df_uci.head(5),x='Estado',y='Porcentaje UCI',color='Estado',color_continuous_scale="sunset")
st.plotly_chart(fig)
with st.expander('Ver ranking completo:'):
    st.table(df_uci['Porcentaje UCI'])
    st.markdown('Algunos estados no reportaron todos los datos considerados para este análisis en el período, por lo que figuran con valores NAN')

#---
st.header("Muertes por covid, por estado, durante el año 2021")
df_21 = df[['date','state','critical_staffing_shortage_today_yes','deaths_covid']]
df_21.rename(columns={'critical_staffing_shortage_today_yes':'Falta de personal','deaths_covid':'Muertos por COVID'},inplace=True)

df_21 = df_21[df_21['date'].dt.year == 2021]
df_21 = df_21.groupby(by='state').agg({'Falta de personal':'mean','Muertos por COVID':'sum'})
df_21['Estado'] = df_21.index.map(states)

fig = px.choropleth(df_21,
                    locations=df_21.index, 
                    locationmode="USA-states", 
                    scope="usa",
                    color= 'Muertos por COVID',
                    color_continuous_scale="sunset",
                    )
                
fig.update_layout(
    width=800,
    height=600,)
fig.update_layout(title='Muertos por COVID en 2021',
                 font={'size':14})
fig.update_layout(title={
    'x':0.45,
    'xanchor':'center'
})
st.plotly_chart(fig)
st.table(df_21.sort_values(by='Muertos por COVID',ascending=False)[['Estado','Muertos por COVID']].head(5))


with st.expander('Ver tabla completa'):
    st.table(df_21.sort_values(by='Muertos por COVID',ascending=False)[['Estado','Muertos por COVID']])

#---------------
st.header('Relación entre falta de personal y muertes por COVID, año 2021')

#
with st.container():
    st.write('Seleccione un estado para visualizar la relacion entre falta de personal (promedio) y muertos por COVID (acumulado) para ese estado. Si no selecciona ningún valor, se tomarán los 10 estados con mayor cantidad de muertes por COVID')
    with st.expander('Seleccione un estado'):
        state = st.multiselect('Estado:',
                        options=df_21['Estado'].unique(),
                        default=df_21.sort_values(by='Muertos por COVID',ascending=False)['Estado'].head(10))

state = list(map(states_inverse.get,state))

df_selection = df_21.query('state == @state').sort_values(by='Muertos por COVID',ascending=False)
st.table(df_selection[['Muertos por COVID','Falta de personal']])
#Armo el plot con datos de muertes por COVID y falta de personal
fig = px.bar(df_selection,x=df_selection['Estado'],y=df_selection['Falta de personal'],color='Muertos por COVID')
fig.update_layout(title_text="Relacion entre falta de personal y muertes por COVID")
fig.update_layout(title={
    'x':0.45,
    'xanchor':'center'
})
fig.update_yaxes(title_text="Hosp. con falta de personal crítico (avg)")
st.plotly_chart(fig)
##------------------------------
df_21 = df[['date','state','critical_staffing_shortage_today_yes','deaths_covid']]
df_21.rename(columns={'critical_staffing_shortage_today_yes':'Falta de personal','deaths_covid':'Muertos por COVID'},inplace=True)
df_21 = df_21[df_21['date'].dt.year == 2021]
df_21['Estado'] = df_21['state'].map(states)


with st.container():
    st.write('Seleccione un estado para visualizar la relacion entre falta de personal y muertos por COVID  para ese estado a lo largo de todo 2021. Si no selecciona ningún valor, se tomará el estado con mayor cantidad de muertes por COVID.')
    with st.expander('Seleccione un estado'):
        state = st.multiselect('Estado:',
                        options=df_21['Estado'].unique(),
                        default=df_21.sort_values(by='Muertos por COVID',ascending=False)['Estado'].head(1))

title = ' '.join(state)
state = list(map(states_inverse.get,state))


df_selection = df_21.query('state == @state').sort_values(by='date')

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Scatter(x=df_selection['date'],y=df_selection['Falta de personal'], name='Falta de personal',),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(x=df_selection['date'],y=df_selection['Muertos por COVID'],name='Muertos por COVID',),  
    secondary_y=True
)
fig.update_layout(
    title_text="Relacion entre falta de personal y muertes por COVID en 2021"
)
fig.update_xaxes(title_text=title)
fig.update_yaxes(title_text="Hospitales con falta de personal", secondary_y=False)
fig.update_yaxes(title_text="Muertes COVID", secondary_y=True)
st.plotly_chart(fig)
#----
st.header('Peor mes de la pandemia para EEUU')
cols = ['date','Camas usadas para COVID','Falta de personal','Muertos por COVID','Ocupacion UCI pediatrica','Ocupacion UCI adultos']
df = LoadData()
df_f = pd.DataFrame()
df_f[cols] = df[['date','inpatient_beds_used_covid','critical_staffing_shortage_today_yes','deaths_covid','staffed_pediatric_icu_bed_occupancy','staffed_adult_icu_bed_occupancy']]
#df_f['mes'] = df_f['date'].dt.to_period('M')
df_f = df_f.sort_values(by='date')
df_f = df_f.resample('M',on='date').sum()

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Scatter(x=df_f.index,y=df_f['Camas usadas para COVID'], name='Camas usadas para COVID',),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(x=df_f.index,y=df_f['Falta de personal'],name='Falta de personal'),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(x=df_f.index,y=df_f['Ocupacion UCI pediatrica'],name='Ocupacion UCI pediatrica'),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(x=df_f.index,y=df_f['Ocupacion UCI adultos'],name='Ocupacion UCI adultos'),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(x=df_f.index,y=df_f['Muertos por COVID'],name='Muertos por COVID'),  
    secondary_y=True
)
fig.update_layout(
    title_text="Variables asociadas a stress del servicio de salud durante la pandemia",title={
    'x':0.41,
    'xanchor':'center'}
)
fig.update_layout(
    autosize=False,
    width=900,
    height=500,
)
# fig.update_xaxes(title_text=title)
fig.update_yaxes(title_text="Cantidad", secondary_y=False)
fig.update_yaxes(title_text="Muertes COVID", secondary_y=True)
st.plotly_chart(fig)
st.markdown('En el gráfico puede observarse que, por la conjunción de máximos de camas utilizadas para COVID, muertos por COVID y ocupacion de camas de cuidados intensivos, enero de 2021 fue el peor mes de la pandemia hasta ahora en EEUU')


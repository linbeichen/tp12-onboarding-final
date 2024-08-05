import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd



# 加载数据
accident_lga = gpd.read_file('accident_lga.geojson')
accident_severity = pd.read_json('accident_severity.json')

accident_lga['accident_category'] = pd.cut(
    accident_lga['ACCIDENT_NO'], 
    bins=[0, 100, 500, 1000, float('inf')],
    labels=['Low', 'Medium', 'High', 'Very High']
)

# 创建地图
def create_map():
    fig = px.choropleth_mapbox(
        accident_lga, 
        geojson=accident_lga.geometry, 
        locations=accident_lga.index, 
        color= 'accident_category',
        color_discrete_map={
            'Low': 'lightcoral',
            'Medium': 'red',
            'High': 'darkred',
            'Very High': 'maroon'
        },
        mapbox_style="carto-positron",
        zoom=8, center = {"lat": -37.8104, "lon": 144.9628},
        opacity=0.8,
        labels={'ACCIDENT_NO':'Number of Accidents'}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

# 创建条形图
def create_bar_chart(selected_lga):
    filtered_data = accident_severity[accident_severity['LGA_NAME'] == selected_lga]
    severity_data = filtered_data.groupby('SEVERITY')['ACCIDENT_NO'].sum().reset_index()
    severity_data['SEVERITY'] = severity_data['SEVERITY'].map({1: 'Mild', 2: 'Severe', 3: 'Fatal'})
    
    fig = px.bar(severity_data, x='SEVERITY', y='ACCIDENT_NO', 
                 labels={'ACCIDENT_NO': 'Number of Accidents', 'SEVERITY': 'Severity'},
                 title=f'Accident Severity in {selected_lga}')
    return fig

# 应用布局
def create_visualization_page():
    return html.Div([
        html.H1("Accident Data Visualization"),
        dcc.Graph(id='map', figure=create_map()),
        html.Div([
            html.Label("Select LGA:"),
            dcc.Dropdown(
                id='lga-dropdown',
                options=[{'label': lga, 'value': lga} for lga in accident_severity['LGA_NAME'].unique()],
                value='ALPINE'
            ),
        ]),
        dcc.Graph(id='bar-chart')
    ])
'''
html.Div([
    html.H1("Accident Data Visualization"),
    dcc.Graph(id='map', figure=create_map()),
    html.Div([
        html.Label("Select LGA:"),
        dcc.Dropdown(
            id='lga-dropdown',
            options=[{'label': lga, 'value': lga} for lga in accident_severity['LGA_NAME'].unique()],
            value='ALPINE'
        ),
    ]),
    dcc.Graph(id='bar-chart')
])
'''

# 回调函数更新条形图
@callback(
    Output('bar-chart', 'figure'),
    Input('lga-dropdown', 'value')
)
def update_bar_chart(selected_lga):
    return create_bar_chart(selected_lga)

# 运行应用
if __name__ == '__main__':
    # 初始化Dash应用
    app = dash.Dash(__name__)
    app.layout = create_visualization_page()
    app.run_server(debug=True)
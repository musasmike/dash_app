# Import required packages
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load the data
spacex_df = pd.read_csv('data/spacex_launch_dash.csv')
# Launch Sites drop-down list
launch_sites_list = list(spacex_df['Launch Site'].unique())
launch_sites_list.insert(0, 'All Sites')

# Application layout
app.layout = dbc.Container(children=[
    # The Header Section
    dbc.Row([
        dbc.Col([
            # Dashboard Title
            html.Div('SpaceX Launch Records Dashboard',
                     style={'font-size': '28px', 'font-family': 'Merriweather', 'font-weight': 'bold',
                            'color': 'white'})
        ],
            width={'size': 12},
            style={'padding': '5px 0 0 0', 'text-align': 'center'}
        )
    ], justify='center', style={'background-color': '#000000', 'padding': '10px 0 15px 0'}),
    # Break line
    html.Br(),
    html.Br(),

    # Launch Site Drop-Down Menu
    dbc.Row([
        dbc.Col([
            # Launch Site Menu Title
            html.Div('Launch Site'),
            # Launch Site Drop-down
            html.Div(dcc.Dropdown(
                id='site-dropdown',
                options=[
                    {'label': i, 'value': i}
                    for i in launch_sites_list
                ],
                value='All Sites',
                placeholder='place holder here',
                searchable=True
            ))
        ], width={'size': 4}),
        # Range Slider
        dbc.Col([
            html.Div('Payload Range (Kg):'),
            html.Div(dcc.RangeSlider(
                0, 10000, 1000, value=[0, 10000],
                id='payload-slider'
            ))
        ], width={'size': 7, 'offset': 1})
    ]),

    # Graphs
    dbc.Row([
        # Graph 1: pie chart
        dbc.Col([
            # Graph 1 object
            html.Div(dcc.Graph(id='success-pie-chart'))
        ], width={'size': 5}),
        # Graph 2: Scatter point chart
        dbc.Col([
            # Graph 2 object
            html.Div(dcc.Graph(id='success-payload-scatter-chart'))
        ], width={'size': 7})
    ])
])


# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    filtered_df_all_sites = filtered_df.groupby('Launch Site')[['class']].mean().reset_index()
    if entered_site == 'All Sites':
        fig = go.Figure(data=[go.Pie(labels=filtered_df_all_sites['Launch Site'],
                                     values=filtered_df_all_sites['class'],
                                     textfont=dict(color='white', size=16),
                                     textinfo='label+percent',
                                     marker_colors=('#D9D9D9', '#A6A6A6', '#00C2BA', '#BFBFBF'),
                                     scalegroup='one')
                              ])

        fig.update_traces(marker=dict(line=dict(color='#FFFFFF', width=2)))

        fig.update_layout(
            title=dict(
                text='Total Success Launches by Sites',
                font=dict(size=20)
            ),
            plot_bgcolor='white',
            margin=dict(t=100, l=0, r=0, b=0),
            showlegend=False
        )

        return fig
    else:
        for site in list(filtered_df['Launch Site'].unique()):
            if entered_site == site:
                filter_site = filtered_df.loc[filtered_df['Launch Site'] == site]
                filter_site = round(filter_site['class'].value_counts(normalize=True) * 100,
                                    2).sort_index().reset_index()
                filter_site['class'] = filter_site['class'].replace(0, 'Failed').replace(1, 'Succeed')
                fig = go.Figure(data=[go.Pie(labels=filter_site['class'],
                                             values=filter_site['proportion'],
                                             textfont=dict(color=['black', 'white'], size=16),
                                             textinfo='label+percent',
                                             marker_colors=['#D9D9D9', '#00C2BA'],
                                             scalegroup='one')
                                      ])
                fig.update_traces(
                    marker=dict(line=dict(color='#FFFFFF', width=2))
                )

                fig.update_layout(
                    title=dict(
                        text='Total Success Launches for site ' + site,
                        font=dict(size=20)
                    ),
                    plot_bgcolor='white',
                    margin=dict(t=100, l=0, r=0, b=0),
                    showlegend=False
                )

        return fig


# Function decorator
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
# The Function
def get_scatter_point(entered_site, payload_mass):
    low, high = payload_mass
    filtered_df = spacex_df
    mask = (filtered_df['Payload Mass (kg)'] > low) & (filtered_df['Payload Mass (kg)'] < high)

    if entered_site == 'All Sites':
        fig = px.scatter(filtered_df[mask], x='Payload Mass (kg)', y='class',
                         color='Booster Version Category', opacity=0.7
                         )
        fig.update_traces(marker_size=10)
        fig.update_layout(
            title=dict(
                text='Correlation between Payload and Success for all Sites',
                font=dict(size=20)
            ),
            plot_bgcolor='white',
            margin=dict(t=100, l=0, r=0, b=0),
            legend_title_text='Booster Version',
            legend=dict(
                bgcolor="#F2F2F2",
                bordercolor="#BFBFBF",
                borderwidth=1
            )
        )
        fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='#BFBFBF')
        fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='#BFBFBF')

        return fig
    else:
        for site in list(filtered_df['Launch Site'].unique()):
            if entered_site == site:
                filter_site = filtered_df.loc[filtered_df['Launch Site'] == site]
                fig = px.scatter(filter_site[mask], x='Payload Mass (kg)', y='class',
                                 color='Booster Version Category', opacity=0.7
                                 )
                fig.update_traces(marker_size=10)
                fig.update_layout(
                    title=dict(
                        text='Correlation between Payload and Success for ' + site,
                        font=dict(size=20)
                    ),
                    plot_bgcolor='white',
                    margin=dict(t=100, l=0, r=0, b=0),
                    legend_title_text='Booster Version',
                    legend=dict(
                        bgcolor="#F2F2F2",
                        bordercolor="#BFBFBF",
                        borderwidth=1
                    )
                )
                fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='#BFBFBF')
                fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='#BFBFBF')

                return fig


if __name__ == '__main__':
    app.run_server(debug=True)

import time
from datetime import datetime
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import redis

# Redis configuration
redis_host = '172.17.0.2'
redis_port = 6379
redis_db = redis.Redis(host=redis_host, port=redis_port, db=0)
redis_key = 'KAFKA_DB2:light_sensor_data'

# Create a Dash app
app = dash.Dash(__name__)

# Define CSS styles
styles = {
    'container': {
        'width': '80%',
        'margin': 'auto',
        'padding': '20px'
    },
    'title': {
        'text-align': 'center',
        'font-size': '24px',
        'margin-bottom': '20px'
    },
    'chart-container': {
        'margin-bottom': '20px'
    },
    'table-container': {
        'height': '200px',
        'overflow-y': 'scroll',
        'border': '1px solid #ddd',
        'margin-bottom': '20px'
    },
    'table': {
        'width': '100%',
        'border-collapse': 'collapse'
    },
    'table-header': {
        'background-color': '#f9f9f9',
        'font-weight': 'bold',
        'text-align': 'center',
        'border-bottom': '1px solid #ddd'
    },
    'table-cell': {
        'border': '1px solid #ddd',
        'padding': '8px',
        'text-align': 'center'
    },
    'table-row': {
        'background-color': '#f9f9f9'
    }
}

# Create a function to generate the table HTML
def generate_table(data):
    header = html.Tr([
        html.Th('Timestamp', style=styles['table-header']),
        html.Th('Sensor Value', style=styles['table-header'])
    ])
    rows = [
        html.Tr([
            html.Td(row['Timestamp'], style=styles['table-cell']),
            html.Td(row['Sensor Value'], style=styles['table-cell'])
        ], style=styles['table-row']) for row in data
    ]
    return html.Table([header] + rows, style=styles['table'])

# Define the layout of the app
app.layout = html.Div(
    style=styles['container'],
    children=[
        html.H1('Arduino to Redis_DB Visualization', style=styles['title']),
        html.Div(
            style=styles['chart-container'],
            children=[
                dcc.Graph(id='sensor-graph')
            ]
        ),
        html.Div(
            style=styles['table-container'],
            children=[
                html.H3('Table', style={'margin-bottom': '10px'}),
                html.Div(id='table-container')
            ]
        ),
        html.Div(
            style=styles['chart-container'],
            children=[
                dcc.Graph(id='area-chart')
            ]
        ),
        html.Div(
            style=styles['chart-container'],
            children=[
                dcc.Graph(id='donut-chart')
            ]
        ),
        dcc.Interval(
            id='interval-component',
            interval=1000,  # Refresh interval in milliseconds
            n_intervals=0
        )
    ]
)

# Update the graph, table, area chart, and donut chart with new data
@app.callback(
    [
        Output('sensor-graph', 'figure'),
        Output('table-container', 'children'),
        Output('area-chart', 'figure'),
        Output('donut-chart', 'figure')
    ],
    Input('interval-component', 'n_intervals')
)
def update_data(n):
    # Fetch data from Redis
    redis_data = redis_db.lrange(redis_key, 0, -1)

    # Parse and store data in lists
    timestamps = []
    sensor_values = []
    for data in redis_data:
        data = data.decode('utf-8')
        try:
            sensor_value = int(data)
            timestamps.append(datetime.now())  # Use current timestamp
            sensor_values.append(sensor_value)
        except ValueError:
            print('Invalid data:', data)

    # Create a scatter trace for the line chart
    scatter_trace = go.Scatter(
        x=timestamps,
        y=sensor_values,
        mode='lines',
        name='Sensor Data',
        line=dict(color='red', width=2),  # Customize line color and width
        marker=dict(symbol='circle', size=8),  # Customize marker symbol and size
        hovertemplate='Timestamp: %{x}<br>Sensor Value: %{y}',  # Customize hover template
        hoverlabel=dict(bgcolor='white', font=dict(color='black'))  # Customize hover label
    )

    # Create the figure for the line chart
    line_fig = go.Figure(data=[scatter_trace])

    # Update the layout for the line chart
    line_fig.update_layout(
        title="Arduino Light Sensor Data Chart",
        xaxis_title='Timestamp (H:M:S)',
        yaxis_title='Sensor Value',
        xaxis=dict(
            range=[timestamps[0], timestamps[-1]],  # Set the range of x-axis
            tickformat='%H:%M:%S'  # Format x-axis tick labels
        ),
        autosize=True  # Automatically adjust graph size
    )

    # Generate the table data
    table_data = []
    for timestamp, sensor_value in zip(timestamps, sensor_values):
        table_data.append({'Timestamp': timestamp, 'Sensor Value': sensor_value})

    # Generate the table HTML
    table_html = generate_table(table_data)

    # Create the figure for the area chart
    area_fig = go.Figure(data=[go.Scatter(x=timestamps, y=sensor_values, fill='tozeroy')])

    # Update the layout for the area chart
    area_fig.update_layout(
        title="Sensor Data Area Chart",
        xaxis_title='Timestamp (H:M:S)',
        yaxis_title='Sensor Value',
        xaxis=dict(
            range=[timestamps[0], timestamps[-1]],  # Set the range of x-axis
            tickformat='%H:%M:%S'  # Format x-axis tick labels
        ),
        autosize=True  # Automatically adjust graph size
    )

    # Create the figure for the donut chart
    donut_fig = go.Figure(data=[go.Pie(labels=['Sensor 1', 'Sensor 2'], values=[30, 70])])

    # Update the layout for the donut chart
    donut_fig.update_layout(
        title="Sensor Distribution",
        autosize=True  # Automatically adjust graph size
    )

    return line_fig, table_html, area_fig, donut_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

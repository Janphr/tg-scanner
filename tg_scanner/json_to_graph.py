import datetime
import json
import math

import plotly
import networkx as nx
from plotly.offline import plot
import plotly.graph_objects as go
import numpy as np
from telethon.errors import ChannelPrivateError
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

import dash
from dash import html, dcc
from dash.dependencies import Output, Input

from moduls import Server

max_depth = 2

api_id = 123
api_hash = 'api_hash'

bot_token = 'bot_token'

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

get_history = lambda ch, dt: GetHistoryRequest(
    peer=ch,
    offset_id=0,
    offset_date=dt,
    add_offset=0,
    limit=100,
    max_id=0,
    min_id=0,
    hash=0
)

g = nx.Graph()
app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(id='fig'),
    dcc.Interval(id='interval_component')
])

server = Server(app)
# server.start()


with TelegramClient('anon', api_id, api_hash) as client:
    data = json.load(open('channels_dict.json'))

    root_title = data[next(iter(data))]['title']

    sizes = []

    for channel_id, channel_dict in data.items():
            for out_id in channel_dict['out']:
                # ch = client.get_entity(out_id)
                try:
                    g.add_edge(channel_dict['title'], data[str(out_id)]['title'])
                except KeyError:
                    print("Channel '" + channel_dict['title'] + "' missing")
                    continue
            for in_id in channel_dict['in']:
                # ch = client.get_entity(in_id)
                try:
                    g.add_edge(data[str(in_id)]['title'], channel_dict['title'])
                except KeyError:
                    print("Channel '" + channel_dict['title'] + "' missing")
                    continue

            sizes.append(math.pow(len(channel_dict['out']) + 1, 1/1.9) + 3)

    pos_dict = nx.spring_layout(g, pos=nx.circular_layout(g), threshold=1e-9, iterations=100,
                                # center=[.75, .25]
                                )

    # pos_dict[root_title] = np.array([-.5, 0])

    pos = np.array(list(pos_dict.values()))

    edge_trace = go.Scatter(
        x=pos[:, 0], y=pos[:, 1],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_trace = go.Scatter(
        x=pos[:, 0], y=pos[:, 1],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Bluered',
            reversescale=True,
            color=[],
            size=sizes,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(g.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(adjacencies[0] + '\nConnections: ' + str(len(adjacencies[1])))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Telegram network of the last 2 days starting in channel \'{}\' with max. depth 2.'
                            .format(root_title),
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    fig.show()
    fig.write_html("scan_result.html")

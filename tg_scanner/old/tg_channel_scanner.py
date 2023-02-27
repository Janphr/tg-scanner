import datetime
import json
from telethon.errors import ChannelPrivateError
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

max_depth = 2

api_id = 123
api_hash = 'API_HASH'

bot_token = 'BOT_TOKEN'

start_channel = 't.me/START_CHANNEL'

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



with TelegramClient('anon', api_id, api_hash) as client:
    channels = []

    from_date = datetime.datetime(2022, 1, 25, 0, 0, 0, 0, datetime.timezone.utc)

    channels.append(client.get_entity(start_channel))
    channels_dict = {}
    channels_dict[channels[0].id] = {
        'out': [],
        'in': [],
        'msg_count': -1,
        'users': {},
        'title': channels[0].title,
        'depth': 0
    }

    channel_idx = 0
    date_time = datetime.datetime.now(datetime.timezone.utc)
    curr_channel = channels[0]

    print("Starting channels:")
    for ch_ in channels:
        print(ch_.title if hasattr(ch_, 'title') else ch_.first_name)
    print("")
    print("New channel: " + curr_channel.title if hasattr(curr_channel, 'title') else curr_channel.first_name)
    while True:
        hist = client(get_history(curr_channel, date_time))

        channels_dict[curr_channel.id]['msg_count'] = hist.count

        for user in hist.users:
            channels_dict[curr_channel.id]['users'][user.id] = user.first_name

        for msg in hist.messages:
            if msg.fwd_from and hasattr(msg.fwd_from.from_id, 'channel_id'):
                try:
                    ch_ = client.get_entity(msg.fwd_from.from_id)
                except ChannelPrivateError:
                    continue
                if channels_dict[curr_channel.id]['depth'] < max_depth and ch_ not in channels:
                    channels.append(ch_)
                    print("New channel found: " + ch_.title)
                if ch_.id not in channels_dict.keys():
                    channels_dict[ch_.id] = {
                        'out': [curr_channel.id],
                        'in': [],
                        'msg_count': -1,
                        'users': {},
                        'title': ch_.title,
                        'depth': channels_dict[curr_channel.id]['depth'] + 1
                    }
                else:
                    if channels_dict[ch_.id]['depth'] > channels_dict[curr_channel.id]['depth'] + 1:
                        channels_dict[ch_.id]['depth'] = channels_dict[curr_channel.id]['depth'] + 1
                    channels_dict[ch_.id]['out'].append(curr_channel.id)

                channels_dict[curr_channel.id]['in'].append(ch_.id)
                # g.add_edge(curr_channel.title, ch_.title)
                #
                # pos_dict = nx.kamada_kawai_layout(g)
                #
                # pos = np.array(list(pos_dict.values()))
                #
                # edge_trace = go.Scatter(
                #     x=pos[:, 0], y=pos[:, 1],
                #     line=dict(width=0.5, color='#888'),
                #     hoverinfo='none',
                #     mode='lines')
                #
                # node_trace = go.Scatter(
                #     x=pos[:, 0], y=pos[:, 1],
                #     mode='markers',
                #     hoverinfo='text',
                #     marker=dict(
                #         showscale=True,
                #         # colorscale options
                #         # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #         # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #         # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                #         colorscale='YlGnBu',
                #         reversescale=True,
                #         color=[],
                #         size=10,
                #         colorbar=dict(
                #             thickness=15,
                #             title='Node Connections',
                #             xanchor='left',
                #             titleside='right'
                #         ),
                #         line_width=2))

                # fig = go.Figure(data=[edge_trace, node_trace],
                #                 layout=go.Layout(
                #                     title='<br>Network graph made with Python',
                #                     titlefont_size=16,
                #                     showlegend=False,
                #                     hovermode='closest',
                #                     margin=dict(b=20, l=5, r=5, t=40),
                #                     xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                #                     yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))


                # @app.callback(Output('fig', 'figure'),
                #               [Input('interval_component', 'n_intervals')])
                # def callback(n_intervals):
                #     return go.Figure(data=[edge_trace, node_trace],
                #                 layout=go.Layout(
                #                     title='<br>Network graph made with Python',
                #                     titlefont_size=16,
                #                     showlegend=False,
                #                     hovermode='closest',
                #                     margin=dict(b=20, l=5, r=5, t=40),
                #                     xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                #                     yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))


                # if app.layout is None:
                #     app.layout = html.Div([
                #         dcc.Graph(figure=fig)
                #     ])
                #
                # else:



                # f = go.FigureWidget(fig)
                # plot(fig, filename='test.html')
                # fig.show()

                # plt.clf()
                # nx.draw(g, pos=nx.kamada_kawai_layout(g), with_labels=True, node_size=[])
                # plt.show()

        if len(hist.messages) < 100 or date_time < from_date:
            channel_idx += 1
            if channel_idx >= len(channels):
                break
            date_time = datetime.datetime.now(datetime.timezone.utc)
            curr_channel = channels[channel_idx]
            print("")
            print("New channel: " + curr_channel.title if hasattr(curr_channel, 'title') else curr_channel.first_name)
        else:
            date_time = hist.messages[-1].date

    with open("channels_dict.json", "w") as outfile:
        json.dump(channels_dict, outfile)


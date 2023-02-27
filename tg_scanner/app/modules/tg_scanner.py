import asyncio
import datetime
import json
import math
import random
import threading
from time import sleep

import numpy as np
from telethon.errors import ChannelPrivateError
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest


def get_history(ch, dt):
    return GetHistoryRequest(
        peer=ch,
        offset_id=0,
        offset_date=dt,
        add_offset=0,
        limit=100,
        max_id=0,
        min_id=0,
        hash=0
    )


def color_gradient(x):
    return 255 * x, 0, 255 - 255 * x


def hsv_to_rgb(h, s, v):
    h_i = int(h * 6)
    f = h * 6 - h_i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    if h_i == 0:
        r, g, b = v, t, p
    elif h_i == 1:
        r, g, b = q, v, p
    elif h_i == 2:
        r, g, b = p, v, t
    elif h_i == 3:
        r, g, b = p, q, v
    elif h_i == 4:
        r, g, b = t, p, v
    elif h_i == 5:
        r, g, b = v, p, q
    else:
        r, g, b = 0, 0, 0
    return int(r * 256), int(g * 256), int(b * 256)


class TGScanner(threading.Thread):
    api_id = 123
    api_hash = 'API_HASH'
    start_channel = 't.me/START_CHANNEL'

    max_depth = 4
    from_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=18)

    golden_ratio_conjugate = 0.618033988749895
    h = random.randint(0, 256)

    def __init__(self):
        super().__init__()
        self.update = None
        self.add_node_list = None
        self.remove_node_list = None
        self.set_text = None

    def next_color(self):
        self.h += self.golden_ratio_conjugate
        self.h %= 1
        return hsv_to_rgb(self.h, .5, .95)

    async def scan(self):
        async with TelegramClient('anon', self.api_id, self.api_hash) as client:

            self.set_text({'id': 'date-time', 'text': self.from_date.strftime("%d-%m-%Y %H:%M:%S")})
            self.set_text({'id': 'depth', 'text': self.max_depth})

            channels = []

            channels.append(*(await asyncio.gather(client.get_entity(self.start_channel))))
            channels_dict = {}
            channels_dict[channels[0].id] = {
                'out': [],
                'in': [],
                'msg_count': -1,
                'users': {},
                'title': channels[0].title,
                'depth': 0,
                'color': '#000000'
            }

            c_max = 10
            channel_idx = 0
            date_time = datetime.datetime.now(datetime.timezone.utc)
            curr_channel = channels[0]

            print("Starting channels:")
            for ch_ in channels:
                print(ch_.title if hasattr(ch_, 'title') else ch_.first_name)
                self.update({
                    'nodes': [{
                        'id': ch_.id,
                        'label': ch_.title,
                        'size': 10,
                        'color': {
                            'border': '#ff0000'
                        }
                    }],
                    'edges': []
                })
                self.add_node_list({'label': ch_.title})
            print("")
            print("New channel: " + curr_channel.title if hasattr(curr_channel, 'title') else curr_channel.first_name)
            while True:
                hist = (await asyncio.gather(client(get_history(curr_channel, date_time))))[0]

                channels_dict[curr_channel.id]['msg_count'] = hist.count

                for user in hist.users:
                    channels_dict[curr_channel.id]['users'][user.id] = user.first_name

                for msg in hist.messages:
                    if msg.date < self.from_date:
                        date_time = msg.date
                        break
                    if msg.fwd_from and hasattr(msg.fwd_from.from_id, 'channel_id'):
                        try:
                            ch_ = (await asyncio.gather(client.get_entity(msg.fwd_from.from_id)))[0]
                        except ChannelPrivateError:
                            continue

                        if channels_dict[curr_channel.id]['depth'] < self.max_depth and ch_ not in channels:
                            channels.append(ch_)
                            print("New channel found: " + ch_.title)
                            self.add_node_list({'label': ch_.title})

                        if ch_.id not in channels_dict.keys():
                            channels_dict[ch_.id] = {
                                'out': [curr_channel.id],
                                'in': [],
                                'msg_count': -1,
                                'users': {},
                                'title': ch_.title,
                                'depth': channels_dict[curr_channel.id]['depth'] + 1,
                                'color': '#000000'
                            }
                        else:
                            if channels_dict[ch_.id]['depth'] > channels_dict[curr_channel.id]['depth'] + 1:
                                channels_dict[ch_.id]['depth'] = channels_dict[curr_channel.id]['depth'] + 1
                            channels_dict[ch_.id]['out'].append(curr_channel.id)

                        channels_dict[curr_channel.id]['in'].append(ch_.id)

                        c = len(channels_dict[ch_.id]['out'])

                        if c > 1 and channels_dict[curr_channel.id]['color'] == '#000000':
                            channels_dict[curr_channel.id]['color'] = "#%02x%02x%02x" % self.next_color()

                        # color = "#%02x%02x%02x" % color_gradient(int(np.interp(c, [1, c_max], [0, 1])))

                        data = {
                            'nodes': [{
                                'id': ch_.id,
                                'label': ch_.title,
                                'size': math.pow(len(channels_dict[ch_.id]['out']), 1 / 1.9) + 10
                            }],
                            'edges': [{
                                'id': '{}{}'.format(curr_channel.id, ch_.id),
                                'from': ch_.id,
                                'to': curr_channel.id,
                                'color': channels_dict[ch_.id]['color']
                                if c > len(channels_dict[curr_channel.id]['out'])
                                else channels_dict[curr_channel.id]['color']
                            }]
                        }

                        self.update(data)

                if len(hist.messages) < 100 or date_time < self.from_date:
                    channel_idx += 1
                    self.remove_node_list()

                    if channel_idx >= len(channels):
                        self.update({
                            'nodes': [
                                {
                                    'id': curr_channel.id,
                                    'color': {
                                        'border': '#0000ff'
                                    }
                                }]
                        })
                        break

                    self.update({
                        'nodes': [
                            {
                                'id': curr_channel.id,
                                'color': {
                                    'border': '#0000ff'
                                }
                            },
                            {
                                'id': channels[channel_idx].id,
                                'color': {
                                    'border': '#ff0000'
                                }
                            }]
                    })
                    date_time = datetime.datetime.now(datetime.timezone.utc)
                    curr_channel = channels[channel_idx]
                    print("")
                    print("New channel: " + curr_channel.title if hasattr(curr_channel,
                                                                          'title') else curr_channel.first_name)
                else:
                    date_time = hist.messages[-1].date

    def run(self):
        # sleep(5)
        #
        # self.update({
        #     'nodes': [{
        #         'id': 15,
        #         'label': "ch_.title"
        #     }],
        #     'edges': [{
        #         'id': '{}{}'.format(15, 1),
        #         'from': 1,
        #         'to': 15
        #     }]
        # })

        sleep(5)
        asyncio.run(self.scan())

import datetime
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest

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

    user_name = 'Daddy'
    user_id = None
    user = None

    from_date = datetime.datetime(2021, 1, 15, 0, 0, 0, 0, datetime.timezone.utc)



    for dialog in client.iter_dialogs():
        if dialog.name == user_name:
            user_id = dialog.id
            user = client.get_entity(user_id)
            print(user_name, 'has ID', user_id)
            channels.append(user)

    channels.append(client.get_entity(start_channel))

    # client(JoinChannelRequest(entity))

    msgs = []

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

        for msg in hist.messages:
            if msg.sender_id == user_id:
                out = str(msg.date) + " -> msg found!"
                msgs.append(msg)
                if msg.fwd_from and hasattr(msg.fwd_from.from_id, 'channel_id'):
                    ch_ = client.get_entity(msg.fwd_from.from_id)
                    out += " Forwarded from: " + ch_.title
                    if ch_ not in channels:
                        channels.append(ch_)
                print(out)

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

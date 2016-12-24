
import os, time, shlex, random

from slackclient import SlackClient


BOT_NAME = 'horatiobot'
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose

slack_client = SlackClient(SLACK_BOT_TOKEN)


RANDOM_LINES = (
    ('The victim was found at the end of the road. It looks like', 'it was a dead end'),
    ('The band was killed during the concert. It looks like', "it wasn't a live performance"),
    ('He was killed with a shovel. It looks like another case', 'to dig up'),
)


def get_bot_id(name, call):
    """Retrieves a bot's ID string."""
    if call.get('ok'):
        users = call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == name:
                return user.get('id')
        raise Exception('Could not find bot user with the name ' + name)
    raise Exception('API call is invalid')


def at_bot(bot_id):
    """Retrieves a bot's @ string."""
    return '<@' + bot_id + '>'


def parse_slack_output(slack_rtm_output, bot_id):
    """This parsing function returns None, None unless a message is directed at the Bot."""
    if slack_rtm_output:
        for output in slack_rtm_output:
            if 'text' in output and at_bot(bot_id) in output['text']:
                command = output['text'].split(at_bot(bot_id))[1].strip()
                channel = output['channel']
                return command, channel
    return None, None


def handle_command(command, channel):
    """Receives commands directed at the bot and determines if they are valid commands.

    It so, then acts on the command. If not, returns a random message.

    """
    command_list = shlex.split(command)
    if len(command_list) == 1:
        set_up = 'I guess you could say'
        punchline = command_list[0]
    elif len(command_list) == 2:
        set_up = command_list[0]
        punchline = command_list[1]
    else:
        set_up, punchline = random.choice(RANDOM_LINES)
    response = '%s.. \n ( •__•)    ( •__•)>⌐■--■    (⌐■__■) \n ..*%s*' % (set_up, punchline)
    slack_client.api_call('chat.postMessage', channel=channel, text=response, as_user='true')


def connect_and_listen(bot_id):
    """The main loop for horatiobot to listen for command events."""
    if slack_client.rtm_connect():
        print('horatiobot connected and listening!')
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read(), bot_id)
            if channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        raise Exception('Connection fails. Invalid Slack token or bot ID?')


if __name__ == '__main__':
    api_call = slack_client.api_call('users.list')
    bid = get_bot_id(BOT_NAME, api_call)
    connect_and_listen(bid)

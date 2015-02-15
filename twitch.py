import socket  # imports module allowing connection to IRC
import threading  # imports module allowing timing functions
import ConfigParser  # imports module allowing permanent configuration
import time

# adds variable to allow easier use of the config parser
parser = ConfigParser.SafeConfigParser()

config = 'config.txt'
commands = 'commands.txt'

parser.read(config)

try:
    open(config, 'r+')
except IOError:
    config_ = open(config, 'w+')
    parser.add_section('This is the config file')

try:
    open(commands, 'r+')
except IOError:
    commands_ = open(commands, 'w+')
    commands_.write('This is for storage of custom commands.'
                    ' DO NOT DELETE THIS unless you want to lose all your custom commands.\n')
    commands_.close()

# Creates Config For The Logs If Not Generated
if not parser.has_section('Logs'):
    parser.add_section('Logs')
    parser.set('Logs', '# Debug is mostly for internal use, it shows a large amount of internal data. Default', 'False')
    parser.set('Logs', 'Debug', 'False')
    parser.set('Logs', '# IRC log displays whats being sent between the irc server and bot. Default', 'True')
    parser.set('Logs', 'IRC log', 'True')
    parser.write(open(config, 'r+'))
    print 'generated Logs Config'

# Creates Config For The Login Details If Not Generated
if not parser.has_section('Login Details'):
    parser.add_section('Login Details')
    parser.set('Login Details', '# Bot Username is the name you choose for the bot to be,for twitch you need to '
                                'create an account for the bot.', '')
    parser.set('Login Details', 'Bot Username', '')
    parser.set('Login Details', '# Bot Owner is usually the same as Bot Username,', '')
    parser.set('Login Details', '# but can be linked to another account', '')
    parser.set('Login Details', 'Bot Owner', '')
    parser.set('Login Details', '# Channel is what channel you want the bot to be in.', '')
    parser.set('Login Details', '# type #username of the channel for twitch', '')
    parser.set('Login Details', 'Channel', '')
    parser.set('Login Details', '# oAuth. for twitch channels you can find', '')
    parser.set('Login Details', '# the oauth of the BOT USERNAME here: http://twitchapps.com/tmi/', '')
    parser.set('Login Details', '# for non twitch uses just use the server password ', '')
    parser.set('Login Details', 'oAuth', '')
    parser.set('Login Details', '# Server where you want the bot to connect. it is set to twitch by default', '')
    parser.set('Login Details', '# but you can change it to any irc server to push the bot there', '')
    parser.set('Login Details', 'Server', 'irc.twitch.tv')
    parser.write(open(config, 'r+'))
    print 'Generated Login Details'

if not parser.has_section('Optional Login Details'):
    parser.add_section('Optional Login Details')
    parser.set('Optional Login Details', '# "Is Bot Name Turbo" is currently not used for anything.', '')
    parser.set('Optional Login Details', 'Is Bot Name Turbo', 'False')
    parser.write(open(config, 'r+'))
    print 'generated Optional Login Details Config'


if not parser.has_section('Aesthetic'):
    parser.add_section('Aesthetic')
    parser.set('Aesthetic', '# "Color" Sets the color of bot in chat for twitch. Normal users can', '')
    parser.set('Aesthetic', '# choose between Blue, Coral, DodgerBlue, SpringGreen, YellowGreen, Green,', '')
    parser.set('Aesthetic', '# OrangeRed, Red, GoldenRod, HotPink, CadetBlue, SeaGreen, Chocolate, BlueViolet,', '')
    parser.set('Aesthetic', '# and Firebrick. Twitch Turbo users can use any Hex value (i.e: #000000). ', '')
    parser.set('Aesthetic', 'Color', '')
    parser.write(open(config, 'r+'))
    print 'Generated Aesthetics config'
    print 'Generated Config please fill in.'
    exit()


# Reads Config For Logs
if parser.has_section('Logs'):
    global debug
    global irc_log
    debug = parser.getboolean('Logs', 'Debug')
    irc_log = parser.getboolean('Logs', 'IRC log')
    if debug:
        print 'debug: ', debug
        print 'IRC log: ', irc_log


# Reads Config For Login
if parser.has_section('Login Details'):
    global bot_username
    global botOwner
    global channel
    global oAuth
    global server
    bot_username = parser.get('Login Details', 'Bot Username')
    botOwner = parser.get('Login Details', 'Bot Owner')
    channel = parser.get('Login Details', 'Channel')
    oAuth = parser.get('Login Details', 'oAuth')
    server = parser.get('Login Details', 'Server')
    if server == 'irc.twitch.tv':
        channel = '#' + channel.lower()
    if debug:
        print 'botUsername: ', bot_username
        print 'botOwner: ', botOwner
        print 'channel: ', channel
        print 'oAuth: ', oAuth
        print 'server: ', server


if parser.has_section('Optional Login Details'):
    global turbo
    turbo = parser.getboolean('Optional Login Details', 'Is Bot Name Turbo')
    if debug:
        print 'Is Turbo = ', turbo


if parser.has_section('Aesthetic'):
    global default_color
    default_color = parser.get('Aesthetic', 'Color')
    if debug:
        print 'Default Color = ', default_color

irc = socket.socket()

irc.connect((server, 6667))  # connects to the server
irc.send('PASS ' + oAuth + '\r\n')
irc.send('NICK ' + bot_username + '\r\n')  # Send our Nick
irc.send('USER ' + bot_username + ' 0 * :' + botOwner + '\r\n')  # Send User Info to the server
irc.send('JOIN ' + channel + '\r\n')  # Join the pre defined channel
# irc.send('CHAT_LOGIN ' + oAuth + '\r\n')
if debug:
    print 'Login Process Complete'

queue = 5

if server == 'irc.twitch.tv':
    m_max = 17
else:
    m_max = 1000


# function for sending messages to the IRC chat
def message(msg):
    global queue
    queue += 1
    if debug:
        print 'queued', queue
    if queue < m_max:  # ensures does not send >20 msgs per 30 seconds if not mod. Almost un-limits if not twitch server
        irc.send('PRIVMSG ' + channel + ' :' + msg + '\r\n')
        if debug:
            print 'Sent: ', msg
    else:
        if debug:
            print 'Deleted: ', msg


# function for resetting the queue every 30 seconds
def queue_timer():
    global queue
    if debug:
        print 'queue reset'
    queue = 0
    threading.Timer(m_max, queue_timer).start()

queue_timer()
message('.color ' + default_color)


while True:
    data = irc.recv(1024)  # gets output from IRC server
    data_upper = data.upper()
    user_ = data.split(':')[1]
    user = user_.split('!')[0]  # determines the sender of the messages
    if irc_log:
        print data

    if m_max == 17:
        time.sleep(2)
        if m_max == 17:
            message('.mods')
            time.sleep(1)

    if data_upper.find('ARE: ') != -1:
        ms = data_upper.split('ARE: ')[1]
        if ms.find(bot_username.upper()) != -1:
            m_max = 100
            if debug:
                print 'm_max = ', 100
        else:
            m_max = 20
            if debug:
                print 'm_max = ', 20

    if data_upper.find('PING') != -1:
        irc.send(data_upper.replace('PING', 'PONG'))

    # Command To Add Commands, case sensitive
    if data_upper.find('!CMD+') != -1:
        try:
            cmd_line = data.split('!CMD+ ')[1]
            commands_ = open(commands, 'a')
            cmd = cmd_line.split(' ')[0]
            if cmd not in open(commands).read():
                commands_.write('!' + cmd_line)
                if debug:
                    print 'Command Added'
            else:
                message(cmd + ' is already a command.')
                print 'Already a Command'
            commands_.close()
            if debug:
                cmd_text = cmd_line.split(' +')[1]
                print '!CMD+'
                print 'cmd line =', cmd_line
                print 'cmd =', cmd
                print 'cmd text =', cmd_text
        except IndexError:
            message('Make sure "!CMD+" is in capitals. Usage: !CMD+ cmd_name +cmd_contents')

    if data_upper.find('!CMD~') != -1:
        try:
            cmd_line = data.split('!CMD~ ')[1]
            cmd = cmd_line.split(' ')[0]
            cmd_text = cmd_line.split(' ~')[1]
            if debug:
                print '!CMD~'
                print 'cmd line =', cmd_line
                print 'cmd =', cmd
                print 'cmd text =', cmd_text
        except IndexError:
            message('Make sure "!CMD~" is in capitals. Usage: !CMD~ cmd_name ~cmd_contents')

    # command to remove commands, case sensitive
    if data_upper.find('!CMD-') != -1:
        try:
            cmd_line = data.split('!CMD- ')[1]
            cmd = cmd_line.split(' ')[0]
            commands_ = open(commands, 'w+')
            commands_.find(cmd)
            if debug:
                print '!CMD-'
                print 'cmd line =', cmd_line
                print 'cmd =', cmd
        except IndexError:
            message('Make sure "!CMD-" is in capitals. Usage: !CMD- cmd_name')

    if data_upper.find('!PING') != -1:  # !test command
        message('Pong')
    # changes name color and prints color name
    if data_upper.find('!RAINBOW') != -1:
        message('.color Red')
        message('.me Red')
        message('.color OrangeRed')
        message('.me Orange')
        message('.color GoldenRod')
        message('.me Yellow')
        message('.color SpringGreen')
        message('.me Green')
        message('.color Blue')
        message('.me Blue')
        message('.color BlueViolet')
        message('.me Violet')
        message('.color ' + default_color)

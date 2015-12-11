from __future__ import print_function
from base64 import b64encode
import socket
import ssl

def connectAndIdentify():

    server = "chat.freenode.net"
    port = 6697
    channels = ["##BWBellairs", "##powder-bots", "#botters-test"]
    botnick = "BWBellairs[Bot]"
    realname = "BWBellairs[Bot]"
    ident = "BWBellairs[Bot]"
    use_ssl = True
    use_sasl = True
    password = raw_input("Enter password")
    username = "BWBellairs[Bot]"
    command = "$None$"
    nickname = "BWBellairs[Bot]"

    global irc

    irc = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # defines the socket
    if use_ssl:
        irc = ssl.wrap_socket(sock)
    else:
        irc = sock

    print("connecting to: " + server)
    irc.connect((server, port))  # connects to the server

    if use_sasl:
        saslstring = b64encode("{0}\x00{0}\x00{1}".format(
                	username, password).encode("UTF-8")) 
        irc.send("CAP REQ :sasl\r\n".format("UTF-8"))
        irc.send("USER {0} {1} blah :{2}\r\n".format(
                ident, botnick, realname).encode("UTF-8"))
        irc.send("NICK {0}\r\n".format(botnick).encode("UTF-8"))
        irc.send("AUTHENTICATE PLAIN\r\n".encode("UTF-8"))
        irc.send("AUTHENTICATE {0}\r\n".format(saslstring).encode(
                "UTF-8"))
	authed = confirmsasl()
	if authed:
                irc.send("CAP END\r\n".encode("UTF-8"))
        else:
                print("SASL aborted. exiting.")
                irc.send("QUIT\r\n")
                irc.shutdown(2)
                exit()
    else:
        irc.send("USER {0} {1} blah :{2}\r\n".format(
                ident, botnick, realname).encode("UTF-8"))  # user authentication
        irc.send("NICK {0}\r\n".format(botnick).encode("UTF-8"))  # sets nick
        irc.send("PRIVMSG nickserv :identify {0} {1}\r\n".format(
                username, password).encode("UTF-8"))  # auth

    irc.send("JOIN {0}\r\n".format(",".join(channels)).encode("UTF-8"))  # join the channel(s)

def confirmsasl():
    while True:
        ircmsg = irc.recv(2048)
        ircmsg = ircmsg.split()
        print(ircmsg)
        ircmsg = " ".join(ircmsg)
        success = ":SASL authentication successful"
        failure = ":SASL authentication aborted"
        if success in ircmsg:
                return True
        elif failure in ircmsg:
                return False

def recieve(commandNone = False):

    global t, nickname, hotmask, msg_type, chan, message, command, args
    
    binary_data = irc.recv(1024)
    # Decode data from UTF-8
    #data = binary_data.decode("UTF-8", "ignore")
    data = binary_data
    # Split data by spaces
    t = data.replace(":", "")#.split()
    t = t.split()
    return t

def ircSend(typeM, chan = None, nickname = None, *args):
    try:
        if typeM == "priv":
            irc.send("PRIVMSG {0} :{1} {2}\r\n".format(chan, nickname or args, args or "").encode("UTF-8"))

        elif typeM == "quit":
            irc.send("QUIT {0} :{1}\r\n".format(chan, nickname, args or "GoodBye").encode("UTF-8"))

        elif typeM == "join":
            irc.send("JOIN {0}\r\n".format(chan).encode("UTF-8"))

        elif typeM == "topic":
            irc.send("TOPIC " + chan + ":" + " ".join(args) + "\r\n".encode("UTF-8"))

        elif typeM == "notice":
            irc.send("notice " + chan + ":" + " ".join(args) + "\r\n".encode("UTF-8"))
    except:
        pass
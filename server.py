# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
An example IRC log bot - logs a channel's events to a file.

If someone says the bot's name in the channel followed by a ':',
e.g.

    <foo> logbot: hello!

the bot will reply:

    <logbot> foo: I am a log bot

Run this script with two arguments, the channel name the bot should
connect to, and file to log to, e.g.:

    $ python ircLogBot.py test test.log

will log channel #test to the file 'test.log'.

To run the script:

    $ python ircLogBot.py <channel> <file>
"""


# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
import random

# system imports
import time, sys

#emoji dictioanry
dictf = open("meow_emoji.dict",'r');
emojilist = [];
for line in dictf:
    emojilist.append(line)

# print emojilist
dictf.close()

class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class LogBot(irc.IRCClient):
    """A logging IRC bot."""
    
    nickname = "catbotuiuc"
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))


    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))
        self.logger.close()


    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        print("Signed On")
        self.join(self.factory.channel)    


    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        print("joinned")
        self.logger.log("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            # message = "It isn't nice to whisper!  Play nice with the group."
            # self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        # if msg.startswith(self.nickname + ":"):
        #     msg = "%s: I am a log bot" % user
        #     self.msg(channel, msg)
        #     print("<%s> %s" % (self.nickname, msg))

        wordlist = msg.split()
        if "cat" in wordlist:
            self.logger.log("<%s> %s" % (user, msg))
            if (random.randint(0,15)==1): #make sure it only gets called with a chance of 1/15
                msg = "meow "+emojilist[random.randint(0,len(emojilist)-1)];
                self.msg(channel,msg)
                self.logger.log("<%s> %s" % (self.nickname, msg))
                return
            return

    def kickedFrom(self, channel, kicker, message):
        self.logger.log("I was kicked from %s" % channel)
        print("I was kicked from %s" % channel)
        return

    def left(self, channel):
        self.logger.log("I left %s" % channel)
        print("I left %s" % channel)
        return

    def quit(self, message=''):
        self.logger.log("I quit the server")
        print("I quit the server")
        return

    def myInfo(self, servername, version, umodes, cmodes):
        print("server name: %s v: %s umodes: %s cmodes: %s" % (servername,version,umodes,cmodes))

    # def action(self, user, channel, msg):
    #     """This will get called when the bot sees someone do an action."""
    #     user = user.split('!', 1)[0]
    #     print("* %s %s" % (user, msg))

    # irc callbacks

    # def irc_NICK(self, prefix, params):
    #     """Called when an IRC user changes their nickname."""
    #     old_nick = prefix.split('!')[0]
    #     new_nick = params[0]
    #     print("%s is now known as %s" % (old_nick, new_nick))


    # # For fun, override the method that determines how a nickname is changed on
    # # collisions. The default method appends an underscore.
    # def alterCollidedNick(self, nickname):
    #     """
    #     Generate an altered version of a nickname that caused a collision in an
    #     effort to create an unused related name for subsequent registration.
    #     """
    #     return nickname + '^'



class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel):
        self.channel = channel
        self.filename = "1.log"

    def buildProtocol(self, addr):
        p = LogBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)
    
    # create factory protocol and application
    f = LogBotFactory(sys.argv[1])



    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # run bot
    reactor.run()
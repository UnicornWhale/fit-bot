# -*- coding: utf-8 -*-

import sys
import socket
import string
from settings import host, port, chan


class FitBot(object):
    logged_in = False
    nick = "FitBot"
    ident = "fitbot"
    realname = "PFB"
    readbuffer = ""
    fit_file = 'fits.txt'
    fit_list = []

    def run(self):
        #Get fits from the fits file
        print('Reading Fits')
        self.fit_list = read_fits()

        #Connect to the irc server specified
        inputs = get_inputs()
        connect_to_server(inputs)
        print 'Connected.'

        #Begin operations
        read_loop()

    def get_inputs(self):
        """If the necessary components are not specified in the settings file, ask the user for them"""
        if not host:
            host = input('What server -> ')
        if not port:
            port = int(input('What port -> '))
        if not chan:
            chan = input('What channel -> ')
        return (host, port, chan)

    def read_fits(self):
        """Get fits from the fits file"""
        fits = open(self.fit_file, 'r')

        result = []
        for line in fits:
            result.append(line)
        return result

    def connect_to_server(self):
        """Connect to the IRC server"""
        self.irc=socket.socket()
        self.irc.connect((host, port))
        self.irc.send("nick %s\r\n" % self.nick)
        self.irc.send("USER %s %s bla :%s\r\n" % (self.ident, host, self.realname))

    def read_loop(self):
        """
        Infinite loop of reading everything people say on the server, and checking to see if it contains
        commands. If there is a command, respond to it appropriately
        """
        while True:
            readbuffer = readbuffer+self.irc.recv(1024)
            temp = string.split(readbuffer, "\n")
            readbuffer = temp.pop()

            for line in temp:
                line = string.rstrip(line)
                line = string.split(line)

                join_channel_if_necessary(line)
                respond_to_commands(line)

    def join_channel_if_necessary(self, line):
        """Check if logged in to the channel, if not then log in"""
        if line[1] == 'MODE' and not self.logged_in:
            self.irc.send("JOIN %s\r\n" % chan)
            self.irc.send('PRIVMSG ' + chan + ' :Hello.\r\n')
            self.logged_in = True

        if line[0] == "PING":
            self.irc.send("PONG %s\r\n" % line[1])

    def respond_to_commands(self, line):
        """Check the given line for a command and if there is one, respond to it properly"""
        if self.logged_in and len(line) > 3:
            command = line[3:] #Get rid of protocol parts and get actual content

            #Command to display fits
            if command[0] == ':!fit':
                lines = []
                adding = False

                #Get args from command
                if len(command) > 1:
                    ship_name = command[1]
                    if len(command) > 2:
                        for word in command[2:]:
                            ship_name = ship_name + ' ' + word

                    #Find fit of specified ship in the fits.txt file
                    for line in fit_list:
                        if line[1:line.find(',')].lower() == ship_name.lower(): #Begin adding at first line of fit
                            adding = True
                        elif line[0] == '[' and line[0:6] != '[Empty': #End adding at first line of next fit
                            adding = False
                        if adding:
                            lines.append(line)

                #Respond to command with no args
                if len(lines) == 0:
                    self.irc.send('PRIVMSG ' + chan + ' :Please include a ship name (!fit Brutix for example) \r\n')
                #Send the asked for ship fit
                else:
                    for line in lines:
                        if line == '\n':
                            self.irc.send('PRIVMSG ' + chan + ' : \r\n')
                        else:
                            self.irc.send('PRIVMSG ' + chan + ' :%s\r\n' % line)

            if command[0] == ':!help':
                self.irc.send('PRIVMSG ' + chan + ' :To use fit bot, type !fit followed by a ship name.\r\n')
                self.irc.send('PRIVMSG ' + chan + ' :Example: !fit Brutix\r\n')

def main():
    fitbot = FitBot()
    fitbot.run()

#Boilerplate to call main()
if __name__ == '__main__':
    main()

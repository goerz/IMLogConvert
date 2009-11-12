# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2009 by Michael Goerz                                   #
#    http://www.physik.fu-berlin.de/~goerz                                 #
#                                                                          #
#    This program is free software; you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

""" 
This module contains two classes: one to describe a IM Conversations and on
to describe an individual Instant Message.
"""
from IMLogConvert.Conversation import Conversation, Message, StatusMessage
from xml.sax import make_parser, ContentHandler
import IMLogConvert.Time
import sys

class AdiumReader:
    """ Reader for Adium Logs  """
    def __init__(self):
        """ Initialize Reader """
        self.alias_replacements = {}
        self.service_replacements = {}

    def read(self, filename_or_stream):
        """ Fill the conversation with data from the XML in the
            filename_or_stream
        """
        conversation = Conversation()
        parser = make_parser()
        parser.setContentHandler(AdiumContentHandler(conversation))
        try:
            parser.parse(filename_or_stream)
        except Exception, data:
            print >> sys.stderr, \
            "There was a fatal error in parsing the xml file:\n%s" % data
            sys.exit()
        for (account, alias) in conversation.participants.items():
            if self.alias_replacements.has_key(alias):
                conversation.participants[account] \
                = self.alias_replacements[alias]
        if self.service_replacements.has_key(conversation.service):
            conversation.service \
            = self.service_replacements[conversation.service]
        return conversation


class AdiumContentHandler(ContentHandler):
    """ ContentHandler for XML Parser. Construct a Conversation from Adium Log
        XML 
    """
    def __init__(self, conversation):
        """Initialize parser state variables """
        self.conversation = conversation
        self.open_element = ""
        self.buffer = {}
    def startElement(self, name, attrs):
        """Hook for opening XML tags """
        if name == "chat":
            self.conversation.service = attrs.get("service", None)
            self.conversation.account = attrs.get("account", None)
            self.conversation.start_time = None
            self.conversation.timezone = None
            self.conversation.participants = {}
            self.conversation.messages = []
        if name in ["message", "status", "event"]:
            self.open_element = name
            time_str = attrs.get("time", None)
            self.buffer['time'] =  time_str[:-6]
            self.buffer['timezone'] = time_str[-6:-3] + time_str[-2:]
            self.buffer['sender'] = attrs.get("sender", None)
            self.buffer['alias'] = attrs.get("alias", None)
            self.buffer['type'] = attrs.get("type", None)
            if self.conversation.timezone is None:
                self.conversation.timezone = self.buffer['timezone']
            if self.conversation.start_time is None:
                self.conversation.start_time = IMLogConvert.Time.tz_strpmktime(
                        self.buffer['time'], '%Y-%m-%dT%H:%M:%S', 
                        self.conversation.timezone)
        if name in ["message", "status", "event"]:
            self.buffer['text'] = ''
        if name == 'br':
            self.buffer['text'] += "\n"
    def characters(self, content):
        """Hook for XML text data """
        if self.open_element in ["message", "status", "event"]:
            self.buffer['text'] += content
    def endElement(self, name):
        """Hook for closing XML tags """
        if name in ["message", "status", "event"]:
            text = self.buffer['text']
            if text is None:
                text = ''
            time = IMLogConvert.Time.tz_strpmktime(
                    self.buffer['time'], '%Y-%m-%dT%H:%M:%S', 
                    self.buffer['timezone'])
            sender = self.buffer['sender']
            if sender is not None:
                if self.buffer['alias'] is None:
                    self.conversation.participants[sender] \
                    = sender
                else:
                    self.conversation.participants[sender] \
                    = self.buffer['alias']
            if name == "message":
                message = Message(time, sender, text)
            else:
                if text == '':
                    if (self.buffer['alias'] is not None 
                    and self.buffer['type'] is not None):
                        text = "%s became %s" % (self.buffer['alias'], 
                                                 self.buffer['type'])
                if text == '':
                    message = None
                else:
                    message = StatusMessage(time, text)
            if message is not None:
                self.conversation.messages.append(message)
            self.open_element = ""


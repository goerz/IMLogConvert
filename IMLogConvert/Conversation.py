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
from xml.sax import saxutils, make_parser, ContentHandler
import IMLogConvert.Time
from time import gmtime
import sys
import codecs

class Conversation:
    """ Instant Message Conversation. A conversation is characterized by the
        'service', 'account', and 'start_time' fields as explained in the
        documentation of the constructor. In addition, there is a
        'participants' dictionary, which should contain the usernames of all
        participants in the conversation as keys, and their aliases (real
        names) as values, and an array 'messages' that contains all the
        individual messages (Message/StatusMessage) that are part of the
        conversation, ordered by time.
    """
    def __init__(self, service=None, account=None, 
                 start_time=None, timezone=''):
        """ Initialize a conversation with the given service, account,
            start_time, and timezoone.  'service' is a string describing the IM service or
            protocol that was used in the conversation. 'account' is the
            username of the person recording the conversation. 'start_time' is
            the time in epoch seconds at which the conversation was initiated.
            'timezone' is the time zone offset (e.g. '+0100') of the time zone
            the conversation took place in.
        """
        self.service = service
        self.account = account
        self.start_time = start_time
        self.timezone = timezone
        self.participants = {}
        self.messages = []

    def to_xml(self, filename=None):
        """ Return an XML file representing the conversation as a UTF-8 encoded
            string. If filename is given, write the xml to file.
        """
        result  = r'<?xml version="1.0" encoding="utf-8"?>'+"\n"
        result += \
        "<conversation service=%s account=%s start_time=%s timezone=%s>\n" % (
        saxutils.quoteattr(self.service).encode('utf-8'),
        saxutils.quoteattr(self.account).encode('utf-8'),
        saxutils.quoteattr( IMLogConvert.Time.tz_strftime(
          '%a %d %b %Y %H:%M:%S', self.start_time, self.timezone, 
          append_offset=False)),
        saxutils.quoteattr(str(self.timezone)) )
        result += r'  <participants>' + "\n"
        for participant in self.participants.keys():
            result += "    <participant alias=%s>%s</participant>\n" % (
                      saxutils.quoteattr(
                          self.participants[participant]).encode('utf-8'),
                      saxutils.escape(participant).encode('utf-8'),
                      )
        result += r'  </participants>' + "\n"
        result += r'  <messages>' + "\n"
        for message in self.messages:
            result += r'    ' + message.to_xml(self.timezone) + "\n"
        result += r'  </messages>' + "\n"
        result += r'</conversation>'
        if filename is not None:
            outfile = open(filename, 'w')
            outfile.write(result)
            outfile.close()
        return result

    def from_xml(self, filename_or_stream):
        """ Fill the conversation with data from the XML in the
            filename_or_stream
        """
        parser = make_parser()
        parser.setContentHandler(ConversationContentHandler(self))
        try:
            parser.parse(filename_or_stream)
        except Exception, data:
            print >> sys.stderr, \
            "There was a fatal error in parsing the xml file:\n%s" % data
            sys.exit()

    def filename(self):
        """ Generate a generic filename for the conversation, like
            2007_03_20_164955_icq_John_Doe.xml
        """
        timetuple = gmtime(self.start_time)
        name = 'noname'
        service = self.service
        service = service.replace("/", "")
        service = service.replace(" ", "_")
        for (account_name, alias) in self.participants.items():
            if account_name != self.account:
                name = alias
                name = name.replace(u"ö", "oe")
                name = name.replace(u"ä", "ae")
                name = name.replace(u"ü", "ue")
                name = name.replace(u"ß", "ss")
                name = name.replace(u"Ö", "Oe")
                name = name.replace(u"Ä", "Ae")
                name = name.replace(u"Ü", "ue")
                name = name.replace(u":", "")
                name = name.replace(u"/", "_")
                name = name.replace(u"\\", "_")
                name = name.replace(u"*", "")
                name = name.replace(u"?", "")
                name = name.replace(u"!", "")
                name = name.replace(u"|", "")
                name = name.replace(u" ", "_")
                name = codecs.encode(name, 'ascii', 'ignore')
                break
        outfilename = "%04i_%02i_%02i_%02i%02i%02i_%s_%s.xml" % (
        timetuple[0], timetuple[1], timetuple[2], timetuple[3],
        timetuple[4], timetuple[5], service, name
        )
        return outfilename


class Message:
    """
    Message that is part of a conversation. A message is characterized by the
    'time', 'sender', and 'text', as explained inthe documentation of the
    constructor.
    """
    def __init__(self, time=None, sender=None, text=None):
        """ Initialize a message with the given time, sender, and text.
            'time' is the time at wich the message was received in epoch
            seconds. 'sender' is the username of the person sending the
            message. 'text' is a unicode string containing the content of the
            message.
        """
        self.time = time
        self.sender = sender
        self.text = text
    def to_xml(self, timezone):
        """ Return a UTF-8 encoded string containing the message """
        return "<message time=%s sender=%s>%s</message>" % (
        saxutils.quoteattr( IMLogConvert.Time.tz_strftime(
          '%a %d %b %Y %H:%M:%S', self.time, timezone, append_offset=False)),
        saxutils.quoteattr(self.sender).encode('utf-8'),
        saxutils.escape(self.text).encode('utf-8') )

class StatusMessage(Message):
    """
    Status Message, . A message is characterized by the
    'time', and 'text', but no 'sender' as explained in the documentation of
    the constructor.
    """
    def __init__(self, time=None, text=None):
        """ Initialize a message with the given time and text.  'time' is the
             time at wich the message was received in epoch seconds. 'text' is
             a unicode string containing the content of the status message.
        """
        Message.__init__(self, time=time, text=text)
        self.time = time
        self.text = text
        del self.sender
    def to_xml(self, timezone):
        """ Return a UTF-8 encoded string containing the message """
        return "<status time=%s>%s</status>" % (
        saxutils.quoteattr( IMLogConvert.Time.tz_strftime(
          '%a %d %b %Y %H:%M:%S', self.time, timezone, append_offset=False)),
        saxutils.escape(self.text).encode('utf-8') )

class ConversationContentHandler(ContentHandler):
    """ ContentHandler for XML Parser. Construct a Conversation from XML """
    def __init__(self, conversation):
        """Initialize parser state variables """
        self.conversation = conversation
        self.open_element = ""
        self.buffer = {}
    def startElement(self, name, attrs):
        """Hook for opening XML tags """
        if name == "participant":
            self.open_element = name
            self.buffer['alias'] = attrs.get("alias", None)
            self.buffer['participant'] = ''
        if name == "conversation":
            self.conversation.service = attrs.get("service", None)
            self.conversation.account = attrs.get("account", None)
            self.conversation.timezone = attrs.get("timezone", None)
            self.conversation.start_time = IMLogConvert.Time.tz_strpmktime(
                    attrs.get("start_time", None), '%a %d %b %Y %H:%M:%S', 
                    self.conversation.timezone)
        if name == "message":
            self.open_element = name
            self.buffer['time'] = attrs.get("time", None)
            self.buffer['sender'] = attrs.get("sender", None)
            self.buffer['text'] = ''
        if name == "status":
            self.open_element = name
            self.buffer['time'] = attrs.get("time", None)
            self.buffer['text'] = ''
    def characters(self, content):
        """Hook for XML text data """
        if self.open_element == "participant":
            self.buffer['participant'] += content.strip()
        if self.open_element == "message":
            self.buffer['text'] += content
        if self.open_element == "status":
            self.buffer['text'] += content
    def endElement(self, name):
        """Hook for closing XML tags """
        if name == "participant":
            participant = self.buffer['participant'].strip()
            self.conversation.participants[participant] = self.buffer['alias']
            self.open_element = ""
        if name == "message":
            text = self.buffer['text']
            time = IMLogConvert.Time.tz_strpmktime(
                    self.buffer['time'], '%a %d %b %Y %H:%M:%S', 
                    self.conversation.timezone)
            sender = self.buffer['sender']
            message = Message(time, sender, text)
            self.conversation.messages.append(message)
            self.open_element = ""
        if name == "status":
            text = self.buffer['text']
            time = IMLogConvert.Time.tz_strpmktime(
                    self.buffer['time'], '%a %d %b %Y %H:%M:%S', 
                    self.conversation.timezone)
            message = StatusMessage(time, text)
            self.conversation.messages.append(message)
            self.open_element = ""


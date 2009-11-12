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
This module contains a class for writing Conversations in the Pidgin IM log
text format IM logs
"""
from IMLogConvert.Conversation import StatusMessage
import IMLogConvert.Time
import codecs

class PidginTextWriter:
    """ Reader for text format logs created by Pidgin
    """
    def __init__(self):
        """ Initialize the writer
        """
        self.encoding = 'utf-8'

    def write(self, conversation, filename):
        """ Writer a conversation to the given filename
        """
        fh = codecs.open(filename, 'w', self.encoding)
        contactname = ''
        for participant in conversation.participants.keys():
            if participant != conversation.account:
                contactname = participant
        fh.write("Conversation with %s " % contactname)
        fh.write("at %s " % IMLogConvert.Time.tz_strftime(
                            '%a %d %b %Y %I:%M:%S %p', 
                            conversation.start_time,
                            conversation.timezone))
        fh.write("on %s " % conversation.account)
        fh.write("(%s)\n" % conversation.service)
        for message in conversation.messages:
            msg_time_str = IMLogConvert.Time.tz_strftime('%I:%M:%S %p', 
                           message.time, conversation.timezone,
                           append_offset=False)
            if isinstance(message, StatusMessage):
                fh.write("(%s) %s\n" % (msg_time_str, message.text))
            else:
                sender = conversation.participants[message.sender]
                fh.write("(%s) %s: %s\n" % (msg_time_str, sender, message.text))
        
        fh.close()


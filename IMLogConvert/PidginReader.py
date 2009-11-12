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
This module contains a class for reading text format IM logs created by Pidgin
(or libpurple in general)
"""
from IMLogConvert.Conversation import Conversation, Message, StatusMessage
import IMLogConvert.Time
import re
import codecs


class PidginTextReader:
    """ Reader for text format logs created by Pidgin
    """
    def __init__(self, aliases):
        """ Initialize the reader.
            'alias' is the alias of the person who created the log, as it
            appears in the log.
        """
        self.aliases = aliases
        self.encoding = 'utf-8'
        self.alias_replacements = {}
        self.firstline_patterns = [
        re.compile(
        # Conversation with 345 at Mon 23 Jul 2006 03:59:08 PM on 123 (icq)
        r'''Conversation \s+ with \s+ (?P<contactname>[^/]+)(/[^()]+)? \s+
            at \s+  [A-Z][a-z]{2}
            \s+ (?P<time>
              (?P<date>[0-9]{2} \s+ [A-Za-z]+ \s+ [0-9]{4}) \s+ 
              [0-9]{1,2}:[0-9]{2}:[0-9]{2} (\s+ (AM|PM))?  
            ) \s+ 
            (?P<timezone>[+\-\dA-Z]+)?
            \s+ on \s+ (?P<account>[^/]+)(/(?P<resource>[^()]+))? \s+
            \((?P<service>[^()]+)\)''', re.X),
        re.compile(
        # Conversation with 345 at 2004-06-12 20:04:59 on 123 (icq)
        r'''Conversation \s+ with \s+ (?P<contactname>[^/]+)(/[^()]+)? \s+
            at \s+ (?P<time>
              (?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}) \s+ 
              [0-9]{1,2}:[0-9]{2}:[0-9]{2}
            ) 
            \s+ on \s+ (?P<account>[^/]+)(/(?P<resource>[^()]+))? \s+
            \((?P<service>[^()]+)\)''', re.X),
        re.compile(
        # Conversation with d78 at 8/15/2007 9:55:37 PM on mic (aim)
        r'''Conversation \s+ with \s+ (?P<contactname>[^/]+)(/[^()]+)? \s+
            at \s+ (?P<time>
              (?P<date>[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}) \s+ 
              [0-9]{1,2}:[0-9]{2}:[0-9]{2} (\s+ (AM|PM))?
            ) 
            \s+ on \s+ (?P<account>[^/]+)(/(?P<resource>[^()]+))? \s+
            \((?P<service>[^()]+)\)''', re.X),
        re.compile(
        # Conversation with 345 at 21.07.2007 16:35:21 on 123 (icq)
        r'''Conversation \s+ with \s+ (?P<contactname>[^/]+)(/[^()]+)? \s+
            at \s+ (?P<time>
              (?P<date>[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}) \s+ 
              [0-9]{2}:[0-9]{2}:[0-9]{2}
            ) 
            \s+ on \s+ (?P<account>[^/]+)(/(?P<resource>[^()]+))? \s+
            \((?P<service>[^()]+)\)''', re.X)
        ]
        self.msgline_pattern = re.compile(
        r'''^\(   (\d{2}/\d{2}/\d{4}\s+)?
                  (?P<time>[0-9]{1,2}:[0-9]{2}:[0-9]{2} [ ]? (AM|PM)?)
            \)[ ]
            (?P<alias>[^:]+):[ ] (?P<text>.*)''', re.X)
        self.status_pattern = re.compile(
        r'''^\(   (\d{2}/\d{2}/\d{4}\s+)?
                  (?P<time>[0-9]{1,2}:[0-9]{2}:[0-9]{2} [ ]? (AM|PM)?)
            \)[ ] (?P<text>.*)''', re.X)
        self.date_patterns = [
                r'%d %b %Y %H:%M:%S',    # 03 Apr 2008 23:10:54
                r'%d %b %Y %I:%M:%S %p', # 23 Jul 2006 03:59:08 PM
                r'%Y-%m-%d %H:%M:%S',    # 2004-06-12 20:04:59
                r'%d.%m.%Y %H:%M:%S',    # 12.06.2004 20:04:59
                r'%m/%d/%Y %I:%M:%S %p'  # 8/15/2007 10:55:37 PM
        ]
    def read(self, filename):
        """ Parse the contents of filename and create a conversation
        """
        fh = codecs.open(filename, 'r', self.encoding, errors='replace')

        # extract info from the first line
        firstline = fh.readline()
        start_time = None
        account = None
        service = None
        firstline_match = None
        for firstline_pattern in self.firstline_patterns:
            firstline_match = firstline_pattern.match(firstline)
            if firstline_match:
                break
        if firstline_match:
            try:
                timezone = str(firstline_match.group('timezone'))
                timezone = IMLogConvert.Time.tz_offset(timezone)
            except IndexError:
                # No time zone given, we have to guess
                timezone = ''
            time_str = firstline_match.group('time').strip()
            start_time = None
            for date_pattern in self.date_patterns:
                try:
                    start_time = IMLogConvert.Time.tz_strpmktime(time_str, 
                                 date_pattern, timezone)
                    used_date_pattern = date_pattern
                    break
                except ValueError:
                    pass
            if start_time is None:
                raise ValueError("'%s' does not match any date pattern (%s)" 
                                 % (time_str, filename))
            account = firstline_match.group('account')
            service = firstline_match.group('service')
            date_day = firstline_match.group('date')
        else:
            raise ValueError(
            "First line in %s does not match the expected pattern" % filename)
        contactname = firstline_match.group('contactname')
        conversation = Conversation(service, account, start_time)
        conversation.participants[account] = self.aliases[0]
        conversation.participants[contactname] = contactname
        conversation.timezone = timezone

        # go through the individual messages
        for line in fh:
            msgline_match = self.msgline_pattern.match(line)
            if msgline_match:
                is_status = False
                contactname_alias = msgline_match.group('alias')
                contactname_alias = contactname_alias.replace(
                ' <AUTO-REPLY>', '')
                for substring in [
                'The following message', 'TeXIM', 'Unable to send message', 
                'GaimTeX', 'OTR Error']:
                    if substring in contactname_alias:
                        is_status = True
                if not is_status:
                    message = Message()
                    time_str = date_day + ' ' + msgline_match.group('time')
                    try:
                        message.time = IMLogConvert.Time.tz_strpmktime(time_str,
                                       used_date_pattern, timezone)
                    except ValueError:
                        raise ValueError(
                        "'%s' does not match date pattern %s (%s)"
                        % (time_str, used_date_pattern, filename))
                    if message.time < conversation.start_time - 2*3600:
                        message.time += 24*3600
                    if message.time < conversation.start_time - 2:
                        if len(conversation.messages) == 0:
                            # time stamp on initial message trumps conversation
                            conversation.start_time = message.time
                        else:
                            raise ValueError(
                            "Nonsensical timestamp '%s' in %s" 
                            % (msgline_match.group('time'), filename))
                    if (msgline_match.group('alias') in self.aliases or
                    msgline_match.group('alias') == account): 
                        message.sender = account
                    else:
                        message.sender = contactname
                        conversation.participants[contactname] \
                        = contactname_alias
                    message.text = unicode(msgline_match.group('text'))
                    conversation.messages.append(message)
                    continue
            status_match = self.status_pattern.match(line)
            if status_match:
                message = StatusMessage()
                time_str = date_day + ' ' + status_match.group('time')
                try:
                    message.time = IMLogConvert.Time.tz_strpmktime(time_str, 
                                    used_date_pattern, timezone)
                except ValueError:
                    raise ValueError("'%s' does not match date pattern %s (%s)" 
                                    % (time_str, used_date_pattern, filename))
                if message.time < conversation.start_time - 2*3600:
                    message.time += 24*3600
                if message.time < conversation.start_time - 2:
                    if len(conversation.messages) == 0:
                        # time stamp on initial message trumps conversation
                        conversation.start_time = message.time
                    else:
                        raise ValueError("Nonsensical timestamp '%s' in %s" % (
                            status_match.group('time'), filename))
                message.text = unicode(status_match.group('text'))
                conversation.messages.append(message)
                continue
            # fall-through: append to last message
            if line.endswith("\n"):
                line = line[:-1]
            conversation.messages[-1].text += "\n" + unicode(line)
        for (account, alias) in conversation.participants.items():
            if self.alias_replacements.has_key(alias):
                conversation.participants[account] \
                = self.alias_replacements[alias]

        return conversation

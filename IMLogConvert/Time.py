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
Time utilities and data
"""
import time
import re

timezones = {
'ACDT' : '+1030', 'ACST' : '+0930', 'ADT' : '-0300', 'ADT'  : '-0400',
'AEDT' : '+1100', 'AES'  : '+1000', 'AEST': '+1000', 'AHDT' : '-0900',
'AHST' : '-1000', 'AKDT' : '-0800', 'AKST': '-0900', 'AST'  : '-0400',
'ASTU' : '-0300', 'AT'   : '+0200', 'AWDT': '+0900', 'AWST' : '+0800',
'BRA'  : '-0300', 'BST'  : '+0100', 'BT'  : '+0300', 'CAST' : '+0930',
'CDT'  : '-0500', 'CEST' : '+0200', 'CET' : '+0100', 'CETDS': '+0200',
'CST'  : '-0600', 'CSuT' : '+1030', 'DNT' : '+0100', 'DST'  : '+0200',
'EAST' : '+1000', 'EDT'  : '-0400', 'EES' : '+0300', 'EET'  : '+0200',
'EETDS': '+0300', 'EMT'  : '+0100', 'EST' : '-0500', 'ESuT' : '+1100',
'FDT'  : '-0100', 'FST'  : '+0200', 'FWT' : '+0100', 'GMT'  : '+0000',
'GST'  : '+1000', 'HADT' : '-0900', 'HAST': '-1000', 'HDT'  : '-0930',
'HFE'  : '+0200', 'HFH'  : '+0100', 'HKT' : '+0800', 'HOE'  : '+0100',
'HST'  : '-1000', 'IDLE' : '+1200', 'IDLW': '-1200', 'IDT'  : '+0430',
'IST'  : '+0530', 'IT'   : '+0330', 'ITA' : '+0100', 'JST'  : '+0900',
'JT'   : '+0730', 'KDT'  : '+1000', 'KST' : '+0900', 'LIGT' : '+1000',
'MAL'  : '+0800', 'MAT'  : '+0300', 'MDT' : '-0600', 'MEDST': '+0200',
'MEST' : '+0200', 'MESZ' : '+0200', 'MET' : '+0100', 'MEWT' : '+0100',
'MEX'  : '-0600', 'MEZ'  : '+0100', 'MSD' : '+0300', 'MSK'  : '+0200',
'MST'  : '-0700', 'NDT'  : '-0230', 'NFT' : '-0330', 'NOR'  : '+0100',
'NST'  : '-0330', 'NZDT' : '+1300', 'NZST': '+1200', 'NZT'  : '+1200',
'PDT'  : '-0700', 'PST'  : '-0800', 'SADT': '+1030', 'SAST' : '+0930',
'SET'  : '+0100', 'SST'  : '+0200', 'SST' : '+0800', 'SST'  : '-1100',
'SWT'  : '+0100', 'THA'  : '+0700', 'TST' : '+0300', 'UT'   : '+0000',
'UTC'  : '+0000', 'UTZ'  : '-0300', 'VTZ' : '-0200', 'WADT' : '+0900',
'WAST' : '+0800', 'WAT'  : '+0100', 'WDT' : '+0900', 'WEST' : '+0100',
'WET'  : '+0000', 'WETDS': '+0100', 'WST' : '+0800', 'WTZ'  : '-0100',
'WUT'  : '+0100', 'YDT'  : '-0800', 'YST' : '-0900'                  }

def tz_offset(abbrev):
    """
    Lookup a time zone offset from a time zone name (like 'EST'), if possible.
    If time zone name is unknown, return the original abbrev
    """
    if timezones.has_key(abbrev.strip()):
        return timezones[abbrev.strip()]
    else:
        return abbrev

def tz_offset_sec(offset):
    """ Convert time zone offset (e.g. +0100) or abbreviation (e.g. 'EST') into
        an offset in seconds """
    if offset == '':
        return 0
    if not re.match(r'[+-]\d{4}', offset):
        offset = tz_offset(offset)
    if not re.match(r'[+-]\d{4}', offset):
        raise ValueError("Invalid time zone %s" % offset)
    result = int(offset[3:]) * 60
    result += int(offset[1:3]) * 3600
    if offset[0] == '-':
        result = result * (-1)
    return result

def tz_strftime(format, epoch_seconds, offset, append_offset=True):
    """ Return formatted time string in time zone offset """
    if offset == '':
        offset = '+0000'
    if not re.match(r'[+-]\d{4}', offset):
        offset = tz_offset(offset)
    if not re.match(r'[+-]\d{4}', offset):
        raise ValueError("Invalid time zone %s" % offset)
    tz_time_tuple = time.gmtime(epoch_seconds+tz_offset_sec(offset))
    result = time.strftime(format, tz_time_tuple)
    if append_offset:
        result = result + ' ' + offset
    return result
    
def tz_strpmktime(time_str, format, offset):
    """ Parse formatted time string in time zone 'offset', return epoch
        seconds. The time_str itself should not contain any eplicit time zone
        information, but contain a local time in the 'offset' time zone
    """
    if offset == '':
        offset = '+0000'
    if not re.match(r'[+-]\d{4}', offset):
        offset = tz_offset(offset)
    if not re.match(r'[+-]\d{4}', offset):
        raise ValueError("Invalid time zone %s" % offset)
    result = time.mktime(time.strptime(time_str, format))
    result = result - time.timezone - tz_offset_sec(offset)
    return result

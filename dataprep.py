# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#!/usr/bin/env python

import itertools
import datetime
import calendar
import time
import pytz
import json


def load_json(filename):
    """
    Simply load and return a JSON file. This will typically contain a JSON 
    array and will be returned as a list of timestamp strings.
    """
    with open(filename) as infile:
        data = json.load(infile)
    return data


def convert_timezone_eastern(hours):
    """
    Convert a list datetime objects, which already have a tz object specified,
    to Eastern time. (TODO: Generalize this method to take in any tz_str.)
    >>> import datetime, pytz
    >>> utc = pytz.utc
    >>> dtlist = [utc.localize(datetime.datetime(2012,5,5)+datetime.timedelta(days=x)) for x in range(3)]
    >>> convert_timezone_eastern(dtlist)
    [datetime.datetime(2012, 5, 4, 20, 0, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>), datetime.datetime(2012, 5, 5, 20, 0, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>), datetime.datetime(2012, 5, 6, 20, 0, tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>)]
    """
    
    tz_str = 'US/Eastern'
    eastern = pytz.timezone(tz_str)
    return [h.astimezone(eastern) for h in hours]


def bin_timestamp(timestamp_strings, fmt, binsize = 3600, filter_holidays = False, tz='UTC'):
    """
    Returns a list of lists, with each sub-list containing a datetime 
    object corresponding to an hour and a integer count of timestamps 
    within that hour. as a ___ object. Assumes timestamp string is UTC 
    (Greenwich mean time) formatted as '%Y-%m-%dT%H:%M:%S+00:00'. 
    This returned list will not, in general, contain a 'bin' for each
    hour between the min and max timestamp in the dataset (i.e., hour 
    windows that have 0 timestamps will _not_ be contained in the list 
    with a timestamp count == 0).
    >>> strs = u'2012-03-01T00:05:55+00:00', u'2012-03-01T00:06:23+00:00', u'2012-03-01T00:06:52+00:00'
    >>> fmt = '%Y-%m-%dT%H:%M:%S+00:00'
    >>> bin_timestamp(strs, fmt)
    ([[datetime.datetime(2012, 3, 1, 0, 0, tzinfo=<UTC>)], [3]], [])
    """
    
    skipped_timestamps = []
    
    # if timestamp_strings is a string, make it a list so it iterates correctly
    # (find a cleaner method later)
    if timestamp_strings is str:
        timestamp_strings = [timestamp_strings]

    # convert timestamp string -> datetime objects:
    if filter_holidays:
        import sys
        sys.exit('Filtering out holdiays is not implemented yet.')
#         special holidays = []
#         dt = [datetime.datetime.strptime(t, fmt) for t in timestamp_strings\
#               if t in special_days]
    else:
        # TODO, impt: skip any misformatted timestamp strings & print error message
        dt = []
        for i,t in enumerate(timestamp_strings):
            try:
                dt.append(datetime.datetime.strptime(t, fmt))
            except:
                print 'Skipping', t, 'due to incompatible format.'
                skipped_timestamps.append(i)

    # bin each timestamp into the specified time windows:
    utc = pytz.timezone(tz)
    binned_times = [[utc.localize(datetime.datetime(*time.gmtime(d*binsize)[:6])), len(list(g))] \
                    for d,g in itertools.groupby(dt, \
                        lambda di: int(calendar.timegm(di.timetuple()))/binsize)]
    

    # return an list of lists, unzipped from binned_times:
    return [list(t) for t in zip(*binned_times)], skipped_timestamps


def prepare(jsonfile, tz = 'UTC'):
    """
    This takes in a JSON file containing timestamp data and calls functions 
    to convert these to datetime objects and bin them into hour long windows.
    'tz' is the timezone and is UTC (~Greenwich mean time) by default. 
    Returns 2 variables: 'hours' is a list of datetime objects that correspond
    to year, date, and the the start of the hour long window that describes 
    each bin. 'usage' is the amount of logins in that time in the dataset.
    """
    
    # Load a list of user login times (UTC timestamp):
    logins = load_json(jsonfile)
    
    # timestamp string format & time constants:
    fmt = '%Y-%m-%dT%H:%M:%S+00:00'
    seconds_per_hour = 60*60 # number of seconds in an hour
    hours_per_week = 24*7

    # bin the timestamp strings into hour-spanning windows:
    (hours, usage), skipped_timestamps = bin_timestamp(logins, fmt, seconds_per_hour)
    
    # fill in any hours without logins to be zero:
    starthour = hours[0]
    total_hours = (calendar.timegm(max(hours).timetuple()) - calendar.timegm(min(hours).timetuple()))/60/60
    allhours = [starthour + datetime.timedelta(hours = x) for x in range(total_hours)]
    for dt in allhours:
        if dt not in hours:
            hours.append(dt)
            usage.append(0)

    # sort the list by hour & unzip:
#     hours, usage = zip(*sorted(zip(hours, usage), key = lambda hu:hu[0]))

    return hours, usage

# <codecell>



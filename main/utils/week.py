import datetime as dt

def monday_of(d):
    return d - dt.timedelta(days=d.weekday())
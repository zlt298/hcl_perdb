import datetime

def xlSerialToDatetime(s,datemode = 0):
    if datemode not in (0, 1):
        raise XLDateBadDatemode(datemode)
    if s == 0.00:
        return datetime.time(0, 0, 0)
    if s < 0.00:
        raise XLDateNegative(s)
    xldays = int(s)
    frac = s - xldays
    seconds = int(round(frac * 86400.0))
    assert 0 <= seconds <= 86400
    if seconds == 86400:
        seconds = 0
        xldays += 1

    if xldays == 0:
        # second = seconds % 60; minutes = seconds // 60
        minutes, second = divmod(seconds, 60)
        # minute = minutes % 60; hour    = minutes // 60
        hour, minute = divmod(minutes, 60)
        return datetime.time(hour, minute, second)

    if xldays < 61 and datemode == 0:
        raise XLDateAmbiguous(s)

    return (
        datetime.datetime.fromordinal(xldays + 693594 + 1462 * datemode)
        + datetime.timedelta(seconds=seconds)
        )

''' The sql interface for the sp command line interface '''

import json
from datetime import datetime
from datetime import timedelta
import mysql.connector
import pandas as pd

PASSWORD = "root"
USR = "root"


def collect_alarms(host, severity, since, output, sname, alarmtype, time=None):
    ''' Queries the sql database for information about alarms '''
    if since == "current":
        mydb = mysql.connector.connect(
            host="localhost",
            user=USR,
            passwd=PASSWORD,
            database="sp_state"
        )
    else:
        mydb = mysql.connector.connect(
            host="localhost",
            user=USR,
            passwd=PASSWORD,
            database="sp_event"
        )

    mycursor = mydb.cursor()

    sql = build_alarm_query(host, severity, since, sname, alarmtype, time)

    try:
        mycursor.execute(sql)
    except mysql.connector.errors.ProgrammingError:
        return "Invalid value for option"
    except mysql.connector.errors.DatabaseError:
        return "Invalid date"

    myresult = mycursor.fetchall()

    if myresult == []:  # If no results are returned (empty list)
        return "No results found"

    if since == "current":
        df = pd.DataFrame(myresult,
                          columns=['id', 'alarmTypeKey',
                                   'severity', 'note', 'timeRaised'])

    else:
        df = pd.DataFrame(myresult,
                          columns=['id', 'alarmTypeKey', 'severity',
                                   'note', 'timeRaised', 'action'])
    sids = df['id'].to_list()
    hosts = []
    keys = []
    actions = []
    for s in sids:
        if since == "current":
            h = get_host_from_service(s)
            k = get_serkey_from_service(s)
            actions.append("Alarm_Raise")
        else:
            h = get_host_from_sysevent(s)
            k = get_serkey_from_sysevent(s)
        hosts.append(str(h)[3:-4])
        keys.append(str(k)[3:-4])

    df.insert(0, 'host', hosts, True)
    if sname == "all":
        df.insert(1, 'serviceInstanceKey', keys, True)
    df = df.drop(['id'], axis=1)

    if alarmtype != "all":
        df = df.drop(['alarmTypeKey'], axis=1)

    if since == "current":
        df['action'] = actions

    # Format the output
    if output == "table":
        if host != "all":
            df = df.drop(['host'], axis=1)
        if severity != "all":
            df = df.drop(['severity'], axis=1)

        return df.to_string(index=False)
    elif output == "json":
        out = json.dumps(df.to_dict(orient='index'),
                         indent=4, separators=(", ", " = "), default=str)
        return out
    else:
        df = df.drop(['note', 'timeRaised', 'action'], axis=1)
        return df.to_string(header=False, index=False)


def collect_sysevents(host, severity, since, output, sname, event, time=None):
    ''' Queries sql database for information about system events
        which it returns'''
    mydb = mysql.connector.connect(
        host="localhost",
        user=USR,
        passwd=PASSWORD,
        database="sp_event"
    )

    mycursor = mydb.cursor()
    sql = build_sysevent_query(host, severity, since, sname, event, time)

    try:
        mycursor.execute(sql)
    except mysql.connector.errors.ProgrammingError:
        return "Invalid value for option"
    except mysql.connector.errors.DatabaseError:
        return "Invalid date"

    myresult = mycursor.fetchall()

    if myresult == []:
        return "No results found"

    df = pd.DataFrame(myresult, columns=['id', 'type', 'severity', 'note',
                                         'timestamp', 'action'])
    sids = df['id'].to_list()
    hosts = []
    keys = []
    for s in sids:
        h = get_host_from_sysevent(s)
        k = get_serkey_from_sysevent(s)
        hosts.append(str(h)[3:-4])
        keys.append(str(k)[3:-4])

    df.insert(0, 'host', hosts, True)

    df = df.drop(['id'], axis=1)

    # Format the output
    if output == "table":
        if host != "all":
            df = df.drop(['host'], axis=1)
        if severity != "all":
            df = df.drop(['severity'], axis=1)
        if event != "all":
            df = df.drop(['action'], axis=1)
        if sname == "all":
            df.insert(1, 'serviceInstanceKey', keys, True)

        return df.to_string(index=False)
    elif output == "json":
        df.insert(1, 'serviceInstanceKey', keys, True)
        out = json.dumps(df.to_dict(orient='index'),
                         indent=4, separators=(", ", " = "), default=str)
        return out
    else:
        if host != "all":
            df = df.drop(['host'], axis=1)
        if severity != "all":
            df = df.drop(['severity'], axis=1)
        if sname == "all":
            df.insert(1, 'serviceInstanceKey', keys, True)
        df = df.drop(['note', 'timestamp', 'action'], axis=1)
        return df.to_string(header=False, index=False)


def collect_services(host, state, output, service):
    ''' Queries sql database for information about services
        which it then returns '''
    mydb = mysql.connector.connect(
        host="localhost",
        user=USR,
        passwd=PASSWORD,
        database="sp_state"
    )

    mycursor = mydb.cursor()

    sql = build_service_query(host, state, service)

    try:
        mycursor.execute(sql)
    except mysql.connector.errors.ProgrammingError:
        return "Invalid value for option"
    except mysql.connector.errors.DatabaseError:
        return "Invalid date"

    myresult = mycursor.fetchall()

    if myresult == []:
        return "No results found"

    df = pd.DataFrame(myresult,
                      columns=['hostname', 'serviceInstanceKey',
                               'runningState'])
    if host != "all":
        df = df.drop(['hostname'], axis=1)
    if state != "all":
        df = df.drop(['runningState'], axis=1)
    if service != "all":
        df = df.drop(['serviceInstanceKey'], axis=1)

    # Format output
    if output == "table":
        return df.to_string(index=False)
    elif output == "json":
        out = json.dumps(df.to_dict(orient='index'), indent=4,
                         separators=(", ", " = "), default=str)
        return out
    else:
        return df.to_string(header=False, index=False)


def get_sysevent_from_host(host):
    ''' Returns system event id for a specified host '''
    mydb = mysql.connector.connect(
        host="localhost",
        user=USR,
        passwd=PASSWORD,
        database="sp_event"
    )

    mycursor = mydb.cursor()

    sql = "SELECT id FROM systemeventsource WHERE hostname = %s"

    hname = (host, )

    mycursor.execute(sql, hname)

    myresult = mycursor.fetchall()

    return myresult


def get_service_from_host(host):
    ''' Returns service id for specified host '''
    mydb = mysql.connector.connect(
        host="localhost",
        user=USR,
        passwd=PASSWORD,
        database="sp_event"
    )

    mycursor = mydb.cursor()

    sql = "SELECT serviceId FROM systemeventsource WHERE hostname = %s"

    hname = (host, )

    mycursor.execute(sql, hname)

    myresult = mycursor.fetchall()

    return myresult


def get_host_from_sysevent(event):
    ''' Returns host for specified system event id '''
    mydb = mysql.connector.connect(
        host="localhost",
        user=USR,
        passwd=PASSWORD,
        database="sp_event"
    )

    mycursor = mydb.cursor()

    sql = "SELECT hostname FROM systemeventsource WHERE id = %s"

    sevent = (event, )

    mycursor.execute(sql, sevent)

    myresult = mycursor.fetchall()

    return myresult


def get_host_from_service(servid):
    ''' Returns host from specified service id '''
    mydb = mysql.connector.connect(
        host="localhost",
        user=USR,
        passwd=PASSWORD,
        database="sp_event"
    )

    mycursor = mydb.cursor()

    sql = "SELECT hostname FROM systemeventsource WHERE serviceId = %s"

    sname = (servid, )

    mycursor.execute(sql, sname)

    myresult = mycursor.fetchall()

    return myresult


def get_serkey_from_sysevent(event):
    ''' Returns service instance key for specified system event source id '''
    mydb = mysql.connector.connect(
        host="localhost",
        user=USR,
        passwd=PASSWORD,
        database="sp_event"
    )

    mycursor = mydb.cursor()

    sql = "SELECT serviceInstanceKey FROM systemeventsource WHERE id = %s"

    sevent = (event, )

    mycursor.execute(sql, sevent)

    myresult = mycursor.fetchall()

    return myresult


def get_serkey_from_service(servid):
    ''' Returns service instance key for specified service id '''
    mydb = mysql.connector.connect(
        host="localhost",
        user=USR,
        passwd=PASSWORD,
        database="sp_event"
    )

    mycursor = mydb.cursor()

    sql = "SELECT serviceInstanceKey FROM"
    sql += " systemeventsource WHERE serviceId = %s"

    sname = (servid, )

    mycursor.execute(sql, sname)

    myresult = mycursor.fetchall()

    return myresult


def get_sysevent_from_serkey(event):
    ''' Returns system event id for specified service instance key '''
    mydb = mysql.connector.connect(
        host="localhost",
        user=USR,
        passwd=PASSWORD,
        database="sp_event"
    )

    mycursor = mydb.cursor()

    sql = "SELECT id FROM systemeventsource WHERE serviceInstanceKey = %s"

    sevent = (event, )

    mycursor.execute(sql, sevent)

    myresult = mycursor.fetchall()

    return myresult


def get_service_from_serkey(servid):
    ''' Returns service id for specified service in stance key '''
    mydb = mysql.connector.connect(
        host="localhost",
        user=USR,
        passwd=PASSWORD,
        database="sp_event"
    )

    mycursor = mydb.cursor()

    sql = "SELECT serviceId"
    sql += " FROM systemeventsource WHERE serviceInstanceKey = %s"

    sname = (servid, )

    mycursor.execute(sql, sname)

    myresult = mycursor.fetchall()

    return myresult


def build_alarm_query(host, severity, since, sname, alarm, time=None):
    ''' Builds sql query for alarms '''
    if since == "current":
        out = "SELECT serviceId, alarmTypeKey, severity, note, timeRaised FROM"
        out += " activealarm"
    else:
        out = "SELECT systemEventSourceId, type, severity, note, timestamp,"
        out += " systemEventAction FROM systemevent WHERE systemEventAction"
        out += " LIKE \'Alarm_%\'"

        if since == "yesterday":
            ti = datetime.date(datetime.now()) - timedelta(days=1)
            t = str(ti)
        else:
            t = time
        out += " AND timestamp >= \'" + t + "%\'"

    if host != "all":
        if since == "current":
            out += " WHERE ("
            ids = get_service_from_host(host)
            for x in ids:
                spec = "serviceId = \'" + str(x)[1:-2] + "\'" + " OR "
                out += spec
            out = out[:-4] + ")"

        else:
            out += " AND ("
            ids = get_sysevent_from_host(host)
            for x in ids:
                spec = "systemEventSourceId = \'" + str(x)[1:-2] + "\'"
                spec += " OR "
                out += spec
            out = out[:-4] + ")"

    if severity != "all":
        if host == "all" and since == "current":
            out += " WHERE severity = \'" + severity.upper() + "\'"

        else:
            out += " AND severity = \'" + severity.upper() + "\'"

    if alarm != "all":
        if host == "all" and since == "current" and severity == "all":
            out += " WHERE alarmTypeKey LIKE \'" + alarm + "%\'"

        else:
            out += " AND type LIKE \'" + alarm + "%\'"

    if sname != "all":
        if host == "all" and since == "current" and severity == "all" and alarm == "all":
            out += " WHERE ("
            ids = get_service_from_serkey(sname)
            for x in ids:
                spec = "serviceId = \'" + str(x)[1:-2] + "\'" + " OR "
                out += spec
            out = out[:-4] + ")"
        else:
            out += " AND ("
            ids = get_sysevent_from_serkey(sname)
            for x in ids:
                spec = "systemEventSourceId = \'" + str(x)[1:-2] + "\'"
                spec += " OR "
                out += spec
            out = out[:-4] + ")"

    print(out)
    return out


def build_sysevent_query(host, severity, since, sname, event, time=None):
    ''' Builds sql query for system events '''
    out = "SELECT systemEventSourceId, type, severity, note, timestamp,"
    out += " systemEventAction FROM systemevent WHERE "

    if host != "all":
        out += "("
        ids = get_sysevent_from_host(host)
        for x in ids:
            spec = "systemEventSourceId = \'" + str(x)[1:-2] + "\'" + " OR "
            out += spec
        out = out[:-4] + ")"

    if since == "yesterday":
        ti = datetime.date(datetime.now()) - timedelta(days=1)
        t = str(ti)
    elif since == "utc-time":
        t = time
    else:
        t = str(datetime.now())

    if host != "all":
        out += " AND "

    out += "timestamp >= \'" + t

    if since != "current":
        out += "%"

    out += "\'"

    if severity != "all":
        out += " AND severity = \'" + severity.upper() + "\'"

    if sname != "all":
        out += " AND ("
        ids = get_sysevent_from_serkey(sname)
        for x in ids:
            spec = "systemEventSourceId = \'" + str(x)[1:-2] + "\'" + " OR "
            out += spec
        out = out[:-4] + ")"

    if event != "all":
        out += " AND systemEventAction = \'" + event + "\'"

    return out


def build_service_query(host, state, service):
    ''' Returns sql query for services '''
    out = "SELECT hostname, serviceInstanceKey, runningState FROM servicestate"

    if host != "all":
        out += " WHERE hostname = \'" + host + "\'"

    if state != "all":
        if host != "all":
            out += " AND "
        else:
            out += " WHERE "
        out += "runningState = \'" + state + "\'"

    if service != "all":
        if host != "all" or state != "all":
            out += " AND "
        else:
            out += " WHERE "
        out += "serviceInstanceKey = \'" + service + "\'"

    return out

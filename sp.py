''' Command line interface: Service Platform '''

import click
import readsql


@click.group("sp")
def sp():
    '''Get information about alarms, system events or services'''


@sp.command("alarms")
@click.option('--host', type=str, default='all',
              help='The host to display information for')
@click.option('--severity', type=click.Choice(['all', 'warning', 'critical']),
              default='all', help='Which severity to display information for')
@click.option('--since',
              type=str, default='current',
              help='Time to display information from, either "current",'
              + ' "yesterday", or "yyyy-mm-dd_hh:mm:ss"')
@click.option('--output', type=click.Choice(['table', 'simple', 'json']),
              default='table', help='Format the output')
@click.option('--serviceinskey', type=str,
              default='all', help='Filter by serviceInstanceKey')
@click.option('--alarmtype', type=str, default='all', help='Filter by alarmType')
def alarms(host, severity, since, output, serviceinskey, alarmtype):
    '''Display information about alarms'''
    if host == 'all':
        hname = 'all'
    else:
        hname = host

    if serviceinskey == 'all':
        sname = 'all'
    else:
        sname = serviceinskey

    if since not in ('current', 'yesterday'):
        time = since.replace("_", " ")
        since = "utc-time"
    else:
        time = None

    result = readsql.collect_alarms(hname, severity, since,
                                    output, sname, alarmtype, time)
    click.echo(result)


@sp.command("sysevents")
@click.option('--host', type=str,
              default='all', help='The host to display information for')
@click.option('--severity',
              type=click.Choice(['all', 'warning', 'info', 'critical']),
              default='all',
              help='Which severity to display information for')
@click.option('--since',
              type=str, default='current',
              help='Time to display information from, either "current",'
              + ' "yesterday", or "yyyy-mm-dd_hh:mm:ss"')
@click.option('--output', type=click.Choice(['table', 'simple', 'json']),
              default='table', help='Format the output')
@click.option('--serviceinskey', type=str,
              default='all', help='Filter by serviceInstanceKey')
@click.option('--event', type=str, default='all',
              help='Filter by eventAction')
def sysevents(host, severity, since, output, serviceinskey, event):
    '''Display information about system events'''
    if host == 'all':
        hname = 'all'
    else:
        hname = host

    if since not in ('current', 'yesterday'):
        time = since.replace("_", " ")
        since = "utc-time"
    else:
        time = None

    if serviceinskey == 'all':
        sname = 'all'
    else:
        sname = serviceinskey

    if event == 'all':
        ename = 'all'
    else:
        ename = event

    result = readsql.collect_sysevents(hname, severity, since,
                                       output, sname, ename, time)

    click.echo(result)


@sp.command("services")
@click.option('--host', type=str,
              default='all', help='The host to display information for')
@click.option('--state', type=click.Choice(['all', 'running', 'stopped']),
              default='all',
              help='Which services state to display information for')
@click.option('--output', type=click.Choice(['table', 'simple', 'json']),
              default='table', help='Format the output')
@click.option('--serviceinskey', type=str,
              default='all', help='Filter by serviceInstanceKey')
def services(host, state, output, serviceinskey):
    '''Display information about services'''
    if host == 'all':
        hname = 'all'
    else:
        hname = host

    if serviceinskey == 'all':
        sname = 'all'
    else:
        sname = serviceinskey

    result = readsql.collect_services(hname, state, output, sname)
    click.echo(result)

#!/usr/bin/python3

"""
Copyright 2023, Georg Pfuetzenreuter for SUSE LLC

Licensed under the EUPL, Version 1.2 or - as soon they will be approved by the European Commission - subsequent versions of the EUPL (the "Licence").
You may not use this work except in compliance with the Licence.
An English copy of the Licence is shipped in a file called LICENSE along with this applications source code.
You may obtain copies of the Licence in any of the official languages at https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12.
"""

from flask import Flask, request
from waitress import serve
import datetime
import logging
import os
import sys
import yaml

host = os.getenv('ZC_HOST', '::1')
port = os.getenv('ZC_PORT', 8090)
issuesdir = os.getenv('ZC_ISSUES')
loglevel = os.getenv('ZC_LOGLEVEL', 'INFO').upper()

log = logging.getLogger('zabbix-cstate')
logging.basicConfig(level=loglevel)

# map Zabbix to cstate severity levels
severitymap = {'Information': 'notice', 'Warning': 'disrupted', 'Average': 'disrupted', 'High': 'disrupted', 'Disaster': 'down'}

if issuesdir is None:
    log.error('Cannot operate - please set ZC_ISSUES to a location to store generated issue files in.')
    sys.exit(1)

app = Flask(__name__)

def issuefile(eventid):
    issuefilepath = os.path.join(issuesdir, eventid + '.md')
    log.debug('Constructed path to issue file: %s', issuefilepath)
    return issuefilepath

def check_issue(file):
    issuefileexists = os.path.isfile(file)
    log.debug('File %s exists: %s', file, issuefileexists)
    return issuefileexists

def generate_issue(title, date, time, severity, affected, status, eventid, file, resolvedWhen=None):
    log.info('Generating issue for event %i', int(eventid))

    date = date.replace('.','-')

    if status == 'PROBLEM':
        resolved = False
    if status == 'RESOLVED':
        resolved = True

    data = {
            'title': title,
            'date': date + ' ' + time,
            'resolved': resolved,
            'resolvedWhen': resolvedWhen,
            'severity': severity,
            'affected': affected,
            'section': 'issue'
            }

    log.debug('Constructed issue data: %s', data)

    with open(file, 'w') as filehandle:
        filehandle.write('---\n')
        yaml.dump(data, filehandle, sort_keys=False)
        filehandle.write('---\n')

def close_issue(file):
    log.info('Closing issue at %s', file)

    body = None

    with open(file, 'r') as filehandle:
        for structure in list(yaml.safe_load_all(filehandle)):
            if structure is None:
                continue
            if isinstance(structure, str):
                body = structure
            if 'title' in structure:
                data = structure

    data['resolved'] = True
    data['resolvedWhen'] = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')

    log.debug('Constructed issue data: %s', data)

    with open(file, 'w') as filehandle:
        filehandle.write('---\n')
        filehandle.write(yaml.dump(data, default_flow_style=False, sort_keys=False))
        filehandle.write('---\n')
        if body is not None:
            filehandle.write(body)

@app.route('/call', methods=['POST'])
def responder():
    if request.method == 'POST':
        data = request.json
        log.debug('Received payload: %s', data)

        eventid = data['id']
        status = data['status']
        system = data['system']
        severity = data['severity']

        file = issuefile(eventid)
        issue_exists = check_issue(file)

        if status == 'RESOLVED' and issue_exists:
            log.debug('"Resolved" incident detected')
            close_issue(file)

        elif status == 'PROBLEM' and not issue_exists:
            log.debug('"Problem" incident detected')
            affected = [system]

            # check if multiple systems are affected (Zabbix 'cs_subsystems' tag)
            if 'subsystems' in data['servicetags']:
                log.debug('Found subsystems')
                subsystems = data['subsystems']
                affected = affected.extend(subsystems)

            # rewrite Zabbix to cstate severity
            severity = severitymap[severity]
            log.debug('Severity set to ' + severity)

            # create new incident
            generate_issue(data['name'], data['date'], data['time'], severity, affected, data['status'], eventid, file)

        else:
            log.error('Cannot deal with event: ')
            log.error(eventid)

        return 'OK'

if __name__ == '__main__':
    log.debug('Initializing server ...')
    #app.run(host=host, port=port)
    serve(app, host=host, port=port)

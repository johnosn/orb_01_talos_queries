"""Generate an authentication token for the Cisco Orbital API."""
from datetime import datetime, timedelta
import json
import requests
from requests.auth import HTTPBasicAuth


def gen_orb_auth(orb_url, orb_client, orb_secret):
    """Generate a new Orbital authentication token."""
    # REQUEST AUTH TOKEN
    url = orb_url + 'oauth2/token'
    payload = 'grant_type=client_credentials'
    headers = {'Content-Type': "application/x-www-form-urlencoded",
               'Accept': "application/json"}
    response = requests.post(url, data=payload,
                             headers=headers,
                             auth=HTTPBasicAuth(orb_client, orb_secret))

    # CHECK SERVER RESPONSE
    check_orb_response(response)

    # PARSE AUTH TOKEN
    r_json = response.json()
    token = 'Bearer ' + r_json['token']
    expiry = datetime.strptime(r_json['expiry'][0:26], '%Y-%m-%dT%H:%M:%S.%f')
    return token, expiry


def check_orb_expiry(token_expires):
    """Check if token is expired."""
    delta = abs((token_expires - datetime.utcnow()).seconds)
    return bool(delta < 60)


def check_orb_table(value):
    """Validate Orbital query table use."""
    bad_tables = ['carves', 'curl', 'curl_certificate', 'ntfs_journal_events',
                  'powershell_events', 'windows_events', 'windows_eventlog']
    return bool([ele for ele in bad_tables if ele in value['query']])


def create_orb_payload(query_data, nodes, webhookid):
    """Create query json for sending to Orbital."""
    # CALCULATE QUERY EXPIRATION TIME
    value = query_data[2]
    now = datetime.utcnow()
    expiry = now + timedelta(seconds=value['interval'])
    expiry = int(expiry.timestamp())

    # CREATE THE OSQUERY DATA
    osquery = [{"sql": value['query'],
                "name": query_data[1],
                "label": query_data[0]}]

    # CREATE THE CONTEXT INFORMATION - DESCRIPTION
    context = {'description': value['description']}

    # PROVIDE CONTEXT INFORMATION - MITRE TACTICS
    try:
        if value['mitre_tactics']:
            context.update({"mitre_tactics": str(value['mitre_tactics'])})
    except KeyError:
        pass

    # PROVIDE CONTEXT INFORMATION - MITRE TECHNIQUES
    try:
        if value['mitre_techniques']:
            context.update({"mitre_techniques":
                            str(value['mitre_techniques'])})
    except KeyError:
        pass

    # PROVIDE CONTEXT INFORMATION - REFERENCES
    try:
        if value['references']:
            context.update({"references": str(value['references'])})
    except KeyError:
        pass

    payload = {'expiry': expiry,
               'interval': value['interval'],
               'name': query_data[1],
               'osQuery': osquery,
               'context': context,
               'snapshot': value['snapshot']}

    if nodes:
        payload["nodes"] = nodes
    else:
        payload["os"] = value['platform']

    if webhookid:
        payload["postbacks"] = [{"webhookid": webhookid}]

    payload = json.dumps(payload, ensure_ascii=True)
    return payload


def check_orb_response(response):
    """Check Orbital API response."""
    try:
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        r_json = response.json()
        print("\nFAILED:")
        print('Response Error: ', err)
        print(r_json + "\n")
        return False


def submit_orb_query(query_data, orb_data):
    """Submit query to Orbital API."""
    # CHECK ORBITAL TABLE
    if check_orb_table(query_data[2]):
        print("FAILED: " + query_data[1] +
              " contains a table not used by Orbital")
        return

    # CREATE ORBITAL REQUEST INFORMATION
    url = "{0}query".format(orb_data[0])
    payload = create_orb_payload(query_data, orb_data[2], orb_data[3])
    headers = {'Authorization': orb_data[1],
               'Content-Type': 'application/json',
               'Accept': 'application/json'}

    # print("Payload sop: " + str(payload))
    # SUBMIT QUERY
    response = requests.post(url, headers=headers, data=payload)

    # CHECK SERVER RESPONSE
    is_ok = check_orb_response(response)
    if is_ok:
        r_json = response.json()
        print("SUCCESS: submitted job id: " + r_json['ID'] +
              " for query: " + query_data[1])

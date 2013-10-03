import requests
import re
import time

ip_regex = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # 123.123.123.123
full_regex = '<td>{ip}</td><td>(.*?)</td>'.format(ip=ip_regex)

address = 'http://192.168.0.1/wlanAccess.asp'
auth = ('', 'admin')

known_hosts = {'192.168.0.12': 'paulo-mac'}

computers_online = set()

def get_new_computers():
    """
    Updates the 'computers_online' set and returns the difference.

    The return value is a tuple (computers_entered, computers_exited).
    Both values are a list of (ip, hostname) tuples.
    """
    global computers_online

    response = requests.get(address, auth=auth)
    names = set(re.findall(full_regex, response.text))
    for ip, name in names:
        if ip in known_hosts and not name:
            names.remove((ip, name))
            names.add((ip, known_hosts[ip]))

    entered = names - computers_online
    exited = computers_online - names

    computers_online = names

    return (entered, exited)

def show_computers_online():
    """
    Opens a notification balloon displaying the computers currently online.
    """
    computers = ['{name} ({ip})'.format(name=name, ip=ip)
                 for ip, name in computers_online]
    notify('Doorman', 'Computers online now:\n\n' + '\n'.join(computers))


if __name__ == '__main__':
    from background import tray, notify
    from simpleserver import serve
    tray('Doorman', 'computer-plus.ico', on_click=show_computers_online)
    serve(computers_online, port=2345)
    while True:
        try:
            entered, exited = get_new_computers()
        except:
            # In case the network is down, sleep a little longer.
            time.sleep(120)
            continue

        if not entered and not exited:
            time.sleep(60)
            continue

        messages = []

        if entered:
            entered_text = ['{name} ({ip})'.format(name=name, ip=ip)
                            for ip, name in entered]
            messages.append('Entered:\n' + '\n'.join(entered_text))

        if exited:
            exited_text = ['{name} ({ip})'.format(name=name, ip=ip)
                            for ip, name in exited]
            messages.append('Exited:\n' + '\n'.join(exited_text))

        notify('Doorman', '\n\n'.join(messages))

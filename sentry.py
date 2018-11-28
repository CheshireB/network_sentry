import subprocess
import re
import telegram
import time

from settings import TOKEN, SLEEP_TIME, TELEGRAM_CHAT_IDS, NAMED_HOSTS


class Network(object):

    def __init__(self):
        self.hosts_up = set()

        self.update_hosts()

    def run_nmap(self):
        command = "nmap -sP 192.168.1.1/24"

        return subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True
        )

    def update_hosts(self):
        pattern = r'\d+(?:\.\d+){3}'
        hosts_up = set()

        nmap_output = [str(line) for line in self.run_nmap().splitlines() if b'Nmap scan report' in line]
        for report in nmap_output:
            ip = re.search(pattern, report).group()
            hosts_up.add(ip)

        self.hosts_up = hosts_up

        print('Hosts updated %s' % self.hosts_up)


class Sentry(object):

    def __init__(self):
        self.active_hosts = set()
        self.telegram_bot = telegram.Bot(TOKEN)

    def send_to_telegram(self, message):
        for telegram_id in TELEGRAM_CHAT_IDS:
            self.telegram_bot.send_message(
                chat_id=telegram_id,
                text=message
            )

    def send_to_vk(self, message):
            pass

    def send_message(self, message):
        self.send_to_telegram(message)

    def activate_sentry(self):
        net = Network()

        while True:

            print('Sentry: Down hosts: %s' % self.active_hosts.difference(net.hosts_up))
            for host in self.active_hosts.difference(net.hosts_up):
                name = NAMED_HOSTS[host] if host in NAMED_HOSTS else 'Unknown'
                message = '%s disconnected' % name
                self.send_to_telegram(message)

            print('Sentry: Hosts not in active_hosts: %s' % net.hosts_up.difference(self.active_hosts))
            for host in net.hosts_up.difference(self.active_hosts):
                name = NAMED_HOSTS[host] if host in NAMED_HOSTS else 'Unknown'
                message = '%s connected' % name
                self.send_to_telegram(message)

            self.active_hosts = net.hosts_up
            print('\t')

            time.sleep(SLEEP_TIME)

            net.update_hosts()


sentry = Sentry()
sentry.activate_sentry()

from zabbix.api import ZabbixAPI
from lib.config import Config
from lib import crypt
import argparse
import argcomplete


class ConfigVmCloner(Config):
    def __init__(self, cfg_file=None):
        super().__init__(cfg_file)
        self.zabbix = self.config['zabbix']
        self.zabbix['password'] = crypt.decode(self.zabbix['password'])


def delete_host(name):
    """
    delete an host on the zabbix server
    :param name: name of the host to delete
    :return: nothing
    """
    cfg = ConfigVmCloner()

    zapi = ZabbixAPI(url=cfg.zabbix['url'],
                     use_authenticate=False,
                     user=cfg.zabbix['username'],
                     password=cfg.zabbix['password'])
    try:
        hosts = zapi.host.get(filter={"host": name})
    except():
        print("/!\\Failed to get the host/!\\")
        exit(1)

    hostnames = [host['host'] for host in hosts]

    # if there is no problem we delete it
    if len(hostnames) == 1:
        id_host = [hosts[0]['hostid']]
        zapi.do_request(method='host.delete', params=id_host)
    else:
        print("/!\\ Problem on the number of host found on the Zabbix server /!\\")
        print("------- Here is the list --------")
        for element in hostnames:
            print(element)
        print("------- End of the list ---------")


def collect_args():
    """
    collect arguments from the command line and clean them
    :return: an object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help="nom de la vm", type=str)
    parser.add_argument('--force', help="power off/on", action='store_true')
    parser.add_argument("--config", type=str, help="fichier de configuration")

    argcomplete.autocomplete(parser)
    return parser.parse_args()


if __name__ == '__main__':
    args = collect_args()
    delete_host(name = args.name)

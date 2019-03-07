from .crypt import decode
from requests import Session
from zeep import Client, Transport


class DNSMgr:

    def __init__(self, **cfg):
        self.auth = (cfg['username'], decode(cfg['password']))
        self.verify = cfg['ca_file']
        self.wsdl = cfg['url']

    def connect(self):
        session = Session()
        session.auth = self.auth
        session.verify = self.verify
        transport = Transport(session=session)
        return Client(self.wsdl, transport=transport)

    def add_record(self, name, ip):
        """
        add DNS record type A
        :param name: fqdn
        :param ip: ip address
        :return: boolean
        """
        z = self.connect()
        z.service.AddDnsServerResourceRecordA(name, ip)

    def remove_record(self, name, ip, domain):
        """
        remove type A
        :param name: name of the server ex xbricetest2
        :param ip: ip address
        :return: boolean
        """
        z = self.connect()
        z.service.RemoveDnsServerResourceRecordA(name, ip, domain)

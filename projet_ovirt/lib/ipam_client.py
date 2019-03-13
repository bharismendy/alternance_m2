# -*- coding: utf-8 -*-

import json
import re
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning


class IpamClient:
    def __init__(self, username, password, owner, url, verify):
        """Création d'une session vers un serveur PHPIpam.

           username : identifiant de connexion
           password : mot de passe
           owner : e-mail du propriétaire de l'IP (lors d'un reserve_address)
           url : URL de l'appli REST utilisée ie: https://foo.fr/api/app/
           verify : si True, vérifie le certificat https
        """

        m = re.match(r'^https?://([^/]+)/.+(.)$', url)
        if m is None:
            raise Exception('Malformed HTTP URL: '+url)
        if m.group(2) != '/':
            self.url = url + '/'
        else:
            self.url = url
        self.username = username
        self.password = password
        self.verify = verify
        self.owner = owner
        if not self.verify:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.headers = {
            'Content-Type': 'application/json',
            'Connection': 'close',
            'Host': m.group(1)
        }

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, typ, v, tb):
        self.close()

    def connect(self):
        r = requests.post(
            self.url+'user/',
            auth=requests.auth.HTTPBasicAuth(
                username=self.username,
                password=self.password
            ),
            verify=self.verify,
            headers=self.headers
        )
        if r.ok:
            self.headers['token'] = r.json()['data']['token']
        else:
            raise Exception('login failed: '+r.text)

    def close(self):
        self.delete('user/')
        del self.headers['token']

    def check_token(self):
        """Vérifie si la session est toujours active
        """
        try:
            self.get('user/')
            return True
        except:
            return False

    def request_address(self, subnet_cidr):
        """Retourne la prochaine IP disponible dans le sous réseau

           subnet_cidr: masque de sous-réseau IPAM (!)
        """
        subnet_id = self.get_subnet_id(subnet_cidr)
        r = self.get('/subnets/{}/first_free/'.format(subnet_id))
        return r['data']

    def reserve_address(self, hostname, subnet_cidr):
        """Réserve la prochaine IP disponible dans le sous réseau

           hostname:    FQDN à enregistrer
           subnet_cidr: masque de sous-réseau IPAM (!)
        """
        ip = self.request_address(subnet_cidr)
        self.reserve_this_address(hostname, subnet_cidr, ip)
        return ip

    def reserve_this_address(self, hostname, subnet_cidr, ip):
        """Réserve l'IP dans le sous réseau

           hostname:    FQDN à enregistrer
           subnet_cidr: masque de sous-réseau IPAM (!)
           ip:          IP à enregistrer
        """
        subnet_id = self.get_subnet_id(subnet_cidr)
        self.post(
            '/addresses/',
            payload={
                "owner": self.owner,
                "hostname": hostname,
                "subnetId": subnet_id,
                "ip": ip
            }
        )

    def release_address(self, ip):
        """Libère l'IP
        """
        r = self.get('/addresses/search/{}/'.format(ip))
        if len(r['data']) > 1:
            raise Exception(ip+' référencée plusieurs fois')
        ip_id = r['data'][0]['id']
        return self.delete('/addresses/{}/'.format(ip_id))

    def get_subnet_id(self, subnet_cidr):
        r = self.get('/subnets/cidr/{}/'.format(subnet_cidr))
        if len(r['data']) > 1:
            raise Exception(subnet_cidr+' référencée plusieurs')
        subnet_id = r['data'][0]['id']
        return subnet_id

    def get(self, query):
        r = requests.get(
            self.url+query,
            verify=self.verify,
            headers=self.headers
        )
        if r.ok:
            return r.json()
        else:
            self.fail('GET', query, {}, r)

    def post(self, query, payload):
        r = requests.post(
            self.url+query,
            verify=self.verify,
            headers=self.headers,
            data=json.dumps(payload)
        )
        if r.ok:
            return r.json()
        else:
            self.fail('POST', query, payload, r)

    def delete(self, query):
        r = requests.delete(
            self.url+query,
            verify=self.verify,
            headers=self.headers
        )
        if r.ok:
            return r.json()
        else:
            self.fail('DELETE', query, {}, r)

    def fail(self, method, query, payload, response):
        raise Exception(method+' '+query+' failed')

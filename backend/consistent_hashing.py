from hashlib import sha256

class ConsistentHashing:
    def __init__(self, servers=[], replications=100):
        self.replications = replications
        self.peers_per_node = {}
        self.nodes = {}
        self.ring = {}
        self.keys = {}

        self._create_ring(servers)

    def _create_ring(self, servers):
        for server in servers:
            self.nodes[server['id']] = server['port']

            for i in range(self.replications):
                hash_ = self._hash(f'{server["id"]}-{i}')
                self.ring[hash_] = server['id']

                if server['id'] not in self.peers_per_node:
                    self.peers_per_node[server['id']] = 0
                else:
                    self.peers_per_node[server['id']] += 1

        self.keys = sorted(self.ring.keys())

    def _hash(self, data):
        hash_ = sha256()
        hash_.update(bytes(data, encoding='utf8'))
        hash_ = hash_.hexdigest()
        return int(hash_, 16)

    def add_node(self):
        pass

    def remove_node(self, server, name):
        try:
            self.nodes[server['id']] = server['port']
        except Exception:
            raise KeyError('Node: \'{}\' doesnt exist, choose other node: {}'.format(
                name, self.nodes.keys()))
        else:
            self.replications.pop(name)
            for w in range(self.replications):
                del self.ring[self._hash('%s-%s' % (name, w))]
            self.keys = sorted(self.ring.keys())

    def search_node(self, name):
        try:
            name == self.replications.pop(name)
        except Exception:
            raise KeyError('Node: \'{}\' doesnt exist'.format(name))
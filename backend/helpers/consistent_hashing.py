from threading import Lock
from hashlib import sha1
from time import sleep
import grpc

from proto import API_pb2
from proto import API_pb2_grpc

lock = Lock()

class ConsistentHashing:
    def __init__(self, n_servers, port, node_specs, m=160):
        self.n_servers = n_servers
        self.default_port = port
        self.active_nodes = 1
        self.ready = False
        self.m = m
        self.MAX_ID = 2 ** m

        self.stubs = {}
        self.finger_table = {}
        self.keys = {}

        self.id = self._hash(str(node_specs['id']))
        self.server_id = node_specs['id']
        print(f'{node_specs["id"]} - {self.id}')

        self.predecessor = None

    def _flood(self):
        node = API_pb2.Node()
        node.id = str(self.id)
        node.server_id = self.server_id

        for i in range(self.n_servers):
            hash_ = self._hash(str(i))

            if hash_ == self.id:
                continue

            while True:
                try:
                    with grpc.insecure_channel(f'nerd_room_backend{i}:{self.default_port}') as channel:
                        stub = API_pb2_grpc.APIStub(channel)
                        stub.FloodNode(node)
                except Exception as e:
                    print('Node not ready. Will retry in 3 seconds')
                    sleep(3)
                    continue
                break

    def _find_successor(self, key):
        target_node = API_pb2.Node()

        found = False

        if self.id < self.predecessor['id']:
            if self.predecessor['id'] < key <= self.MAX_ID or 0 <= key <= self.id:
                target_node.id = str(self.id)
                target_node.server_id = self.server_id
                found = True
        elif self.predecessor['id'] < key <= self.id:
            target_node.id = str(self.id)
            target_node.server_id = self.server_id
            found = True

        if not found:
            for i in range(self.m-1):
                if self.finger_table[i]['id'] < self.finger_table[i+1]['id']:
                    if self.finger_table[i]['id'] <= key < self.finger_table[i+1]['id']:
                        target_node.id = str(self.finger_table[i]['id'])
                        target_node.server_id = self.finger_table[i]['server_id']
                        found = True
                        break
                elif self.finger_table[i]['id'] <= key <= self.MAX_ID or 0 <= key <= self.finger_table[i+1]['id']:
                    target_node.id = str(self.finger_table[i]['id'])
                    target_node.server_id = self.finger_table[i]['server_id']
                    found = True
                    break

        if not found and key > self.finger_table[self.m-1]['id']:
                try:
                    with grpc.insecure_channel(f'nerd_room_backend{self.finger_table[self.m-1]["server_id"]}:{self.default_port}') as channel:
                        stub = API_pb2_grpc.APIStub(channel)
                        target_node = stub.FindSuccessor(API_pb2.RequestFindSuccessor(key=str(key)))
                except Exception as e:
                    print(e)
                    print('Node not working')
                    self._remove_node()


        return target_node

    def _build_finger_table(self):
        for i in range(self.m):
            self.finger_table[i] = {
                'id': (self.id + (2 ** i)) % (2 ** self.m),
                'server_id': self.server_id,
                'succ': self.id
            }

    def _hash(self, data):
        hash_ = sha1()
        hash_.update(bytes(data, encoding='utf8'))
        hash_ = hash_.hexdigest()
        return int(hash_, 16)

    def _remove_node(self):
        pass

    def hash(self, key):
        return self._hash(str(key))

    def initialize(self):
        self._build_finger_table()
        self._flood()

        while self.active_nodes != self.n_servers:
            pass

        self.ready = True

        # print(f'id: {self.server_id} - predecessor: {self.predecessor["server_id"]}')
        # for i in range(self.m):
        #     print(f"{i} - {self.finger_table[i]['id']} - {self.finger_table[i]['succ']}")
        # print()

    def flood(self, request):
        empty = API_pb2.Empty()

        lock.acquire()

        new_node = request
        new_node_id = int(new_node.id)

        # Select the predecessor
        change = False
        if not self.predecessor:
            change = True
        else:
            if self.predecessor['id'] > self.id:
                if new_node_id > self.predecessor['id']:
                    change = True
                elif new_node_id < self.id:
                    change = True
            else:
                if new_node_id < self.predecessor['id']:
                    change = True
                elif new_node_id < self.id:
                    change = True

        if change:
            self.predecessor = {'id': new_node_id, 'server_id': new_node.server_id}

        for i in range(self.m):
            if new_node_id >= self.finger_table[i]['id']:
                if self.finger_table[i]['id'] > self.finger_table[i]['succ'] or self.finger_table[i]['succ'] > new_node_id:
                    self.finger_table[i]['succ'] = new_node_id
                    self.finger_table[i]['server_id'] = new_node.server_id
            elif new_node_id < self.finger_table[i]['succ'] and self.finger_table[i]['id'] >= new_node_id:
                    self.finger_table[i]['succ'] = new_node_id
                    self.finger_table[i]['server_id'] = new_node.server_id

        self.active_nodes += 1

        lock.release()

        return empty

    def find_successor(self, key):
        return self._find_successor(int(key))

    def get_reachable_nodes(self):
        nodes = []
        for i in range(self.m):
            node = {'id': self.finger_table[i]['succ'], 'server_id': self.finger_table[i]['server_id']}
            if node not in nodes:
                nodes.append(node)
        return nodes

    def join_node(self):
        pass

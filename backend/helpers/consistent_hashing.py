from threading import Lock, Timer
from hashlib import sha1
import grpc

from proto import API_pb2
from proto import API_pb2_grpc

lock = Lock()

class Node:
    def __init__(self, id=None, host=None, port=None, server_id=None, predecessor=None, pb=None):
        if not pb:
            self.id = id
            self.host = host
            self.port = port
            self.server_id = server_id
            self.predecessor = predecessor
        else:
            self.id = int(pb.id)
            self.host = pb.host
            self.port = pb.port
            self.server_id = pb.server_id
            self.predecessor = Node(pb=pb.predecessor) if pb.HasField('predecessor') else predecessor

    def __eq__(self, other):
        return self.id == other.id

    def to_pb(self):
        node = API_pb2.Node()
        node.id = str(self.id)
        node.server_id = self.server_id
        node.host = self.host
        node.port = self.port

        if self.predecessor:
            node.predecessor.CopyFrom(self.predecessor.to_pb())

        return node


class ConsistentHashing:
    STABILIZE_TIME = 10
    FIX_FINGERS_TIME = 7

    def __init__(self, specs, m=160):
        id = self._hash(f'{specs["host"]}-{specs["port"]}')
        print(f'{specs["server_id"]} - {id}')

        self.node = Node(id, specs['host'], specs['port'], specs['server_id'])
        self.connect_host = specs['connect_host']
        self.connect_port = specs['connect_port']
        self.first = self.connect_host == self.node.host and self.connect_port == self.node.port

        self.m = m
        self.MAX_ID = 2 ** m
        self.next_key = 0

        self.finger_table = {}
        self.keys = {}

        self._build_finger_table()

        if not self.first:
            self._join()
        else:
            self._initialize_stabilize()
            self._initialize_fix_fingers()

    def _hash(self, data):
        hash_ = sha1()
        hash_.update(bytes(data, encoding='utf8'))
        hash_ = hash_.hexdigest()
        return int(hash_, 16)

    def _in_interval(self, key, node_left, node_right, inclusive_left=False, inclusive_right=False):
        if node_left != node_right:
            if inclusive_left:
                node_left = (node_left - 1) % (2 ** self.m)
            if inclusive_right:
                node_right = (node_right + 1) % (2 ** self.m)

        if node_left < node_right:
            return node_left < key < node_right
        else:
            return (key > max(node_left, node_right)) or \
                   (key < min(node_left, node_right))

    def _build_finger_table(self):
        for i in range(self.m):
            self.finger_table[i] = {
                'id': (self.node.id + (2 ** i)) % (2 ** self.m),
                'succ': self.node
            }

    def _closest_preceding_node(self, key):
        for i in range(self.m-1, -1, -1):
            if self._in_interval(self.finger_table[i]['succ'].id, self.node.id, key):
                return self.finger_table[i]['succ']
        return self.node

    def _find_successor(self, key):
        if self.node.predecessor is not None and self._in_interval(key, self.node.predecessor.id, self.node.id, inclusive_right=True):
            return self.node
        elif self._in_interval(key, self.node.id, self.finger_table[0]['succ'].id, inclusive_right=True):
            return self.finger_table[0]['succ']
        else:
            preceding_node = self._closest_preceding_node(key)
            try:
                with grpc.insecure_channel(f'{preceding_node.host}:{preceding_node.port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    pb_request_find_successor = API_pb2.RequestFindSuccessor(key=str(preceding_node.id))
                    pb_node = stub.FindSuccessor(pb_request_find_successor)
                    node = Node(pb=pb_node)
                    return node
            except Exception as e:
                print('Node not working')
                print(e)
                return None

    def _initialize_finger_table(self):
        for i in range(self.m):
            id = (self.node.id + (2 ** i)) % (2 ** self.m)
            try:
                with grpc.insecure_channel(f'{self.connect_host}:{self.connect_port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    pb_request_find_successor = API_pb2.RequestFindSuccessor(key=str(id))
                    pb_node = stub.FindSuccessor(pb_request_find_successor)
                    node = Node(pb=pb_node)
                    self.finger_table[i] = {
                        'id': id,
                        'succ': node
                    }
            except Exception as e:
                print(e)

    def _join(self):
        print(f'Joining: {self.connect_host} {self.connect_port}')
        while True:
            try:
                with grpc.insecure_channel(f'{self.connect_host}:{self.connect_port}') as channel:
                    stub = API_pb2_grpc.APIStub(channel)
                    pb_request_find_successor = API_pb2.RequestFindSuccessor(key=str(self.node.id))
                    pb_node_succ = stub.FindSuccessor(pb_request_find_successor)
                    node_succ = Node(pb=pb_node_succ)
                    self.finger_table[0]['succ'] = node_succ
                    break
            except Exception as e:
                pass

        self._initialize_stabilize()
        self._initialize_fix_fingers()

        # for i in range(self.m):
        #     print(f"{i} - {self.finger_table[i]['id']} - {self.finger_table[i]['succ'].server_id}")
        # print()

    def _notify(self, notify_node):
        with grpc.insecure_channel(f'{notify_node.host}:{notify_node.port}') as channel:
            stub = API_pb2_grpc.APIStub(channel)
            stub.Notify(self.node.to_pb())

    def _initialize_stabilize(self):
        t = Timer(ConsistentHashing.STABILIZE_TIME, self._stabilize)
        t.start()

    def _stabilize(self):
        skip = False

        successor = self.finger_table[0]['succ']

        if not skip:
            with grpc.insecure_channel(f'{successor.host}:{successor.port}') as channel:
                stub = API_pb2_grpc.APIStub(channel)
                pb_node = stub.GetPredecessor(API_pb2.Empty())
                x = Node(pb=pb_node)

                # print(f"In stabilize receive predecessor {x.server_id} from successor {successor.server_id}")

                if x.id == -1:
                    skip = True

                if not skip:
                    if x is not None and self._in_interval(x.id, self.node.id, successor.id):
                        self.finger_table[0]['succ'] = x

        self._notify(self.finger_table[0]['succ'])

        t = Timer(ConsistentHashing.STABILIZE_TIME, self._stabilize)
        t.start()

    def _initialize_fix_fingers(self):
        t = Timer(ConsistentHashing.FIX_FINGERS_TIME, self._fix_fingers)
        t.start()

    def _fix_fingers(self):
        id = self.node.id + (2 ** self.next_key) % (2 ** self.m)
        self.finger_table[self.next_key]['succ'] = self._find_successor(id)

        self.next_key += 1
        self.next_key %= self.m

        t = Timer(ConsistentHashing.FIX_FINGERS_TIME, self._fix_fingers)
        t.start()

    def hash(self, key):
        return self._hash(str(key))

    def find_successor(self, key):
        return self._find_successor(int(key))

    def notify(self, pb_node):
        lock.acquire()

        maybe_predecessor = Node(pb=pb_node)

        # print(f"Receive notification in {self.node.server_id} from {maybe_predecessor.server_id}")
        if self.node.predecessor is None or \
            self._in_interval(maybe_predecessor.id, self.node.predecessor.id, self.node.id):

            # if self.node.predecessor:
            #     print(f"Antes Predecessor do server {self.node.predecessor.server_id}")
            # else:
            #     print(f"Antes Predecessor do server {self.node.predecessor}")
            self.node.predecessor = maybe_predecessor
            # print(f"Depois Predecessor do server {self.node.predecessor.server_id}")

        lock.release()

    def get_predecessor(self):
        if not self.node.predecessor:
            return Node(-1, '', -1, -1)

        return self.node.predecessor

    def get_reachable_nodes(self):
        nodes = []
        for i in range(self.m):
            node = self.finger_table[i]['succ']
            if node not in nodes:
                nodes.append(node)
        return nodes

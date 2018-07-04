from socket import error, socket, AF_INET, SOCK_DGRAM
from Queue import Queue, Empty
from simpleubjson import encode, decode
from .network import AbsNetwork, ConnectionError, NetworkThread


class ClientThread(NetworkThread):

    def __init__(self, srv_addr, eng, port):
        self.srv_addr = srv_addr
        NetworkThread.__init__(self, eng, port)
        self.msgs = Queue()
        self.rpc_ret = Queue()

    def _configure_socket(self):
        self.tcp_sock.connect((self.srv_addr, self.port))

    def _process_read(self, sock):
        try:
            data = self.recv_one_message(sock)
            if data:
                dct = dict(decode(data))
                if 'is_rpc' in dct: self.rpc_ret.put(dct['result'])
                else:
                    args = [dct['payload'], sock]
                    self.eng.cb_mux.add_cb(self.read_cb, args)
        except ConnectionError as exc:
            print exc
            self.connections.remove(sock)

    def _process_write(self, sock):
        try:
            msg = self.msgs.get_nowait()
            sock.sendall(self.size_struct.pack(len(msg)))
            sock.sendall(msg)
        except Empty: pass

    def send_msg(self, msg): self.msgs.put(msg)

    def do_rpc(self, funcname, args, kwargs):
        msg = {'is_rpc': True, 'payload': [funcname, args, kwargs]}
        self.msgs.put(encode(msg))
        return self.rpc_ret.get()


class Client(AbsNetwork):

    def __init__(self, port):
        AbsNetwork.__init__(self, port)
        self.udp_sock = self.srv_addr = None
        self.authenticated = False
        self._functions = []
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(('ya2.it', 8080))
        self.my_addr = sock.getsockname()[0]

    def start(self, read_cb, srv_addr):
        self.srv_addr = srv_addr
        AbsNetwork.start(self, read_cb)

    def _build_network_thread(self):
        srv, port = self.srv_addr.split(':')
        return ClientThread(srv, self.eng, int(port))

    def _configure_udp(self): pass

    def send_udp(self, data_lst, receiver=None):
        receiver = receiver if receiver else self.srv_addr
        payload = {'sender': self.my_addr, 'payload': data_lst}
        self.udp_sock.sendto(encode(payload), (receiver, self.port))

    def register_rpc(self, funcname): self._functions += [funcname]

    def unregister_rpc(self, funcname): self._functions.remove(funcname)

    def __getattr__(self, attr):
        if attr not in self._functions: raise AttributeError(attr)

        def do_rpc(*args, **kwargs):
            return self.network_thr.do_rpc(attr, args, kwargs)
        return do_rpc

    def process_udp(self):
        try:
            payload, addr = self.udp_sock.recvfrom(8192)
            payload = self._fix_payload(dict(decode(payload)))
            self.read_cb(payload['payload'], payload['sender'])
        except error: pass

    def _actual_send(self, datagram, receiver=None):
        self.network_thr.send_msg(datagram)

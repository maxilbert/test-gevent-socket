import sys, os
import time
import gevent
from multiprocessing import Process

from gevent import socket,monkey
from gevent.queue import Queue
monkey.patch_all()


class Node (Process):

    def __init__(self, port: int, nodes_list: list):
        self.queue = Queue()
        self.port = port
        self.nodes_list = nodes_list
        self.outgoing_socks = {addr: socket.socket() for addr in self.nodes_list}
        Process.__init__(self)

    def run(self):
        self._serve_forever()

    def _handle_request(self, client, address):

        def _setup(conn, rbufsize):
            print("connection from {} to port {} is under establishment...".format(address, self.port))
            return conn.makefile('rb', rbufsize)

        def _finish(rfile):
            print("server is closing...")
            rfile.close()

        rbufsize = -1
        rfile = _setup(client, rbufsize)
        try:
            while True:
                data = rfile.readline().strip()
                if data != '' and data:
                    if data == 'ping'.encode(encoding="utf-8"):
                        client.send('pong'.encode(encoding="utf-8"))
                        pass
                    self.queue.put(data)
                    print("{} sends to {}:".format(address, client) + str(data))
                else:
                    print(data)
                    print('syntax error messages')
                    time.sleep(0.005)
                    continue
        except Exception as e:
            print(e)
            _finish(rfile)

    def _serve_forever(self):
        self.ingoing_sock = socket.socket()
        self.ingoing_sock.bind(("", self.port))
        self.ingoing_sock.listen(5)
        #print("子进程运行中,pid=%d..." % os.getpid())
        while True:
            print(self.port)
            client_sock, address = self.ingoing_sock.accept()
            print(self.port)
            gevent.spawn(self._handle_request, client_sock, address)

    def connect_nodes(self):
        try:
            for addr in self.nodes_list:
                self.outgoing_socks[addr].connect(addr)
                self.outgoing_socks[addr].sendall('ping\n'.encode(encoding='utf-8'))
                pong = self.outgoing_socks[addr].recv(1024)
                if pong == 'pong'.encode('utf-8'):
                    print("{} sends to {}:".format(addr, self.outgoing_socks[addr]) + str(pong))
                    continue
                else:
                    print('connection is lost')
        except Exception as e:
            print(e)

    def _send(self, receiver: tuple, msg: bytes):
        try:
            self.outgoing_socks[receiver].sendall(msg)
        except Exception as e:
            try:
                self.outgoing_socks[receiver].connect(receiver)
                self.outgoing_socks[receiver].sendall(msg)
            except Exception as e1:
                print(e1)

    def send(self, receiver: tuple, msg: str):
        self._send(receiver, (msg + '\n').encode('utf-8'))

    def _broadcast(self, msg: bytes):
        for addr in self.nodes_list:
            self._send(addr, msg)

    def broadcast(self, msg: str):
        self._broadcast((msg + '\n').encode('utf-8'))

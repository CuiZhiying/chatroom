#!/user/bin/env python
"""
try:
    import cPickle as pickle
except:
    import pickle
"""

import select
import socket
import sys
import signal
import pickle
import struct
import argparse

SERVER_HOST = 'localhost'
CHAT_SERVER_NAME = 'server'

#common method channel is a socket object
def send(channel, *args):
    send_buffer = pickle.dumps(args);
    value = socket.htonl(len(send_buffer))
    size = struct.pack("L", value)
    channel.send(size)
    channel.send(send_buffer)

def receive(channel):
    size = struct.calcsize("L")
    size = channel.recv(size)
    try:
        size = socket.ntohl(struct.unpack("L", size)[0])
    except struct.error as e:
        return ''
    
    buf = b""
    while len(buf) < size:
        buf += channel.recv(size - len(buf))
        return pickle.loads(buf)[0]

class ChatClient(object):
    """a command lin chat client using select"""
    def __init__(self, name, port, host=SERVER_HOST):
        self.name = name
        self.connected = False
        self.host = host
        self.port = port
        #
        self.prompt= '[' + '@'.join((name, socket.gethostname().split('.')[0])) + ']> '
        # connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print("Now connected to chat server@ port {0}".format(self.port))
            self.connected = True
            send(self.sock, 'NAME: '+self.name)
            data = receive(self.sock)

            addr = data.split('CLIENT: ')[1]
            self.prompt = '[' + '@'.join((self.name, addr)) +'>'
        except socket.error as e:
            print("Failed to connect to chat server @ port {0}".format(self.port))
            sys.exit(1)

    def run(self):
        """ chat client main loop"""
        while self.connected:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()
                #waiting  for input from stdin and socket
                readable, writeable,  exceptional = select.select([0, self.sock], [], [])
                for sock in readable:
                    if sock == 0:
                        data = sys.stdin.readline().strip()
                        if data:
                            send(self.sock, data)
                    elif sock == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print("Client shutting down...")
                            self.connected = False
                            break
                        else:
                            sys.stdout.write(data+'\n')
                            sys.stdout.flush()
            except KeyboardInterrupt:
                print("Client interrupted.")
                with open('./temp.txt', 'w') as f:
                    f.write("I was excuted!")
                self.sock.close()
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Socket server example with select')
    parser.add_argument('--name', action='store', dest='name', required=True)
    parser.add_argument('--port', action='store', dest='port', type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    type(port)
    name = given_args.name
    if name == CHAT_SERVER_NAME:
        server = ChatServer(port)
        server.run()
    else:
        client = ChatClient(name=name, port=port)
        client.run()

































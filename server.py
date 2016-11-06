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
    send_buffer = pickle.dumps(args)
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


class ChatServer(object):
    """An example chat server using select"""
    def __init__(self, port, blocklog=5):
        self.clients = 0
        self.clientmap = {}
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port))
        print("Server is listening to port {0}...".format(port))
        self.server.listen(blocklog)

        signal.signal(signal.SIGINT, self.sighandler)

    def sighandler(self, signum, frame):
        """clean up client outputs"""
        #close the server
        print("Shutting down sever...")
        #close existing client sockets
        for output in self.outputs:
            output.close()
        self.server.close()

    def get_client_name(self, client):
        """Return the name of the client"""
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host)) #name@host

    def run(self):
        inputs = [self.server, sys.stdin]
        self.outputs = []
        running = True
        while running:
            try:
                readable, writeable, exceptional = select.select(inputs, self.outputs, [])
            except select.error as e:
                break

            for sock in readable:
                print(sock)

            for sock in readable:
                if sock == self.server:
                    # handle the server socket
                    #print(sock)
                    client, address = self.server.accept()
                    print("chat server: got connetion {0} from {1}".format(client.fileno(), address))

                    #read the login name
                    cname = receive(client).split('NAME: ')[1]

                    self.clients += 1
                    send(client, 'CLIENT: '+str(address[0]))
                    inputs.append(client)
                    self.clientmap[client] = (address, cname)

                    msg = "\n(Connected: New client {0} from {1}".format(self.clients, self.get_client_name(client))

                    for output in self.outputs:
                        send(output, msg)
                    self.outputs.append(client)
                elif sock == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = False

                else:
                    #handle all other sockets
                    try:
                        data = receive(sock)
                        '''
                        # using in GUI

                        if data:
                            msg = '\n#[' + self.get_client_name(sock) + ']>> ' + data
                            msg_self = '\n[' + self.get_client_name(sock) + ']>> '+ data
                            for output in self.outputs:
                                if output != sock:
                                    send(output, msg)
                                else:
                                    send(outputs, msg_self)
                        '''

                        # using in 命令行
                        if data:
                            # send as new client message
                            msg = '\n#[' + self.get_client_name(sock) + ']>> ' + data
                            for output in self.outputs:
                                if output != sock:
                                    send(output, msg)

                        else:
                            print("Chat server: {0} hung up".format(sock.fileno()))
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)

                            # Sending client leaving information
                            msg = "\n(Now hung up: client form {0})".format(self.get_client_name(sock))

                            for output in self.outputs:
                                send(output, msg)
                                #print("{0} is left {1}".format(msg, output))
                    except:
                        #remove
                        inputs.remove(sock)
                        self.outputs.remove(sock)
                        print("Exception: {0} is removed".format(sock))

        
        self.server.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Socket server example with select')
    #parser.add_argument('--name', action='store', dest='name', required=True)
    parser.add_argument('--port', action='store', dest='port', type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    #name = given_args.name
    server = ChatServer(port)
    server.run()
































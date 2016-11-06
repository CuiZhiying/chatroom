#-*- encoding utf-8 -*-

import tkinter as tk
import tkinter.scrolledtext as tkst
import socket  as sc
import select  as slct
import sys
import signal
import pickle
import struct 

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



class chat_room_client(tk.Tk):

    #default windows width and height
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        try:
            self.__root.wm_iconbitmap("chatroom.ico")
        except:
            pass

        try:
            self.__thisWidth = win_args['width']
        except:
            pass
        
        self.AppData = {
                "IP"     : tk.StringVar(),
                "port"   : tk.StringVar(),
                "name"   : tk.StringVar(),
                "server" : tk.StringVar(),
                "temp_message" : tk.StringVar(),
                "feedback" : ''
                }
        '''
        screenWidth  = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        left         = screenWidth  / 2 
        top          = screenHeight / 2
        self.geometry('%dx%d+%d+%d') % ()
        '''

        self.resizable(width=False, height=True)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, ChattingFrame):
            page_name = F.__name__
            frame     = F(container, self)
            self.frames[page_name] = frame
            #frame.grid(row=0, column=0, sticky="ewsn")

        self.raise_frame("LoginFrame")

    def raise_frame(self, page_name):
        for frame in self.frames.values():
            frame.grid_remove()
        frame = self.frames[page_name]
        frame.grid(row=0, column=0, sticky="ewsn")
        frame.tkraise()

    def get_frame_by_name(self, page_name):
        for page in self.frames.values():
            if str(page.__class__.__name__)==page_name:
                return page
        return None

    #def mainloop(self):
    #    self.mainloop()

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        tk.Label(self, text="昵称：").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(self, text="IP  ：").grid(row=1, column=0, padx=10, pady=5)
        tk.Label(self, text="端口：").grid(row=2, column=0, padx=10, pady=5)

        entry_name = tk.Entry(self, textvariable=self.controller.AppData["name"])
        entry_IP   = tk.Entry(self, textvariable=self.controller.AppData["IP"]  )
        entry_port = tk.Entry(self, textvariable=self.controller.AppData["port"])
        entry_name.grid(row=0, column=1, padx=10, pady=5)
        entry_IP.grid(row=1, column=1, padx=10, pady=5)
        entry_port.grid(row=2, column=1, padx=10, pady=5)

        tk.Button(self, text="进入聊天室", width=10, command=self.login).grid(row=3, column=0, padx=10, pady=5)
        tk.Button(self, text="退出", width=10, command=self.logout).grid(row=3, column=1, padx=10, pady=5)

    def login(self):
        feedback = "Connected to "+\
             self.controller.AppData['IP'].get()+\
             self.controller.AppData['port'].get()+"\n"
        self.controller.raise_frame("ChattingFrame")
        chatting_frame = self.controller.get_frame_by_name("ChattingFrame")
        chatting_frame.add_message(feedback)

    def logout(self):
        self.controller.destroy()




class ChattingFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.receive_message_window = tkst.ScrolledText(
                self, 
                width  = 40,
                height = 20,
                undo   = True,
                )
        self.receive_message_window['font'] = ('consolas', 12)
        self.receive_message_window.grid(
                row        = 1,
                columnspan = 2,
                padx       = 10, 
                pady       = 10, 
                sticky     = "nsew" 
                )
        self.type_message_window = tk.Text(
                self,
                width  = 40, 
                height = 5, 
                undo   = True
                )
        self.type_message_window['font'] = ('consolas', 12)
        self.type_message_window.grid(
                row     = 2,
                padx    = 10,
                pady    = 10,
                rowspan = 2, 
                sticky  = "nsew"
                )

        tk.Button(self, text="发送", width=10, command=self.send)\
                          .grid(row=2, column=1, padx=10, pady=5)
        tk.Button(self, text="退出", width=10, command=self.logout)\
                          .grid(row=3, column=1, padx=10, pady=5)
        
        self.receive_message_window.config(state=tk.DISABLED)


    def send(self):
        self.add_message(
                 self.controller.AppData['name'].get()+":"+\
                 self.type_message_window.get('1.0', tk.END)\
                 )
        self.type_message_window.delete("1.0", tk.END)

    def logout(self):
        self.controller.destroy()

    def add_message(self, new_message):
        self.receive_message_window.config(state=tk.NORMAL)
        self.receive_message_window.insert(tk.END, new_message)
        self.receive_message_window.config(state=tk.DISABLED)

def main():
    client = chat_room_client()
    client.mainloop()

if __name__ == '__main__':
    main()



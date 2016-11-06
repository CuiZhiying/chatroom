#-*- encoding utf-8 

from tkinter import *
import socket

def send():
    pass

def receive():
    pass

class chat_client(object):
    """ a chat room client using tkinter GUI, my first try """
    #variables
    __root = Tk()

    #default window with and height

    __thisWidth = 500
    __thisHeight= 500
    __login_frame = Frame(__root)
    __message_frame = Frame(__root)
    __thisMessageArea = Text(__root)
    __thisScrollBar   = Scrollbar(__thisMessageArea)

    def __init__(self, **win_args):
        
        try:
            self.__root.wm_iconbitmap("chatroom.ico")
        except:
            pass

        try:
            self.__thisWidth = win_args['width']
        except KeyError:
            pass

        self.__root.title("chat room")
#        self.__message_frame.title('chatting...')
        self.__message_frame.pack()

        screenWidth = self.__root.winfo_screenwidth()
        screenHeight= self.__root.winfo_screenheight()

        left = (screenWidth / 2) - (self.__thisWidth / 2)
        top  = (screenHeight/ 2) - (self.__thisHeight/ 2)

        self.__root.geometry('%dx%d+%d+%d'%(self.__thisWidth, self.__thisHeight, left, top))

        self.__root.grid_rowconfigure(0, weight=1)
        self.__root.grid_columnconfigure(0, weight=1)

        self.login_frame = login_frame = Frame(self.__root)
        login_frame.pack()

        Label(login_frame, text="昵称：").grid(row=0, column=0, padx=10, pady=5)
        Label(login_frame, text="IP  ：").grid(row=1, column=0, padx=10, pady=5)
        Label(login_frame, text="端口：").grid(row=2, column=0, padx=10, pady=5)

        self.name = StringVar()
        self.IP   = StringVar()
        self.port = IntVar()

        entry_name = Entry(login_frame, textvariable=self.name).grid(row=0, column=1, padx=10, pady=5)
        entry_IP   = Entry(login_frame, textvariable=self.IP  ).grid(row=1, column=1, padx=10, pady=5)
        entry_port = Entry(login_frame, textvariable=self.port).grid(row=2, column=1, padx=10, pady=5)

        Button(login_frame, text="进入聊天室", width=10, command=self.login).grid(row=3, column=0, padx=10, pady=5)
        Button(login_frame, text="退出", width=10, command=self.login).grid(row=3, column=1, padx=10, pady=5)

    def login(self):
        #self.login_frame.tkraise()
        #self.__root.destroy()
        self.__message_frame.tkraise()
    
    def run(self):
        self.__root.mainloop()
    
client = chat_client()
client.run()

# GUI learning

import tkinter as tk

class User(object):
    def __init__(self):
        self.username = ''
        self.userIP   = ''

class login_window(object):
    def __init__(self, master, user):
        tk.Label(master, text="昵称").grid(row=0, column=0)
        tk.Label(master, text="密码").grid(row=1, column=0)
        
        user.username = tk.StringVar()
        user.password = tk.StringVar()
        entry1 = tk.Entry(master, textvariable=user.username)
        entry2 = tk.Entry(master, textvariable=user.userIP)

        entry1.grid(row=0, column=1, padx=10, pady=5)
        entry2.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(master, text="登陆", width=10, command=self.show).\
                grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        tk.Button(master, text="退出", width=10, command=master.quit)\
                .grid(row=3, column=1, sticky=tk.E, padx=10, pady=5)

    def show():
        pass

if __name__=='__main__':
    user = User()
    root = tk.Tk()
    login_window(root, user)
    print(user.username, user.password)
    tk.mainloop()

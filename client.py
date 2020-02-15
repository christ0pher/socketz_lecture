import functools
import json
import socket
import threading
from queue import Queue, Empty
from tkinter import *
from tkinter import scrolledtext

import select

MSG_QUEUE = Queue()
WINDOW_QUEUE = Queue()



def read_send_thread(queue, window_queue):
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connection.connect(("localhost", 50001))
    server_connection.setblocking(False)
    stop = False
    socket_list = [server_connection]
    while not stop:
        readable, writable, exceptional = select.select(socket_list, socket_list, socket_list, 0.1)

        try:
            msg = queue.get_nowait()
            for s in writable:
                if msg:
                    s.send(json.dumps(msg).encode())
        except:
            pass

        for s in readable:
            msg = s.recv(2048)

            if len(msg) > 0:
                window_queue.put_nowait(json.loads(msg.decode()))
            else:
                s.close()
                stop = True # no reconnect


t = threading.Thread(target=functools.partial(read_send_thread, MSG_QUEUE, WINDOW_QUEUE))
t.start()


window = Tk()
window.title("Chatbox")
window.geometry('550x300')
name = Entry(window, width=40)
name.grid(column=0, row=0)
txt = scrolledtext.ScrolledText(window, width=100, height=20)
txt.grid(column=0, row=1)
def write_txt():
    try:
        msg = WINDOW_QUEUE.get_nowait()
        txt.insert(index=INSERT, chars="%s: %s\n" % (msg["chatname"], msg["message"]))
        txt.see(END)
    except Empty as e:
        pass
    except Exception as e:
        print(e)
    window.after(100, write_txt)
window.after(100, write_txt)
text_entry = Entry(window, width=40)
text_entry.grid(column=0, row=2)
def send_text():
    text_msg = text_entry.get()
    text_entry.insert(ANCHOR, "")
    MSG_QUEUE.put_nowait({"message": text_msg, "chatname": name.get()})
b = Button(window, text="send", width=10, command=send_text)
b.grid(column=0, row=3)
window.mainloop()
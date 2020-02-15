import json
import select
import socket

CLIENTS = {}

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("0.0.0.0", 50001))
serversocket.listen(5)
serversocket.setblocking(False)

read_socket_list = [serversocket]
write_socket_list = []

while True:
    readable, writable, exceptional = select.select(read_socket_list, write_socket_list, read_socket_list, 0.1)

    new_messages = []

    for read_socket in readable:
        if read_socket == serversocket: # Neue Verbindung geöffnet!
            new_connection, address = read_socket.accept()
            new_connection.setblocking(False)
            read_socket_list.append(new_connection)
            write_socket_list.append(new_connection)
            CLIENTS[address] = new_connection
            print("New client connected: %s" % str(address))
        else:  # read messages
                data = read_socket.recv(2048)
                if len(data) > 0:
                    new_messages.append(json.loads(data.decode()))
                else:
                    print("Connection closed...")
                    write_socket_list.remove(read_socket)
                    read_socket_list.remove(read_socket)
                    read_socket.close()
                    rm = None
                    for client, sock in CLIENTS.items():
                        if sock == read_socket:
                            rm = client
                    del CLIENTS[rm]
    for exception in exceptional:
        read_socket_list.remove(exception)
        rm = None
        for client, sock in CLIENTS.items():
            if sock == exception:
                rm = client
        del CLIENTS[rm]

    for sock in write_socket_list:
        for message in new_messages:
            sock.send(json.dumps(message).encode())

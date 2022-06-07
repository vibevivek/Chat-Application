import threading
import socket
host = '127.0.0.1'
port = 59000

clients=[]
usernames=[]

def parse(received):
    a1=0
    b1=0
    a2=0
    b2=0
    a3=0
    b3=0
    i=0
    l=len(received)
    while (i<l):
        if (received[i]=='['):
            if (a1==0):
                a1=i
            elif (a2==0):
                a2=i
            else:
                a3=i
        if (received[i]==']'):
            if (b1==0):
                b1=i
            elif (b2==0):
                b2=i
            elif (b3==0):
                b3=i
        i+=1
    return [received[a1+1:b1],received[a2+1:b2],received[a3+1:b3]]

def broadcast(message, s_client):
    for client in clients:
        if (client!=s_client):
            client.send(message)

def unicast(message, r_client):
    for client in clients:
        if (client==r_client):
            client.send(message)

def handle_client(client):
    while True:
        try:
            received = client.recv(1024)
            received = received.decode('utf-8')
            if (len(received)>8 and received[0:8]=='RECEIVED'):
                sender = received[10:len(received)-3]
                ind = usernames.index(sender.encode('utf-8'))
                ind2 = clients.index(client)
                dest = usernames[ind2].decode('utf-8')
                clients[ind].send(f'SEND [{dest}]\n\n'.encode('utf-8'))
            else:
                LI = parse(received)
                dest = LI[0]
                len_msg = int(LI[1])
                msg = LI[2]
                indx = clients.index(client)
                sender = usernames[indx]
                sender = sender.decode('utf-8')
                if (len(msg)==len_msg):
                    msg = f"FORWARD [{sender}]\nContent-length: [{len_msg}]\n\n[{msg}]"
                    if (dest=="ALL"):
                        broadcast(msg.encode('utf-8'), client)
                    else:
                        if (dest.encode('utf-8') in usernames):
                            index = usernames.index(dest.encode('utf-8'))
                            unicast(msg.encode('utf-8'), clients[index])
                        else:
                            client.send(f'ERROR 102 Unable to send\n\n'.encode('utf-8'))
                else:
                    unicast(f'ERROR 103 Header incomplete\n\n'.encode('utf-8'), client)
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    username = usernames[index]
                    usernames.remove(username)
                    break

        except:
            unicast(f'ERROR 103 Header incomplete\n\n'.encode('utf-8'), client)
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            usernames.remove(username)
            break


def receive():
    while True:

        server1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server1.bind((host, port))
        server1.listen()
        client, address = server1.accept()
        print(f'connection is established with {str(address)}')
        register = client.recv(1024)

        x=0
        y=0
        for i in range(len(register)):
            if (register[i]==91):
                x=i
            if (register[i]==93):
                y=i
        if (x==0 or y<=x):
            client.send(f"ERROR 101 No user registered\n\n".encode('utf-8'))
        else:
            username = register[x+1:y]
            if (username.isalnum()):    
                usernames.append(username)
                clients.append(client)
                username=username.decode('utf-8')
                print(f'{username} connected!')
                broadcast(f'{username} has connected to the chat room'.encode('utf-8'),client)

                client.send(f"REGISTERED TOSEND [{username}]\n\n".encode('utf-8'))
                thread = threading.Thread(target=handle_client, args=(client,))
                thread.start()
            else:
                client.send(f"ERROR 100 Malformed {username} \n\n".encode('utf-8'))
      

receive()

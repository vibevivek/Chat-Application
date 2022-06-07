import threading
import socket
import sys

n=len(sys.argv)
username = sys.argv[1]
IP = sys.argv[2]
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP, 59000))

flag = False

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
            elif (a3==0):
                a3=i
        if (received[i]==']'):
            if (b1==0):
                b1=i
            elif (b2==0):
                b2=i
            else:
                b3=i
        i+=1
    return [received[a1+1:b1],received[a2+1:b2],received[a3+1:b3]]

def client_receive():
    while True:
        try:
            received = client.recv(1024).decode('utf-8')
            if (len(received)>17 and received[0:17] == "REGISTERED TOSEND"):
                print("Registered on server!")
            elif (received[0]!='F'):
                print(received)
            else:
                LI = parse(received)
                sender = LI[0]
                msg_len = int(LI[1])
                message = LI[2]
                print(sender + ":" + message)
                client.send(f"RECEIVED [{sender}]\n\n".encode('utf-8'))
        except:
            print('ERROR 103 Header Incomplete\n\n')
            client.close()
            break

def client_send():
    while True:
        global flag
        if (flag==False):
            register="REGISTER TOSEND ["+username+"]\n\n"
            client.send(register.encode('utf-8'))
   
            flag=True
        else:
            dest=""
            msg=""
            flag_uni_broad = False
            while (flag_uni_broad==False):
                dest_msg = input()
                l=len(dest_msg)
                if (dest_msg[0]=='@'):
                    if (dest_msg[1]=='['):
                        i=1
                        while (i<l):
                            if (dest_msg[i]==']'):
                                dest=dest_msg[2:i]
                                break
                            i+=1
                        i+=1
                        if (dest_msg[i]==' '):
                            i+=1
                            if (dest_msg[i]=='['):
                                i+=1
                                j=i
                                while (i<l):
                                    if (dest_msg[i]==']'):
                                        msg=dest_msg[j:i]
                                        if (i==l-1):
                                            flag_uni_broad=True
                                    i+=1
                if (flag_uni_broad==False):
                    print("Invalid format, please type in correct format.\n")
            size=len(msg)
            message = f"SEND [{dest}]\nContent-length: [{size}]\n\n[{msg}]"
            client.send(message.encode('utf-8'))



receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()



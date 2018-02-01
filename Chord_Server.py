import socket
import threading
import os
import hashlib

host = ""
port = 13000
is_Part_of_chord = False
firstNode = ""
routingTable = {'predecessor':'glados.cs.rit.edu','successor':'glados.cs.rit.edu' }
list_of_files = {}

def updateListOfFiles():
    return None

# Updates the routing table for the ndoe.
# The boolean "both" indicates that both predecessor and successor are the same node
# The boolean "successor" indicates whether the successor is to be updated or the predecessor

def updateTable(hostName, successor, both):

    if both == False:
        if successor == True:
            routingTable['successor'] = str(hostName) + ".cs.rit.edu"
        else:
            routingTable['predecessor'] = str(hostName) + ".cs.rit.edu"

    else:
        routingTable['successor'] = str(hostName) + ".cs.rit.edu"
        routingTable['predecessor'] = str(hostName) + ".cs.rit.edu"

#This method is used to update the routing table of current node's successor

def updateSuccessor(successorName):
    global port
    print(successorName)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((successorName, port))

    mess1 = "update"
    sock.send(str.encode(mess1))

    mess2 = socket.gethostname()
    data3 = sock.recv(2048)
    sendFirst = data3.decode('utf-8')
    if sendFirst == "send1":
        sock.send(str.encode(mess2))

    sock.close()

    return None

# This method allows the node to join in its correct position

def joinRing(conn):
    global routingTable
    global port

    mess1 = "send"

    conn.send(str.encode(mess1))
    data1 = conn.recv(2048)
    joinerName = data1.decode('utf-8')

    print("Joiner is " + joinerName)

    checkPositionName = joinerName + ".cs.rit.edu"

    sha1Algo1 = hashlib.sha1(str.encode(checkPositionName))
    sha1Algo1 = sha1Algo1.hexdigest()
    sha1 = int(sha1Algo1, 16) % (10 ** 5)

    print(str(sha1))

    sha1Algo2 = hashlib.sha1(str.encode(routingTable['successor']))
    sha1Algo2 = sha1Algo2.hexdigest()
    sha2 = int(sha1Algo2, 16) % (10 ** 5)

    print(str(sha2))

    hosty = socket.gethostname() + ".cs.rit.edu"
    sha1Algo3 = hashlib.sha1(str.encode(hosty))
    sha1Algo3 = sha1Algo3.hexdigest()
    sha3 = int(sha1Algo3, 16) % (10 ** 5)

    print(str(sha3))

    if hosty == routingTable['successor']:

        mess2 = routingTable['successor']
        mess2 = mess2.split('.cs.rit.edu')
        mess2 = mess2[0]
        mess3 = "found"
        conn.send(str.encode(mess3))
        hostName = socket.gethostname()

        updateTable(joinerName, True, False)

        data3 = conn.recv(2048)
        sendFirst = data3.decode('utf-8')
        if sendFirst == "send1":
            conn.send(str.encode(mess2))

        data4 = conn.recv(2048)
        sendSecond = data4.decode('utf-8')
        if sendSecond == "send2":
            conn.send(str.encode(hostName))

        conn.close()

    elif sha1 < sha2 or (sha1 > sha2 and sha3 > sha2):
        mess2 = routingTable['successor']
        mess2 = mess2.split('.cs.rit.edu')
        mess2 = mess2[0]
        mess3 = "found"
        hostName = socket.gethostname()
        updateTable(joinerName, True, False)

        conn.send(str.encode(mess3))

        data3 = conn.recv(2048)
        sendFirst = data3.decode('utf-8')
        if sendFirst == "send1":
            conn.send(str.encode(mess2))

        data4 = conn.recv(2048)
        sendSecond = data4.decode('utf-8')
        if sendSecond == "send2":
            conn.send(str.encode(hostName))

        conn.close()

    else:
        print("Not my successor")
        mess4 = routingTable['successor']
        mess4 = mess4.split('.cs.rit.edu')
        mess4 = mess4[0]

        print("sending to successor : " + mess4)

        conn.send(str.encode(mess4))
        conn.close()


    return None

# This methodcauses the current node to join/create a chord ring
# if it has not already.

def join(conn):

    global routingTable
    global host
    global port
    global is_Part_of_chord
    global firstNode
    found = False
    mess3 = socket.gethostname()

    bootstrap_server = "glados.cs.rit.edu"
    bootstrap_server_port = 15000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((bootstrap_server, bootstrap_server_port))
    data = sock.recv(2048)
    reply = data.decode('utf-8')


    if reply == "First":
        hostName = socket.gethostname()
        updateTable(hostName, True, True)
        sock.send(str.encode(mess3))
        sock.close()

    else:
        firstNode = reply
        firstNode = firstNode + ".cs.rit.edu"
        sock.close()
        while not found:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((firstNode, port))
            message = "joinRing"
            s.send(str.encode(message))
            data3 = s.recv(2048)
            mess1 = data3.decode('utf-8')

            if mess1 == "send":
                s.send(str.encode(mess3))
                data4 = s.recv(2048)
                mess2 = data4.decode('utf-8')

                if mess2 == "found":

                    send1 = "send1"
                    s.send(str.encode(send1))

                    data1 = s.recv(2048)
                    successor = data1.decode('utf-8')
                    updateTable(successor, True, False)

                    send2 = "send2"
                    s.send(str.encode(send2))

                    data2 = s.recv(2048)
                    predecessor = data2.decode('utf-8')
                    updateTable(predecessor, False, False)

                    is_Part_of_chord = True
                    s.close()
                    print(routingTable['successor'])
                    updateSuccessor(routingTable['successor'])
                    found = True

                else:
                    print("Was not found")
                    firstNode = mess2
                    print(firstNode)
                    s.close()


            else:
                print("Error occurred. Could not join ring")
                is_Part_of_chord = False
                found = True
                s.close()

    return None

def leave(conn):
    global port
    global is_Part_of_chord
    global list_of_files

    succ = routingTable['successor']
    pred = routingTable['predecessor']

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((succ, port))

    mess2 = pred
    succ = succ.split('.cs.rit.edu')
    mess4 = succ[0]

    mess1 = "update"
    s.send(str.encode(mess1))

    data2 = s.recv(2048)
    reply1 = data2.decode('utf-8')
    if reply1 == "send1":
        mess2 = mess2.split('.cs.rit.edu')
        mess2 = mess2[0]
        s.send(str.encode(mess2))
        # send all files to successor too

    s.close()

    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1.connect((pred, port))

    mess3 = "updateS"
    s1.send(str.encode(mess3))

    data3 = s1.recv(2048)
    reply2 = data3.decode('utf-8')
    if reply2 == "send2":
        s1.send(str.encode(mess4))

    s1.close()

    is_Part_of_chord = False
    list_of_files = []
    hostName = socket.gethostname()
    updateTable(hostName, False, True)

    return None

def insert(conn):
    mess1 = "go"
    conn.send(str.encode(mess1))
    data1 =conn.recv(2048)
    fileName = data1.decode('utf-8')
    pathname = r"ass4909/" + str(socket.gethostname())

    if os.path.exists(pathname):
        pathname1 = os.path.join(pathname, fileName)
        if os.path.exists(pathname1):
            mess2 = "Exists"
            conn.send(str.encode(mess2))
            conn.close()
    else:
        mess2 = "fresh"
        conn.send(str.encode(mess2))
        os.makedirs(pathname)
        pathname2 = os.path.join(pathname, fileName + ".txt")
        file1 = open(pathname2, "w")
        toFile = "yes"
        file1.write(toFile)
        file1.close()

    return None

def search(conn):
    mess1 = "go"
    conn.send(str.encode(mess1))
    data1 =conn.recv(2048)
    fileName = data1.decode('utf-8')
    pathname = r"ass4909/" + str(socket.gethostname())
    pathname1 = os.path.join(pathname, fileName)
    if os.path.exists(pathname1):
        print()
    else:

        mess2 = "no"
        conn.send(str.encode(mess2))
        conn.close()

    return None

# Displays information about the current host such as
# currentHostName, successor and predecessor and list of file names, etc
def view(hostName):
    count = 1
    print("Information about current Node : ")
    print("Name of this host : " + str(hostName))
    print("Successor is : " + str((routingTable['successor'])) )
    print("Predecessor is : " + str((routingTable['predecessor'])))
    print("List of data items stored at this node :")
    for key in routingTable:
        print(str(count) + " : " + str(routingTable[key]))
        count+=1

    return None

# The main method which offers options to the user and executes actions
def Main():

    global host
    global port
    global is_Part_of_chord

    End = True
    host = socket.gethostname() + ".cs.rit.edu"
    ip = socket.gethostbyname(host)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host,port ))
    print("Server is up and running")

    # each server can handle up to 5 clients at one time. The 6th client will get rejected
    sock.listen(5)

    while End:
        conn, addr = sock.accept()
        print("Client" + str(addr) + " has connected")

        data = conn.recv(2048)
        inp = data.decode('utf-8')
        print(str(inp))

        if inp == "insert":
            t = threading.Thread(target = insert, args = (conn, ))
            t.start()

        elif inp == "search":
            t = threading.Thread(target = search,  args = (conn))
            t.start()

        elif inp == "update":
            send1 = "send1"
            conn.send(str.encode(send1))

            data1 = conn.recv(2048)
            newPredecessor = data1.decode('utf-8')
            updateTable(newPredecessor, False, False)
            conn.close()

        elif inp == "updateS":
            send2 = "send2"
            conn.send(str.encode(send2))

            data1 = conn.recv(2048)
            newSuccessor = data1.decode('utf-8')
            updateTable(newSuccessor, True, False)
            conn.close()

        elif inp == "join" :
            if not is_Part_of_chord:
                t = threading.Thread(target = join, args = (conn, ))
                t.start()
                message = "success"
                conn.send(str.encode(message))
                conn.close()

            else:
                message = "fail"
                conn.send(str.encode(message))
                conn.close()

        elif inp == "joinRing":
            t = threading.Thread(target= joinRing, args = (conn, ))
            t.start()

        elif inp == "leave":
            t = threading.Thread(target = leave, args = (conn, ))
            t.start()

        elif inp == "view":
            t = threading.Thread(target = view, args = (host, ))
            t.start()

        elif inp == "kill":
            t = threading.Thread(target = leave, args = (conn, ))
            t.start()
            print("Server has been closed")
            End = False

        else:
            print("Invalid keyword entered. Please try again")

    sock.close()

    return None

Main()
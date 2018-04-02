###############################
### CISC 435 Course Project ###
###############################

from socket import *
from threading import Thread
from random import randint
from SocketServer import ThreadingMixIn
import urllib2

__author__ = "Eric Lee"
__copyright__ = "Copyright 2017"
__credits__ = ["Eric Lee"]

__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Eric Lee"
__email__ = "lee.eric@queensu.ca"
__status__ = "Development"

serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('',serverPort))

# Maximum number of clients that the server can handle.
MAX_CONN = 3

# Table of all (non-active) client usage data.
clientRecord = []

# Construct a table which stores information about currectly active client(s).
defaultClientTable = [{'Name': None, 'Socket': None, 'Address': None, 'Code': None, 'Category': None, 'Quota': 0, 'NumOfRequestedURLs': 0, 'RequestedURLs': []}] * MAX_CONN

# Create a shallow copy of the default client table.
clientTable = [defaultClientTable[client].copy() for client in range(MAX_CONN)]

# Make a copy of the list of requested URLs from each client.
for client in range(MAX_CONN):
	clientTable[client]['RequestedURLs'] = clientTable[client]['RequestedURLs'][:]


class ClientThread(Thread):

    def __init__(self,addr):
        Thread.__init__(self)
        self.ip = addr[0]
        self.port = addr[1]
        self.handled = False
        print "[+] New server socket thread started for " + self.ip + ":" + str(self.port)

    def getCategory(self, codeNum):
        """ Returns the corresponding category depending on randomly assigned access code """
    
        if int(codeNum) % 10 == 0:
            return "Platinum"
    
        if int(codeNum) % 2 == 0:
            return "Silver"
        else:
            return "Gold"
    
    def getQuota(self, codeNum):
        """ Returns the quota that a client is eligible - For record purposes only,
            since quota counter is implemented on the client side. """
    
        if int(codeNum) % 10 == 0:
            return "Unlimited"
    
        if int(codeNum) % 2 == 0:
            return 3
        else:
            return 5
    
    def getAccessCode(self):
        """ Returns a randomly assigned access code to a client between 50 and 300. """
    
        return randint(50, 300)
    
    def resetClient(self):
        """ Returns an empty client record to be replaced in the (active) client table
            should the client's quota exceed, or if the client terminates the connection. """
    
        return {'Name': None, 'Socket': None, 'Address': None, 'Code': None,
        'Category': None, 'Quota': 0, 'NumOfRequestedURLs': 0,
        'RequestedURLs': []}

    def run(self):
        
        global clientRecord, clientTable

        # Dictionary of dummy URLs and their responses.
        dummyResponses = { "http://www.abc.com/abc": "ABC",
                     "http://www.abc.com/def": "DEF",
                     "http://www.abc.com/xyz": "XYZ" }

        # Boolean to check if connection was closed from the client side.
        connectionClosedByClient = False
        
        while not connectionClosedByClient:
        
            # Create an entry in the client table.
            # Each client created is assigned a name and a random access code.
            for i in range(MAX_CONN):
                if not clientTable[i]['Name']:
                    clientTable[i]['Name'] = 'client' + str(i+1)
                    clientTable[i]['Socket'] = addr[1]
                    clientTable[i]['Address'] = addr[0]
                    accessCode = self.getAccessCode()
                    clientTable[i]['Code'] = accessCode
                    clientTable[i]['Category'] = self.getCategory(accessCode)
                    clientTable[i]['Quota'] = self.getQuota(accessCode)
                    break

            while True:

                if connectionClosedByClient:
                    break

                try:

                    # Receive requests from client.
                    requestedURL = connectionSocket.recv(1024)
                    print "Requested URL from " + self.ip + ":" + str(self.port) + " : " + requestedURL

                    for slot, client in __builtins__.enumerate(clientTable):

                        if client['Socket'] == self.port:

                            # Send available quota initially.
                            if requestedURL == "quota":
                                connectionSocket.send(str(client['Quota']))
                                break

                            # If a client issues an exit, add the client's usage information to the client record table,
                            # and clear the (active) client table entry.
                            if requestedURL == 'exit':
                                connectionSocket.send("Your connection will be closed shortly.")
                                clientRecord.append(client)
                                clientTable[slot] = self.resetClient()
                                print "clientTable:", clientTable
                                print "clientRecord:", clientRecord
                                connectionClosedByClient = True
                                print "Connection closed by client at", self.ip + ":" + str(self.port)
                                break
                            
                            # Record the requested URL as well as increment the number of requests.
                            client['NumOfRequestedURLs'] += 1
                            client['RequestedURLs'].append(requestedURL)
                            
                            # The requested URL needs to start with http:// to request real responses
                            if not requestedURL.startswith("http://"):
                                requestedURL = "http://" + requestedURL
                            
                            # if client usage is requested (only possible by Platinum users)
                            if requestedURL == "http://clientsusage.com":

                                # send active and non-active client information
                                connectionSocket.send("\n\nActive clients: " + str(clientTable) + "\n\n" + "Non-active clients: " + str(clientRecord) + "\n")

                            else: # for all other URLs by any client

                                # if dummy URL is found in list of dummy responses
                                if requestedURL in dummyResponses.keys():
                                    
                                    # Send dummy response to client.
                                    connectionSocket.send(dummyResponses[requestedURL])

                                else:

                                    # Send real URL response back to client.
                                    response = urllib2.urlopen(requestedURL)
                                    http = response.read()
                                    connectionSocket.send(http)

                                break

                except: # catch any exceptions

                    connectionClosedByClient = True
                    clientRecord.append(client)
                    clientTable[slot] = self.resetClient()
                    print "clientTable:", clientTable
                    print "clientRecord:", clientRecord
                    print "Error: Connection closed by client at", self.ip + ":" + str(self.port)
                    break


threads = []
print "Server ready : Waiting for connections from TCP clients..."
while True:

    serverSocket.listen(5)
    connectionSocket, addr = serverSocket.accept()

    for t in threads:
        if not t.is_alive():
            t.handled = True
    threads = [t for t in threads if not t.handled]

    # accept connections from outside only if the number of active users is < 3
    if len(threads) < MAX_CONN:
        
        clientthread = ClientThread(addr)
        clientthread.daemon = True
        clientthread.start()
        threads.append(clientthread)

    else:

        connectionSocket.send("Maximum number of users exceeded. Please try again later.")

connectionSocket.close()

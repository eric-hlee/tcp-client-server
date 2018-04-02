###############################
### CISC 435 Course Project ###
###############################

from socket import *

__author__ = "Eric Lee"
__copyright__ = "Copyright 2017"
__credits__ = ["Eric Lee"]

__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Eric Lee"
__email__ = "lee.eric@queensu.ca"
__status__ = "Development"

serverName = 'localhost'
serverPort = 12000

clientSocket1 = socket(AF_INET, SOCK_STREAM)
clientSocket1.connect((serverName,serverPort))

print "############## Client 1 ###############"

def isInfQuota(quota):
    
    if quota == "Unlimited":
        return True

    return False

requestQuota = True

while True:

    try:

        if requestQuota:
            clientSocket1.send("quota")
            quota = clientSocket1.recv(1024)
            
            if quota == "Maximum number of users exceeded. Please try again later.":
                print quota
                break
            
            print "Your quota:", quota
            
            if quota != "Unlimited":
                quota = int(quota)
                           
            requestQuota = False
        
        if quota == 0 and not isInfQuota(quota):
            clientSocket1.send('exit')
            break

        urlToRequest = raw_input("Input URL to request (or press Enter to disconnect): ")

        if urlToRequest == "http://clientsusage.com":
            if quota != "Unlimited":
                print "Sorry, only Platinum members are allowed to view clients usage.\n"
                
            else:
                clientSocket1.send(urlToRequest)
                receivedData = clientSocket1.recv(1024)
                print "Response from server:", receivedData
                
        else:

            if not requestQuota:
                
                if urlToRequest == '':
                    clientSocket1.send('exit')
                else:
                    clientSocket1.send(urlToRequest)

                receivedData = clientSocket1.recv(1024)
                print "Response from server:", receivedData

                if receivedData == "You have reached your quota... Connection will be closed." or receivedData == "Your connection will be closed shortly.":
                    break
                
                if quota != "Unlimited":
                    quota -= 1

    except:
        
        print "There was an error connecting to the server. Please try again later."
        break

print "Your connection has been terminated."
clientSocket1.close()

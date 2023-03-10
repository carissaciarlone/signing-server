import socket               
import ssl
import sys


def recv_all(s):
	BUFF_SIZE = 4096
	data = b''
	while True:
		part = s.recv(BUFF_SIZE)
		data += part
		if len(part) < BUFF_SIZE:
			break
	return data


#declare the host/server name
hostname = 'quimby02.aus.stglabs.ibm.com' 
#declare the port 
port = 6000 

#set up the context to create an SSL socket
context = ssl.SSLContext(ssl.PROTOCOL_TLS)
#lpcate the client certificate
context.load_verify_locations('/ssl_nimsh/certs/client.pem')
# Create a socket object 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
#wrap the socket with the SSL context
s = context.wrap_socket(sock, server_hostname = hostname)
    

# connect to the server of specified hostname and port number
s.connect((hostname, port)) 


#declare the path where the files are in for signing
if (len(sys.argv) > 1):
	file_loc = '/{0}'.format(sys.argv[1])
else:
	file_loc = '/export/nim/redfly/installp/ppc'


#send server the location of files to be signed
s.send(file_loc.encode())

#recieve an 'ls' on the location indicated to server
file_list = (recv_all(s)).decode()

print (file_list.replace('\\', '\n'))
#recieve relevant signature from the server and display that
print (recv_all(s))
#print location of signature file
print (recv_all(s))


#close the connection
s.close()  
print ('Disconnected from ' + hostname)
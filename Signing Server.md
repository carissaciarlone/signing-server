# Signing Server Documentation

# Table of Contents
1. [Setup](#setup)
	2. [Requirements](#requirements)
2. [Running the Program](#running-program)
3. [Server](#server)
	4. [Subroutines](#server-subroutines)
4. [Client](#client)
	4. [Subroutines](#client-subroutines)
5. [Output](#expected-output)


## Setup

### Requirements 
The user must have both the server.py file and the client.py file or have the server already be running externally. If the server is running externally, disregard the [running program](#running-program) sections server call and just initiate the client call.

The communication between the server and client relies on both of them utilizing the same port to listen and communicate on, for this project, `port 6000` is utilized for communication. As long as nothing else is using that specified port on the server, the client and server should have no issues connecting and communicating.

The secure socket connection between the client and the server relies on being able to read in certifications. An administrator of your python web service must provide a key for the client to use. The client would place that key in their .ssh folder. 

## Running Program
From the directory that contains the server.py, begin the server by calling: 

```python 
python server.py 
```

This call begins the server and waits for a client connection


To connect to the server and initiate the signing process, go to the directory containing the client.py file and call:

```python 
python client.py $FILE_LOCATION
```

Here, the file location is the file(s) the client wishes to have signed. This argument is optional and if it is not used, the server will attempt to sign the files in the current working directory.

Provided no errors, the client is now connected to the server and able to communicate back and forth between themselves.



## Server
The signing server provides a simple way for the user to get their package(s) signed. The signing server provides information relevant to the signing of the clients package(s) and success/failure codes when the signature is attempted. 


The server sets up a python socket that is created using a predefined port and the server's hostname. The socket is wrapped with SSL context in order to only allow secure connections. 
 
To create the wrapper, a context must be set. This is done using ` ssl.SSLContext(ssl.PROTOCOL_TLS)` which basically allows for the private certificate to be loaded

The socket is then created using `socket.socket()` 

Once the socket is created, it now waits for an incoming connection to come in with the correct credentials. The connection is made through the `socket.accept()` call

Once the incoming connection comes in, the server waits for the client to send over information about the location of the file they want signed. The location is retrieved by a `.recv` command

The server then checks whether the location specified is a directory or a file. If it is a directory, it checks whether it has the proper permissions to create signatures with it. If it does, it `socket.sendall()` the `ls <directory\> `. If  the client specified a path that leads to a specific file, it returns that path to the client.

Next, the server runs the `create_pkgsign` command which creates a signature for the file(s) indicated by the signature

The server then parses through the generated signature file and stores as well as sends the relevant signing information over to the server.

The server then closes the connection with the client and remains running waiting for the next incoming connection

### Server Subroutines
The first subroutine is package_sign which takes in the path provided by the client, the file name to be signed, the dictionary which stores the signatures, and the file in which the signatures will be written to.
This subroutine calls the package sign command on each file in the directory indicated by the client or the file if the client indicated a file. This will then create both a dictionary and write to a file the relevant signature information

This subroutine invokes format_sign which formats how the dictionary stores the information. This dictionary is returned to the client and displayed to the client on return.

## Client

The client must be start while the server is listening(actively open) or else a `socket.error: [Errno 79] Connection refused` will occur.

Once the server is  start, the client specifies the hostname of the server and the port which the server is listening on.

This is used in context to create a secure socket binder to the same location the server is listening on

The client now connects by calling `s.connect((hostname, port))` which creates the connection between the client and the server.

The user now indicates where the files they want signed are located and sends that to the server

The client then waits for information from the server by doing a `recv()`

The server then cuts off the connection and the client displays the connection has ended


### Client Subroutines
`recv_all` is a subroutine in client that keeps the communication between the client and server open until it fully retrieves the data the server sends over
```python
def recv_all(s):
	BUFF_SIZE = 4096
	data = b''
	while True:
		part = s.recv(BUFF_SIZE)
		data += part
		if len(part) < BUFF_SIZE:
			break
	return data
```


## Expected Output
Anything following a $ below indicates unique response based on user input. 

When the server is running and the client has not connected yet, the server's output should be

```console
 :>python server.py
Socket successfully created
socket binded to 6000
socket is listening
```
Once a client connects, the server should have output as follows:

```console
('Got connection from', ($IP_ADDR, $PORT))
```

Note that this port is not the same as the port in which the client and server communicate on. This port is the service endpoint.

The client then receives output as follows:

```console
List of files in $CLIENT_PATH:
$FILENAME
$FILENAME
...

$FILENAME: {"keyid": $KEYID, "package": $PACKAGE, 
"timestamp": $TIMESTAMP, "fileset": $FILESET, 
"ftype": $FTYPE, "vrmf": $VRMF, "signature": 
$SIGNATURE}

$FILENAME: {"keyid": $KEYID, "package": $PACKAGE, 
"timestamp": $TIMESTAMP, "fileset": $FILESET, 
"ftype": $FTYPE, "vrmf": $VRMF, "signature": 
$SIGNATURE}
...
```


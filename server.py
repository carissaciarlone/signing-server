import socket 
import ssl       
import os
import subprocess
import json

def package_sign(client_path, file, signature_dict, pkgsign_file):
  client_path = client_path + '/{0}'.format(file)
  #generate the signature and sign the file(s)
  pkg_command = 'create_pkgsign -a infile={0} -a passin=/etc/security/pkgverify/keystore/pswd.file /tmp/signature.$$'.format(client_path)
  subprocess.call(pkg_command, shell=True)
  #retrieve the signature file name based on last signature file generated
  signature_id = subprocess.check_output('ls -Art | tail -n 1', shell=True).decode()
  #remove the headers and grab the relevant information to the signing string
  signing_info = ((subprocess.check_output('cat {0}'.format(signature_id), shell=True)).decode())
  if ('==' in signing_info):
    signing_info = '\n{0}\n'.format(signing_info[0:signing_info.index('==')])
    pkgsign_file.write(signing_info)
    signature_dict = format_sign(signing_info.replace('#package:fileset:vrmf:ftype:keyid:timestamp:signature', '').strip(), signature_dict)

  return signature_dict

def format_sign(signing_info, signature_dict):
  package, fileset, vrmf, ftype, keyid, timestamp, signature = signing_info.split(':')
  signature_dict[file] = {}
  signature_dict[file] = {'package': package, 'fileset': fileset, 'vrmf': vrmf, 'ftype': ftype, 'keyid': keyid, 'timestamp': timestamp, 'signature': signature}
  return signature_dict


#set up the context to create an SSL socket
context = ssl.SSLContext(ssl.PROTOCOL_TLS)
#load the server certificate and the private key
context.load_cert_chain('/ssl_nimsh/certs/server.pem', '/ssl_nimsh/keys/serverkey.pem')

#create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
print ('Socket successfully created')

#declare the port number
port = 6000
#bind the socket to the fetched server host name and the declared port
sock.bind((socket.gethostname(), port))
print ('socket binded to {0}'.format(port) )

#waits for connection
sock.listen(5)
print ('socket is listening') 

#wrap the socket with the SSL context
s = context.wrap_socket(sock, server_side=True) 



#infinite loop, breaks on error
while True:
  #accepts client communication
  c, addr = s.accept()
  print ('Got connection from', addr )
  #grab the filepath from the client and point it to a correct location
  client_path = c.recv(1024).decode()


  #check that the file path exists and the permissions are in order, if it does give an 'ls' of that location otherwise return not found
  if (os.path.isdir(client_path)):
    try:
      dirs = os.listdir( client_path )
    except OSError as err:
      c.send( str(err) )
      c.close()
      break

    f = subprocess.check_output('ls {0}'.format(client_path), shell=True).decode()

    signature_dict = {}
    f = ''
    count = 0
    pkgsign_file = open('signatures.txt' , 'w')
    for file in dirs:
      f += file + '\n'
      if (count < 10):
        signature_dict = package_sign(client_path, file, signature_dict, pkgsign_file)
        count += 1
    
    #return a list of files in the given client directory
    c.sendall('List of files in {0}:\n{1}'.format(client_path, f).encode())

  #if given a path for a specific file just return that file name
  else:
    c.sendall('File to be signed: {0}\n'.format(client_path).encode())
    signature_dict = package_sign(client_path, '', {})
 
  dict_json = json.dumps(signature_dict)
  c.sendall(dict_json.encode())
  c.sendall('\nSignatures written to: {0}\n'.format(pkgsign_file).encode())
  pkgsign_file.close()
  
  #end the connection and stay open awaiting connection until terminated 
  c.close()

    
             

  
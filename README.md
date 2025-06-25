# CS project - altcoin (ilancoin) mining pool

## setup instructinos:
### server:
install the required packages from other/requirements.txt
configure the database and the rpc in the server-main.py file

run the src/server-main.py file 

### client:
install the required packages from other/requirements.txt

run the other/client_gui.py file in the client directory

## client to server communication protocol

the communication from the client to the server will begin with a header that will include
- length - 4 bytes
- operation - 1 byte
- checksum - 4 byte

header size - 9 bytes

the content of the message will be determined by the operation byte:

0 - request mining params

the message should only include the public key hash (address) of the client

1 - submit work
message = [public key hash (address) | block header hex string]

2 - submit block
message = [public key hash (address) | full block hex string]

3 - RSA public key sent

the message should only include the RSA public key

## server to client communication protocol

the communication from the server to the client will begin with a header that will include
- length - 4 bytes
- operation - 1 byte
- checksum - 4 bytes

the content of the message will be determined by the operation byte:

0 - bad block/work submitted

the message should just have an explanation of what the problem with the block is

1 - work submitted properly

the message should only contain the public key hash (address) of the client

2 - mining params

the message should contain the mining parameters as a json blob 

3 - send AeS key

should send the AES key only, encrypted with the RSA public key of the client 

## database layout

this is a very simple database, there is only one table

work: public key hash (char()) - work done (int)



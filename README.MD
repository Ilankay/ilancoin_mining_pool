# CS project - altcoin (ilancoin) mining pool

## client to server communication protocol

each communication must begin with the wallet address of the sender - 20 bytes 

then the communication must have the code for the contents of the rest of the message and the last 32 bytes (256 bits) of the communication will be defined according to this value stored in a byte

0 - quit, closes the connection last 256 bits will be ignored

1 - work made, sent when a hash is found with the amount of zeros required for accquiring a work point, last 256 bits of the communication will be the hash

2 - block found, sent when a block is found, the last 256 bits of the communication will be the hash

3 - initiate client, sent when this is the first time the client is trying to mine, the last 256 bits of the communication will be empty

total length = 20+1+32 = 53

## server to client communication protocol

each communication must begin with the public key of the server walllet - 20 bytes

then the communication must have the code (1 byte) for the contents of the message, there is an aditional byte after this that is defined by the contents of the code

0 - kick, closes the connection, bit after will be ignored

1 - work made, bit after will be on if work made is validated and off if work made is invalid

2 - block found, bit after will be on if block found validated and off if block found is invalid

3 - initiate client, bit after will be ignoredi

total length = 20 +1 +1 = 22

## database layout

this is a very simple database, there is only one table

work: public key (char()) - work done (int)

## todo

### server:
- write add_client method 
- write add_work method (with actual validation)
- write block found method (with actual validation)
- write a method to formulate a response to the client
- add stdio interface with admin that allowes interactions with db

### client:
- get the miner class to return every set amount of time a number with the correct size and a weighted random amount of zeros
- multithread the miner
- add an stdio interface for the client to interact with the admin
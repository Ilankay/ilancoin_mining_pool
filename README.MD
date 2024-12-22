# CS project - altcoin (ilancoin) mining pool

## client to server communication protocol

each communication must begin with the public key of the sender - 512 bits

then the communication must have the code for the contents of the rest of the message and the last 256 bits of the communication will be defined according to this value

0 - quit, closes the connection last 256 bits will be ignored
1 - work made, sent when a hash is found with the amount of zeros required for accquiring a work point, last 256 bits of the communication will be the hash
2 - block found, sent when a block is found, the last 256 bits of the communication will be the hash
3 - initiate client, sent when this is the first time the client is trying to mine, the last 256 bits of the communication will be empty

total length = 512 + 2 + 256 = 770

## server to client communication protocol

each communication must begin with the public key of the client - 512 bits

then the communication must have the code for the contents of the message, there is an aditional bit after this that is defined by the contents of the code

0 - kick, closes the connection, bit after will be ignored
1 - work made, bit after will be on if work made is validated and off if work made is invalid
2 - block found, bit after will be on if block found validated and off if block found is invalid
3 - initiate client, bit after will be ignoredi

total length = 512 + 2 + 1 = 515

## database layout

this is a very simple database, there is only one table
work: public key (char()) - work done (int)
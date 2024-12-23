class CloseConn(Exception):
    """ an exception to throw in order to close a client connection"""
    pass

class ClientExists(Exception):
    """ an exception to throw when a client already exists when trying to add it"""
    pass
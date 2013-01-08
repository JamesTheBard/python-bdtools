#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:et:ai

class SourceNotDefinedError(Exception):
    
    def __init__(self, message):
        Exception.__init__(self, message)

    def __str__(self):
        return repr( self.message )

class SourceNotFoundError(Exception):

    def __init__(self, message, source):
        Exception.__init__(self, message)
        self.source = source

    def __str__(self):
        return repr( self.message )

class FileNotFoundError(Exception):

    def __init__(self, message, filename):
        Exception.__init__(self, message)
        self.filename = filename

    def __str__(self):
        return repr( self.message )

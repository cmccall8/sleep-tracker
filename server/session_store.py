import os
import base64

class SessionStore:

    def __init__(self):
        self.sessions = {}

    #load session data
    def getSessionData(self,sessionID):
        #check dictionary for given sessionID
        if sessionID in self.sessions:
            #if found return it
            return self.sessions[sessionID]
        # otherwise ????
        #return None -- i dont have that (no 404 this is not the server just a helper class)
        else:
            #this only happens when we lose the file folder
            #at this point they need a new session
            return None

    #create new session
    def createSession(self):
        #why self here???
        sessionID = self.generateSessionID()
        #create new empty dictionary as new session
        #little dictionary inside larger one
        #sessionID acts as the key
        self.sessions[sessionID] = {}
        return sessionID

    def generateSessionID(self):
        #true random data (better than randrange 32 is the about of bytes)
        #could add a While loop through dict so that each id is garunteed unique
        rnum = os.urandom(32)
        #make data a string w/ base64 encoding
        rstr = base64.b64encode(rnum).decode("utf-8")
        return rstr

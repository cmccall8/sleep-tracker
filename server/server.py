from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from passlib.hash import bcrypt
import json
from sleeplogs_db import SleepLogDB
from http import cookies
from session_store import SessionStore

#global session store
#this way from request to request data is saved (doesn't start over every time)
#why does it start over and lose data between steps???
gSessionStore = SessionStore()

class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        #hijacking end headers to send cookies with every response
        #replacing end_headers with sending cookie Data
        #then including the actual end_headers function
        self.send_cookie()
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        #must call end_headers on the parent class manually
        #otherwise end_headers will break
        BaseHTTPRequestHandler.end_headers(self)


    #create a cookie object and save in self.cookie
    #client to server
    def load_cookie(self):
        #read a header
        #capture the cookie
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        # or create cookie if one doesn't already exist
        else:
            self.cookie = cookies.SimpleCookie()

    #server to client
    def send_cookie(self):
        #write a header
        #sending cookie data(if any)
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())

    #master algorithm
    #using cookie data, load session data into self.sessionData
    #??? fuzzy on why sessionData needs to repeat so many times
    def loadSessionData(self):
        #fist load cookie data
        #loads all cookie data
        self.load_cookie()
        #if sessionID is found in the cookie
        if "sessionID" in self.cookie:
            #load sessionID from the cookie
            sessionID = self.cookie["sessionID"].value
            #then use sessionID to load session data from the session store
            self.sessionData = gSessionStore.getSessionData(sessionID)
            #save session data into variable for use later(anytime it is loaded or created)
            #IF the session data does NOT exist in the sessions store
            if self.sessionData == None:
                #server was likely restarted
                #re-create session and issue new sessionID to cookie
                sessionID = gSessionStore.createSession()
                #save session data into variable for use later
                self.sessionData = gSessionStore.getSessionData(sessionID)
                #save in cookie
                self.cookie["sessionID"] = sessionID
        #otherwise if no session ID in cookie
        else:
            #then create new session in the session session session store
            sessionID = gSessionStore.createSession()
            #and create new cookie with new sessionID
            self.sessionData = gSessionStore.getSessionData(sessionID)
            #save session data into variable for use later
            #save in cookie
            self.cookie["sessionID"] = sessionID


    def handleNotFound(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(json.dumps("Not Found"), "utf-8"))

    def handleRetrieveMember(self, log_id):
        #ENFORCE AUTHORIZATION (user is logged in)
        if "userID" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            #must return here so they can't move on
            return

        db = SleepLogDB()
        onelog = db.getOneSleeplog(log_id)
        if onelog:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(onelog), "utf-8"))
        else:
            self.handleNotFound()


    def handleRetrieveCollection(self):
        #ENFORCE AUTHORIZATION (user is logged in)
        if "userID" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            #must return here so they can't move on
            return

        #what is this for?
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        db = SleepLogDB()
        alllogs = db.getAllSleeplogs()
        self.wfile.write(bytes(json.dumps(alllogs), "utf-8"))

    def handleLogCreate(self):
    #ENFORCE AUTHORIZATION (user is logged in)
        if "userID" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            #must return here so they can't move on
            return

        db = SleepLogDB()
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("RAW body:", body)
        parsed_body = parse_qs(body)
        print("Parsed data:", parsed_body)
        day = parsed_body["day"][0]
        hours = parsed_body["hours"][0]
        phone = parsed_body["phone"][0]
        late = parsed_body["late"][0]
        mood = parsed_body["mood"][0]

        db.insertSleepLog(day,hours,phone,late,mood)

        self.send_response(201)
        self.end_headers()

    def handleSessionCreate(self):
        db = SleepLogDB()
        #read all data from the body
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("RAW body:", body)
        parsed_body = parse_qs(body)
        print("Parsed data:", parsed_body)

        email = parsed_body["email"][0]
        password = parsed_body["password"][0]
        #encrypted_password = bcrypt.verify(password, hash)

        user = db.checkUserByEmail(email)
        if user:
            checkPassword = bcrypt.verify(password, user['usersxyzzy'])
            if checkPassword:
                self.send_response(201)
                self.end_headers()
                #SAVE USERS ID INTO SESSION DATA
                self.sessionData["userID"] = user["id"]
            else:
                self.send_response(401)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(json.dumps("Not Authenticated"), "utf-8"))
        else:
            self.send_response(401)
            self.end_headers()

    def handleUserCreate(self):
        db = SleepLogDB()
        #read all data from the body
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("RAW body:", body)
        parsed_body = parse_qs(body)
        print("Parsed data:", parsed_body)

        fname = parsed_body["fname"][0]
        lname = parsed_body["lname"][0]
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]
        encrypted_password = bcrypt.hash(password)

        user_check = db.checkUserByEmail(email)
        if user_check == None:
            db.insertUser(fname,lname,email,encrypted_password)

            self.send_response(201)
            self.end_headers()
        else:
            self.send_response(422)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes(json.dumps("Unprocessable"), "utf-8"))

    def handleLogDeleteMember(self, log_id):
        #ENFORCE AUTHORIZATION (user is logged in)
        if "userID" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            #must return here so they can't move on
            return

        db = SleepLogDB()
        onelog = db.getOneSleeplog(log_id)
        if onelog:
            # delete
            db.deleteSleepLog(log_id)
            self.send_response(200)
            self.end_headers()
        else:
            self.handleNotFound()

    def handleLogUpdateMember(self,log_id):
        #ENFORCE AUTHORIZATION (user is logged in)
        if "userID" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            #must return here so they can't move on
            return

        #update
        db = SleepLogDB()
        onelog = db.getOneSleeplog(log_id)
        if onelog:
            # update
            length = self.headers["Content-Length"]
            body = self.rfile.read(int(length)).decode("utf-8")
            print("RAW body:", body)
            parsed_body = parse_qs(body)
            print("Parsed data:", parsed_body)
            day = parsed_body["day"][0]
            hours = parsed_body["hours"][0]
            phone = parsed_body["phone"][0]
            late = parsed_body["late"][0]
            mood = parsed_body["mood"][0]

            db.updateSleepLog(day,hours,phone,late,mood,log_id)

            self.send_response(200)
            self.end_headers()
        else:
            self.handleNotFound()


    def do_GET(self):
        self.loadSessionData()
        #load session data anytime you might have a request
        #don't need in handlers if they are in REST endpoints
        path_parts = self.path.split("/")
        resource = path_parts[1]
        if len(path_parts) > 2:
            identifier = path_parts[2]
        else:
            identifier = None

        if resource == "sleeplogs" and identifier == None:
            self.handleRetrieveCollection()

        elif resource =="sleeplogs" and identifier != None:
            self.handleRetrieveMember(identifier)
        else:
            self.handleNotFound()

    def do_POST(self):
        self.loadSessionData()
        #load session data anytime you might have a request
        db = SleepLogDB()
        if self.path == "/sleeplogs":
            self.handleLogCreate()
        elif self.path == "/users":
            self.handleUserCreate()
        elif self.path == "/sessions":
            self.handleSessionCreate()
        else:
            self.handleNotFound()

    def do_OPTIONS(self):
            self.loadSessionData()
            #load session data anytime you might have a request
            self.send_response(200)
            self.send_header("Access-Control-Allow-Methods", "POST,OPTIONS,GET,PUT,DELETE")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

    def do_DELETE(self):
            self.loadSessionData()
            #load session data anytime you might have a request
            path_parts = self.path.split("/")
            resource = path_parts[1]
            if len(path_parts) > 2:
                identifier = path_parts[2]
            else:
                identifier = None

            if resource =="sleeplogs" and identifier != None:
                self.handleLogDeleteMember(identifier)
            else:
                self.handleNotFound()

    def do_PUT(self):
            self.loadSessionData()
            #load session data anytime you might have a request
            path_parts = self.path.split("/")
            resource = path_parts[1]
            if len(path_parts) > 2:
                identifier = path_parts[2]
            else:
                identifier = None

            if resource =="sleeplogs" and identifier != None:
                #db = SleepLogDB()
                self.handleLogUpdateMember(identifier)
                #self.handleLogCreate()
            else:
                self.handleNotFound()


def run():
    listen = ("127.0.0.1",8080)
    server = HTTPServer(listen, MyRequestHandler)
    print("Listening...")
    server.serve_forever()

run()

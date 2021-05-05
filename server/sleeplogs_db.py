import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class SleepLogDB:
    def __init__(self):
        self.connnection = sqlite3.connect("sleeplogs.db")
        self.connnection.row_factory = dict_factory
        self.cursor = self.connnection.cursor()

    def insertUser(self,fname,lname,email,encrypted_password):
        data = [fname,lname,email,encrypted_password]
        self.cursor.execute("INSERT INTO users (fname,lname,email,usersxyzzy) VALUES (?,?,?,?)", data)
        self.connnection.commit()

    def checkUserByEmail(self, email):
        data = [email]
        self.cursor.execute("SELECT * FROM users WHERE email = ?", data)
        return self.cursor.fetchone()

    def insertSleepLog(self,day,hours,phone,late,mood):
        data = [day,hours,phone,late,mood]
        self.cursor.execute("INSERT INTO logs (day, hours, phone, late, mood) VALUES (?,?,?,?,?)", data)
        self.connnection.commit()

    def getAllSleeplogs(self):
        self.cursor.execute("SELECT * FROM logs")
        sleeplogs = self.cursor.fetchall()
        return sleeplogs

    def getOneSleeplog(self, log_id):
        data = [log_id]
        self.cursor.execute("SELECT * FROM logs WHERE id = ?", data)
        return self.cursor.fetchone()

    def deleteSleepLog(self, log_id):
        data = [log_id]
        self.cursor.execute("DELETE from logs WHERE id = ?", data)
        self.connnection.commit()

    def updateSleepLog(self,day,hours,phone,late,mood,log_id):
        data = [day, hours, phone, late, mood, log_id]
        self.cursor.execute("UPDATE logs SET day = ?, hours = ?, phone = ?, late = ?, mood = ? WHERE id = ?", data)
        self.connnection.commit()

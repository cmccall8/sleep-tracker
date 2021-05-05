# Resourceful Project
### Sleep Logs
Attributes:
* Day (string)
* Hours (string)
* Phone (string)
* Late (string)
* Mood (string)

### Schema
```
  CREATE TABLE logs (
      id INTEGER PRIMARY KEY,
      day TEXT,
      hours TEXT,
      phone TEXT,
      late TEXT,
      mood TEXT);
```

### REST Endpoints
Name | Method | Path
---- | ------ | -----
Retrieve Collection | GET | /sleeplogs
Retrieve Member | GET | /sleeplogs/id
Log Create | POST | /sleeplogs
Log Delete Member | DELETE | /sleeplogs/id
Log Update Member | PUT | /sleeplogs/id

### Users
Attributes:
* First Name (string)
* Last Name (string)
* Email (string)
* Password (string)

### Schema
```
  CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    fname TEXT,
    lname TEXT,
    email TEXT,
    password TEXT);
```

### REST Endpoints
Name | Method | Path
---- | ------ | -----
Users Create | POST | /users
Session Create | POST | /sessions

### Password Hashing
* passlib.hash
* bcrypt

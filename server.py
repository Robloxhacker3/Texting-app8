from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from firebase_admin import firestore, credentials, initialize_app
import uvicorn

# Initialize Firebase
cred = credentials.Certificate("firebase-key.json")
initialize_app(cred)
db = firestore.client()

app = FastAPI()

# User Model
class User(BaseModel):
    username: str
    password: str

# Message Model
class Message(BaseModel):
    sender: str
    receiver: str
    content: str

# Signup
@app.post("/signup")
def signup(user: User):
    users_ref = db.collection("users").where("username", "==", user.username).get()
    if users_ref:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db.collection("users").document(user.username).set({"password": user.password})
    return {"message": "User created"}

# Login
@app.post("/login")
def login(user: User):
    users_ref = db.collection("users").document(user.username).get()
    if not users_ref.exists or users_ref.to_dict()["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful"}

# Send Message
@app.post("/send")
def send_message(msg: Message):
    db.collection("messages").add(msg.dict())
    return {"message": "Message sent"}

# Get Messages
@app.get("/messages/{username}")
def get_messages(username: str):
    messages = db.collection("messages").where("receiver", "==", username).stream()
    return [{"sender": msg.get("sender"), "content": msg.get("content")} for msg in messages]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

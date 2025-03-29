from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from firebase_admin import firestore, credentials, initialize_app
import uvicorn

# Initialize Firebase
cred = credentials.Certificate("firebase-key.json")
initialize_app(cred)
db = firestore.client()

app = FastAPI()

# Models
class User(BaseModel):
    username: str
    password: str

class FriendRequest(BaseModel):
    sender: str
    receiver: str

class Message(BaseModel):
    sender: str
    receiver: str
    content: str

# Signup
@app.post("/signup")
def signup(user: User):
    users_ref = db.collection("users").document(user.username).get()
    if users_ref.exists:
        raise HTTPException(status_code=400, detail="Username already exists")

    db.collection("users").document(user.username).set({"password": user.password, "friends": []})
    return {"message": "User created"}

# Login
@app.post("/login")
def login(user: User):
    user_doc = db.collection("users").document(user.username).get()
    if not user_doc.exists or user_doc.to_dict()["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful"}

# Send Friend Request
@app.post("/add-friend")
def add_friend(request: FriendRequest):
    db.collection("friend_requests").add(request.dict())
    return {"message": "Friend request sent"}

# Get Friend Requests
@app.get("/friend-requests/{username}")
def get_friend_requests(username: str):
    requests = db.collection("friend_requests").where("receiver", "==", username).stream()
    return [{"id": req.id, "sender": req.get("sender")} for req in requests]

# Accept Friend Request
@app.post("/accept-friend/{request_id}")
def accept_friend(request_id: str):
    friend_req = db.collection("friend_requests").document(request_id).get()
    if not friend_req.exists:
        raise HTTPException(status_code=404, detail="Friend request not found")

    sender = friend_req.get("sender")
    receiver = friend_req.get("receiver")

    sender_doc = db.collection("users").document(sender)
    receiver_doc = db.collection("users").document(receiver)

    sender_data = sender_doc.get().to_dict()
    receiver_data = receiver_doc.get().to_dict()

    sender_friends = sender_data["friends"]
    receiver_friends = receiver_data["friends"]

    sender_friends.append(receiver)
    receiver_friends.append(sender)

    sender_doc.update({"friends": sender_friends})
    receiver_doc.update({"friends": receiver_friends})

    db.collection("friend_requests").document(request_id).delete()

    return {"message": "Friend request accepted"}

# Send Message
@app.post("/send")
def send_message(msg: Message):
    db.collection("messages").add(msg.dict())
    return {"message": "Message sent"}

# Get Messages
@app.get("/messages/{username}/{friend}")
def get_messages(username: str, friend: str):
    messages = db.collection("messages").where("receiver", "==", username).where("sender", "==", friend).stream()
    messages += db.collection("messages").where("receiver", "==", friend).where("sender", "==", username).stream()
    
    return [{"sender": msg.get("sender"), "content": msg.get("content")} for msg in messages]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

from dataclasses import dataclass, field
from uuid import uuid4
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import random

app = FastAPI()

@dataclass(slots=True)
class ChatRoom:
    name: str
    subscribers: Dict[str, WebSocket] = field(default_factory=dict)  # username -> websocket

    async def subscribe(self, username: str, ws: WebSocket) -> None:
        await ws.accept()
        self.subscribers[username] = ws
        await self.broadcast(f"System :: {username} joined the chat")

    async def unsubscribe(self, username: str) -> None:
        if username in self.subscribers:
            del self.subscribers[username]
            await self.broadcast(f"System :: {username} left the chat")

    async def broadcast(self, message: str) -> None:
        disconnected_users = []
        for username, ws in self.subscribers.items():
            try:
                await ws.send_text(message)
            except:
                disconnected_users.append(username)
        
        # Cleanup disconnected users
        for username in disconnected_users:
            await self.unsubscribe(username)

@dataclass(slots=True)
class ChatManager:
    rooms: Dict[str, ChatRoom] = field(default_factory=dict)

    def get_or_create_room(self, room_name: str) -> ChatRoom:
        if room_name not in self.rooms:
            self.rooms[room_name] = ChatRoom(name=room_name)
        return self.rooms[room_name]

chat_manager = ChatManager()

def generate_username() -> str:
    adjectives = ["Happy", "Clever", "Brave", "Gentle", "Swift", "Wise", "Kind", "Bright"]
    nouns = ["Panda", "Fox", "Eagle", "Dolphin", "Tiger", "Wolf", "Bear", "Lion"]
    return f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(1, 999)}"

@app.websocket("/chat/{chat_name}")
async def ws_chat(ws: WebSocket, chat_name: str):
    username = generate_username()
    room = chat_manager.get_or_create_room(chat_name)
    
    await room.subscribe(username, ws)
    
    try:
        while True:
            message = await ws.receive_text()
            await room.broadcast(f"{username} :: {message}")
    except WebSocketDisconnect:
        await room.unsubscribe(username)

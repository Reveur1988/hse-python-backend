from websocket import create_connection
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python client.py <chat_room_name>")
        return

    chat_room = sys.argv[1]
    ws = create_connection(f"ws://localhost:8000/chat/{chat_room}")
    
    # Start receiving messages in the background
    from threading import Thread
    def receive_messages():
        while True:
            try:
                message = ws.recv()
                print(message)
            except:
                print("Connection closed")
                break
    
    Thread(target=receive_messages, daemon=True).start()
    
    # Send messages from input
    try:
        while True:
            message = input()
            ws.send(message)
    except KeyboardInterrupt:
        ws.close()
        print("\nDisconnected from chat")

if __name__ == "__main__":
    main()
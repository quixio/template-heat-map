import asyncio
import websockets
from websockets.exceptions import ConnectionClosedError
import os
from quixstreams import Application
from dotenv import load_dotenv
import uuid
import json
load_dotenv()

class webSocketSource:
    
    def __init__(self) -> None:
        app = Application.Quix("heatmap-web-sockets-v1", auto_offset_reset="earliest")
        self._topic = app.topic(name=os.environ["input"])
        
        self._consumer = app.get_consumer()
        self._consumer.subscribe([self._topic.name])
        
        # Holds all client connections partitioned by page.
        self.websocket_connections = {}
        
        # Instead of directly creating a task in the constructor, 
        # we'll start the task from outside to avoid issues with incomplete initialization.
        
    async def consume_messages(self):
        while True:
            message = self._consumer.poll(1)
            
            if message is not None:
                value = json.loads(bytes.decode(message.value()))
                key = bytes.decode(message.key())
                
                if key in self.websocket_connections:
                    for client in self.websocket_connections[key]:
                        try:
                            await client.send(json.dumps(value))
                        except:
                            print("Connection already closed.")
                    
                    print(value)
                    print(f"Send to {key} {str(len(self.websocket_connections[key]))} times.")
            else:
                await asyncio.sleep(1)
                
            
    async def handle_websocket(self, websocket, path):
        print(f"Client connected to socket. Path={path}")
        
        if path not in self.websocket_connections:
            self.websocket_connections[path] = []

        self.websocket_connections[path].append(websocket)

        try:
            print("Keep the connection open and wait for messages if needed")
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosedOK:
            print(f"Client {path} disconnected normally.")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Client {path} disconnected with error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            print("Removing client from connection list")
            if path in self.websocket_connections:
                self.websocket_connections[path].remove(websocket)  # Use `del` to remove items from a dictionary

    async def start_websocket_server(self):
        print("listening for websocket connections..")
        server = await websockets.serve(self.handle_websocket, '0.0.0.0', 80)
        await server.wait_closed()

async def main():
    client = webSocketSource()
    # Start consuming messages as a separate task
    asyncio.create_task(client.consume_messages())
    await client.start_websocket_server()

# Run the application with exception handling
try:
    asyncio.run(main())
except Exception as e:
    print(f"An error occurred: {e}")

#!/usr/bin/env python3
"""
Simple WebSocket test client for the queue system
Run this after starting the Django server with WebSocket support
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Test WebSocket connection to the queue system"""
    
    # Connect to the WebSocket endpoint
    uri = "ws://localhost:8000/ws/queue/1/"  # Assuming hospital ID 1
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            
            # Request queue status
            await websocket.send(json.dumps({
                "type": "get_queue_status"
            }))
            print("Sent: get_queue_status request")
            
            # Listen for responses
            async for message in websocket:
                data = json.loads(message)
                print(f"Received: {data}")
                
                # Break after receiving queue status
                if data.get('type') == 'queue_status':
                    break
                    
    except websockets.exceptions.ConnectionRefused:
        print("Connection refused. Make sure:")
        print("1. Django server is running with ASGI support")
        print("2. Redis server is running")
        print("3. WebSocket routing is properly configured")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing WebSocket connection to queue system...")
    print("Make sure Django server is running with: python manage.py runserver")
    print("And Redis server is running")
    print("-" * 50)
    
    asyncio.run(test_websocket())

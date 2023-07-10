from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from manager import *
from methods import *

import hashlib
import time


app = FastAPI()

manage = ConnectionManager()

@app.get("/")
async def root():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <style type="text/css">
        </style>
        
        <title> Hello, World! </title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script type="text/javascript">
            const client_id = Date.now();
            var ws = new WebSocket(`wss://multilevel-parking.onrender.com/${ client_id }`);
            
            ws.onmessage = function(event) {
                p = document.getElementById("message");
                
                p.innerHTML = event.data;
            };
            
            function getMessage(event) {
                let input = 'CHECK 1';
                
                ws.send(input);
            }
            
            function parkCar(event) {
                let input = 'PARK ABC 1 2';
                ws.send(input);
            }
            
            function leave(event) {
                let token = document.getElementById('token').value;
                let input = `LEAVE ${ token }`;
                
                ws.send(input);
            }
        </script>
    </head>
    <body>
        <h1>Hello, World!</h1>
        <p>Hello, this is Soham Patil</p>
        <input type="text" id="token">
        <button onclick=getMessage(event)>Check</button>
        
        <button onclick=parkCar(event)>Park</button>
        
        <button onclick=leave(event)>Leave</button>
        <p id="message"></p>
        <p id="parkCar"></p>
    </body>
    """
    return HTMLResponse(content = html, status_code = 200)

@app.websocket("/ws/{client_id}")
async def endpoint(websocket: WebSocket, client_id: int):
    await manage.connect(websocket)
    
    try:   
        while True:
            request = await websocket.receive_text()
            
            if request.startswith('CHECK'):
                    _, preferred_floor = request.split()
                    available_slot = check_availability(preferred_floor)

                    if available_slot is None:
                        # Find the nearest floor with available slots
                        for floor in parking_lot.keys():
                            available_slot = check_availability(floor)
                            if available_slot:
                                break

                    response = f'FLOOR { preferred_floor }: SLOT { available_slot } AVAILABLE'
                    await manage.send_personal_message(response, websocket)
            elif request.startswith('PARK'):
                _, car_number, floor, slot = request.split()
                if parking_lot[floor][slot] is None:
                    entry_time = int(time.time())
                    token = generate_token(entry_time)
                    parking_lot[floor][slot] = {
                        'car_number': car_number,
                        'entry_time': entry_time,
                        'token': token
                    }
                    response = f'CAR { car_number } PARKED. TOKEN: {token}'
                else:
                    response = f'THE SLOT { slot } IS FULL'
                await manage.send_personal_message(response, websocket)
            elif request.startswith('LEAVE'):
                _, token = request.split()
                exit_time = int(time.time())
                t_floor = None
                t_slot = None
                car_number = None
                bill = 0
                print(parking_lot)

                # Find the car details using the token
                for floor, slots in parking_lot.items():
                    for slot, car in slots.items():
                        if car and car['token'] == token:
                            car_number = car['car_number']
                            entry_time = car['entry_time']
                            bill = calculate_bill(entry_time, exit_time)
                            parking_lot[floor][slot] = None
                            t_floor = floor
                            t_slot = slot
                            break

                if car_number is not None:
                    response = f'CAR { car_number } LEFT. BILL: { bill } Rs'
                else:
                    response = f'The token number { token } is invalid'
                await manage.send_personal_message(response, websocket)
    except WebSocketDisconnect:
        manage.disconnect(websocket)
        await manage.broadcast(f"Client disconnected!")
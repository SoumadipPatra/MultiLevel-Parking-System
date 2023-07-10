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
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MULTILEVEL PARKING SYSTEM</title>
    <link
      rel="stylesheet"
      href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
    />
    <style>
      .container {
        max-width: 960px;
        margin: 0 auto;
        padding: 20px;
      }

      .flex-container {
        display: flex;
        justify-content: center;
        align-items: center;
      }

      .box {
        flex: 1;
        padding: 5px;
        margin: 3px;
        background-color: rgba(224, 224, 255, 0.5);
        height: 16rem;
        padding: 3rem;
        border
      }

      .box-title {
        text-align: center;
      }

      .form-group {
        margin-bottom: 5px;
      }
      body {
        background-image: url("https://media.istockphoto.com/id/1186972461/photo/generic-white-car-isolated-on-white-background.webp?b=1&s=170667a&w=0&k=20&c=VWXOQDLvEJHhCihgNnErADBLaG7vpHPM7pryTquiLi8=");
        background-repeat: no-repeat;
        background-size: 100%;
      }
      
       #myButton {
    padding: 10px 20px;
    background-color: rgb(5, 132, 243);
    color: white;
    border: none;
    cursor: pointer;
    display: block;
    margin: 0 auto;
    border-radius: 5px;
    margin-top: 290px;
  }
  
  #myButton:hover {
    background-color:rgb(103, 182, 251);
  }
  .team-container {
    margin-top: 10px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
  }
  
  .team-member {
    text-align: center;
  }
  
  .team-member img {
    width: 100%;
    max-width: 200px;
    height: auto;
  }
  
  .team-member h3 {
    margin-top: 10px;
  }
  
  .Aradhya {
      margin-top: 12rem;
      padding: 4rem;
      text-align: center;
  }
  
    </style>
    <script>
        const client_id = Date.now();
        var ws = new WebSocket(`wss://multilevel-parking.onrender.com/ws/${ client_id }`);

        ws.onmessage = function(event) {
            let response = event.data;
            
            console.log(response);

            responseList = response.split(' ');
            
            console.log(responseList);

            if(responseList[0] === 'CHECK') {
                const resultDiv = document.getElementById("result");

                resultDiv.innerHTML = `
                 <ul>
                    <li>Available Floor: ${ responseList[1] }</li>
                    <li>Available Slot: ${ responseList[2] }</li>
                 </ul>
                 <button class="btn btn-primary btn-block" onclick="showAlert()">Park</button>
                `
            } else if (responseList[0] === 'PARK') {
                alert(`The car ${ responseList[1] } is parked and token is ${ responseList[2] }`);
            } else if (responseList[0] === 'FULL') {
                alert(`The slot is full!`);
            } else if (responseList[0] === 'LEAVE') {
                const priceResultDiv = document.getElementById("priceResult");

                priceResultDiv.innerHTML = `The car ${ responseList[1] } is leaving, total bill is Rs. ${ responseList[2] }`;
            } else if (responseList[0] === 'INVALID') {
                const priceResultDiv = document.getElementById("priceResult");

                priceResultDiv.innerHTML = `The token is invalid!`;
            }
        }


        function showTokenNumber() {
            const floorNo = document.getElementById("floorNo").value;
            
            console.log('Called!')

            ws.send(`CHECK ${ floorNo }`);
        }

        function showAlert() {
            var car_number = prompt('Enter the car number!');
            var floor_number = prompt('Enter the floor number!');
            var slot_number = prompt('Enter the slot number!');

            ws.send(`PARK ${ car_number } ${ floor_number } ${ slot_number }`);
        }

        function calculatePrice() {
            const tokenNo = document.getElementById("tokenNo").value;

            ws.send(`LEAVE ${ tokenNo }`);
        }
    </script>
  </head>

  <body>
    <div class="container">
      <div class="row">
        <div class="col">
          <img src="data:image/png;base64,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" alt="VIT Logo" width="100" />
        </div>
        <div class="col text-center">
          <h1>MULTILEVEL PARKING SYSTEM</h1>
        </div>
      </div>

      <div class="row flex-container">
        <div class="col-6 box">
          <h3 class="box-title">Check</h3>
          <div class="form-group">
            <label for="floorNo">Floor no.</label>
            <input type="text" id="floorNo" class="form-control" />
          </div>
          <button class="btn btn-primary btn-block" onclick="showTokenNumber()">
            Submit
          </button>
          <br /><br />
          <div id="result"></div>
        </div>

        <div class="col-6 box">
          <h3 class="box-title">Leave</h3>
          <div class="form-group">
            <label for="tokenNo">Token no.</label>
            <input type="text" id="tokenNo" class="form-control" />
          </div>
          <button class="btn btn-primary btn-block" onclick="calculatePrice()">
            Submit
          </button>
          <br /><br />
          <div id="priceResult"></div>
        </div>
      </div>
    </div>
    <div class ="Aradhya">
         <div id="myButton">
    <button onclick="scrollToSection('#about')" class="btn btn-light">About Us</button>
  </div>
  <br>
  <div  id="about">
    <h2 style="text-align: center; color: rgb(5, 132, 243);"> THE TEAM</h2>
    <div class="team-container">
      <div class="team-member">
        <h3>Soham Lalitkumar Patil</h3>
        <h4>21BIT0519</h4>
      </div>
      <div class="team-member">
        <h3>Saksham Garg</h3>
        <h4>21BIT0272</h4>
      </div>
      <div class="team-member">
        <h3>Aradhya Sehgal</h3>
        <h4>21BIT0188</h4>
      </div>
      <div class="team-member">
        <h3>Soumadip Patra</h3>
        <h4>21BIT0523</h4>
      </div>
      <div class="team-member">
        <h3>Sidharth Ghai</h3>
        <h4>21BIT0527</h4>
      </div>
    </div>
</div>
    <div>
        <h2 style="text-align: center; color: rgb(5, 132, 243);"> PRODUCT DESCRIPTION</h2>
        <br>
        <div style="text-align: center;">This System allows both management and customers to enjoy <span style="color: cornflowerblue;">seamless parking management</span>.</div>
        <br>
At the entrance and exit of the operation site, <span style="color: cornflowerblue;">the client systems</span> would be ready to serve. Trained employees will handle the client systems, <span style="color: cornflowerblue;">generating requests to check for space availability on specific floors.</span> 
<br>
Our server systems, configured by management, will swiftly process these requests, providing an immediate acknowledgement with the available spots. 
<br>
Once an available spot is confirmed, our system will <span style="color: cornflowerblue;">generate a unique token number</span> in reference to your vehicle. This token acts as your personal identifier. As you enter, the token ensures your designated spot remains reserved, <span style="color: cornflowerblue;">eliminating the tedious and non-practical task</span> of finding a place to park. 
<br>
When it’s time for you to leave, simple present your token number at the exit. Our server system instantly retrieves the information, generating your bill according to the configurable policies set by the management. 
<br>
Whether it's hourly rates, flat fees, or any other billing policy, our system adapts to meet your specific needs, and logging the necessary details. 
<br>
This ensures that you don’t have to wait in long queues or struggle with paper receipts. <span style="color: cornflowerblue;">This technology will streamline the entire process, allowing a quick and hassle-free exit. </span>
      </div>
      <div>
        <br>
        <h2 style="text-align: center; color: rgb(5, 132, 243);"> ACKNOWLEDGEMENT</h2>
        <p>We would like to express our deepest gratitude to Professor <span style="color: cornflowerblue;">Dr. P. Shunmuga Perumal</span> for their invaluable guidance, mentorship, and unwavering support throughout this project. 
            <br>
            Their expertise, knowledge, and dedication have been instrumental in shaping our understanding and pushing us to achieve our best. We are incredibly fortunate to have had the opportunity to learn from and work alongside such an exceptional educator.</p>
      </div>
    </div>
  </body>
</html>

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

                    response = f'CHECK { preferred_floor } { available_slot }'
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
                    response = f'PARK { car_number } {token}'
                else:
                    response = f'FULL'
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
                    response = f'LEAVE { car_number } { bill }'
                else:
                    response = f'INVALID { token }'
                await manage.send_personal_message(response, websocket)
    except WebSocketDisconnect:
        manage.disconnect(websocket)
        await manage.broadcast(f"Client disconnected!")
        
@app.get('/vitv.png')
async def vitlogo():
    return 
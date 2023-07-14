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
    <title>MULTILEVEL PARKING SYSTEM - Parking</title>
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
            height: 24rem;
            padding: 3rem;
            border: 0;
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
              var log = [];
              const maxLen = 5;

            function add(x) {
            log.push(x);

            if(log.length > maxLen) {
              log.shift();
            }
          }

              ws.onmessage = function(event) {
                  let response = event.data;

                  console.log(response);

                  responseList = response.split(' ');

                  console.log(responseList);

                  if(responseList[0] === 'CHECK') {
                      const resultDiv = document.getElementById("result");

                      console.log(resultDiv);

                      const carNumber = document.getElementById("carNumber");
                      const parkingFloor = document.getElementById("parkingFloor");
                      const parkingSlot = document.getElementById("parkingSlot");

                      carNumber.value = "";
                      parkingFloor.value = responseList[1];
                      parkingSlot.value = responseList[2];
                  } else if (responseList[0] === 'PARK') {
                      alert(`The car ${ responseList[1] } is parked and token is ${ responseList[2] }`);
                  } else if (responseList[0] === 'FULL') {
                      alert(`The slot is full!`);
                  } else if (responseList[0] === 'LEAVE') {
                      const priceResultDiv = document.getElementById("priceResult");

                      priceResultDiv.innerHTML = `<b>The car ${ responseList[1] } is leaving, total bill is Rs. ${ responseList[2] }</b>`;
                  } else if (responseList[0] === 'INVALID') {
                      const priceResultDiv = document.getElementById("priceResult");

                      priceResultDiv.innerHTML = `The token is invalid!`;
                  } else if (responseList[0] === 'ENTRY') {
                const tbody = document.getElementById("tabbody");
                tbody.innerHTML = ""

                let log_entry = {
                  'type': 0,
                  'car_number': responseList[1],
                  'token': responseList[2],
                  'floor': responseList[3],
                  'slot': responseList[4],
                  'time': new Date(parseInt(responseList[5]) * 1000)
                }

                add(log_entry)

                for(let i = log.length - 1; i >= 0; i--) {
                  let bgClass = "table-success";
                  if(log[i]['type'] === 1) {
                    bgClass = "table-warning";
                  }
                  tbody.innerHTML += `<tr class="${ bgClass }">
                    <td>${ log[i]['car_number'] }</td>
                    <td>${ log[i]['token'] }</td>
                    <td>${ log[i]['floor'] }</td>
                    <td>${ log[i]['slot'] }</td>
                    <td>${ log[i]['time'].getHours() }:${ log[i]['time'].getMinutes()}:${ log[i]['time'].getSeconds() }</td>
                  </tr>`
                }
              } else if (responseList[0] === 'EXIT') {
                const tbody = document.getElementById("tabbody");
                tbody.innerHTML = ""

                let log_entry = {
                  'type': 1,
                  'car_number': responseList[1],
                  'token': responseList[2],
                  'floor': responseList[3],
                  'slot': responseList[4],
                  'time': new Date(parseInt(responseList[5]) * 1000)
                }

                add(log_entry)

                for(let i = log.length - 1; i >= 0; i--) {
                  let bgClass = "table-success";
                  if(log[i]['type'] === 1) {
                    bgClass = "table-warning";
                  }
                  tbody.innerHTML += `<tr class="${ bgClass }">
                    <td>${ log[i]['car_number'] }</td>
                    <td>${ log[i]['token'] }</td>
                    <td>${ log[i]['floor'] }</td>
                    <td>${ log[i]['slot'] }</td>
                    <td>${ log[i]['time'].getHours() }:${ log[i]['time'].getMinutes() }:${ log[i]['time'].getSeconds() }</td>
                  </tr>`
                }
              }
              }

              function calculatePrice() {
                  const tokenNo = document.getElementById("tokenNo").value;

                  if(!tokenNo) {
                    alert('Please enter a token number');
                    return;
                  }

                  ws.send(`LEAVE ${ tokenNo }`);
              }

              function scrollToSection(sectionId) {
                const section = document.querySelector(sectionId);
                if (section) {
                  section.scrollIntoView({ behavior: 'smooth' });
                }
              }

          function showTokenNumber() {
            const floorNo = document.getElementById("floorNo").value;

            console.log('Called!')

            if (!floorNo) {
              alert('Please enter a valid floor number');
              return;
            }
            const parkForm = document.getElementById("parkForm");

            ws.send(`CHECK ${floorNo}`);
            parkForm.style.display = "block";
          }

          function showAlert() {
            var car_number = document.getElementById('carNumber').value;
            var floor_number = document.getElementById('parkingFloor').value;
            var slot_number = document.getElementById('parkingSlot').value;
            const parkForm = document.getElementById("parkForm");

            ws.send(`PARK ${car_number} ${floor_number} ${slot_number}`);
            parkForm.style.display = "none";
          }
    </script>
  </head>
  <body>
    <div class="container">
      <div class="row">
        <div class="col-3">
          <img
            src="https://upload.wikimedia.org/wikipedia/en/thumb/c/c5/Vellore_Institute_of_Technology_seal_2017.svg/1200px-Vellore_Institute_of_Technology_seal_2017.svg.png"
            alt="VIT Logo"
            width="100"
          />
        </div>
        <div class="col-9">
          <h1>MULTILEVEL PARKING SYSTEM</h1>
          <button
            onclick="scrollToSection('#about')"
            class="btn btn-primary"
            style="margin-left: 65%"
          >
            About Us
          </button>
        </div>
      </div>
      <div class="row flex-container mt-5">
        <div class="col-6 box">
          <h3 class="box-title">Check</h3>
          <div class="form-group">
            <label for="floorNo">Floor number</label>
            <input type="text" id="floorNo" class="form-control" />
          </div>
          <button class="btn btn-primary btn-block" onclick="showTokenNumber()">
            Submit
          </button>
          <br /><br />
          <div id="result"></div>
        </div>

        <div class="col-6 box" id="parkForm" style="display: none">
          <h3 class="box-title">Park</h3>
          <div class="form-group">
            <label for="carNumber">Car number</label>
            <input type="text" id="carNumber" class="form-control" />
          </div>
          <div class="form-group">
            <label for="parkingFloor">Floor number</label>
            <input type="text" id="parkingFloor" class="form-control" />
          </div>
          <div class="form-group">
            <label for="parkingSlot">Slot number</label>
            <input type="text" id="parkingSlot" class="form-control" />
          </div>
          <button class="btn btn-primary btn-block" onclick="showAlert()">
            Submit
          </button>
          <br /><br />
          <div id="parkingResult"></div>
        </div>
      </div>
      <div class="row">
        <table class="table">
          <thead>
            <tr class="bg-primary">
              <th scope="col">Car Number</th>
              <th scope="col">Token</th>
              <th scope="col">Floor</th>
              <th scope="col">Slot</th>
              <th scope="col">Time</th>
            </tr>
          </thead>
          <tbody id="tabbody"></tbody>
        </table>
      </div>
    </div>
    <div class="Aradhya">
      <br />
      <div id="about">
        <h2 style="text-align: center; color: rgb(5, 132, 243)">THE TEAM</h2>
        <div class="team-container">
          <div class="team-member">
            <img
              src="https://i1.rgstatic.net/ii/profile.image/11431281173839150-1689066070843_Q128/Soham-Patil-12.jpg"
              alt="Sid"
              style="width: 8rem; height: 8rem"
            />
            <h3>Soham Lalitkumar Patil</h3>
            <h4>21BIT0519</h4>
          </div>
          <div class="team-member">
            <img
              src="https://i1.rgstatic.net/ii/profile.image/11431281173868359-1689066377951_Q128/Saksham-Garg-14.jpg"
              alt="Sid"
              style="width: 8rem; height: 8rem"
            />
            <h3>Saksham Garg</h3>
            <h4>21BIT0272</h4>
          </div>
          <div class="team-member">
            <img
              src="https://i1.rgstatic.net/ii/profile.image/11431281173868769-1689067259648_Q128/Aradhya-Sehgal.jpg"
              alt="Sid"
              style="width: 8rem; height: 8rem"
            />
            <h3>Aradhya Sehgal</h3>
            <h4>21BIT0188</h4>
          </div>
          <div class="team-member">
            <img
              src="https://i1.rgstatic.net/ii/profile.image/11431281173839123-1689065978284_Q128/Soumadip-Patra.jpg"
              alt="Sid"
              style="width: 8rem; height: 8rem"
            />
            <h3>Soumadip Patra</h3>
            <h4>21BIT0523</h4>
          </div>
          <div class="team-member">
            <img
              src="https://i1.rgstatic.net/ii/profile.image/11431281173872499-1689051278139_Q128/Sidharth-Ghai.jpg"
              alt="Sid"
              style="width: 8rem; height: 8rem"
            />
            <h3>Sidharth Ghai</h3>
            <h4>21BIT0527</h4>
          </div>
        </div>
      </div>
      <div>
        <h2 style="text-align: center; color: rgb(5, 132, 243)">
          PRODUCT DESCRIPTION
        </h2>
        <br />
        <div style="text-align: center">
          This System allows both management and customers to enjoy
          <span style="color: cornflowerblue">seamless parking management</span
          >.
        </div>
        <br />
        At the entrance and exit of the operation site,
        <span style="color: cornflowerblue">the client systems</span> would be
        ready to serve. Trained employees will handle the client systems,
        <span style="color: cornflowerblue"
          >generating requests to check for space availability on specific
          floors.</span
        >
        <br />
        Our server systems, configured by management, will swiftly process these
        requests, providing an immediate acknowledgement with the available
        spots.
        <br />
        Once an available spot is confirmed, our system will
        <span style="color: cornflowerblue"
          >generate a unique token number</span
        >
        in reference to your vehicle. This token acts as your personal
        identifier. As you enter, the token ensures your designated spot remains
        reserved,
        <span style="color: cornflowerblue"
          >eliminating the tedious and non-practical task</span
        >
        of finding a place to park.
        <br />
        When it’s time for you to leave, simple present your token number at the
        exit. Our server system instantly retrieves the information, generating
        your bill according to the configurable policies set by the management.
        <br />
        Whether it's hourly rates, flat fees, or any other billing policy, our
        system adapts to meet your specific needs, and logging the necessary
        details.
        <br />
        This ensures that you don’t have to wait in long queues or struggle with
        paper receipts.
        <span style="color: cornflowerblue"
          >This technology will streamline the entire process, allowing a quick
          and hassle-free exit.
        </span>
      </div>
      <div>
        <br />
        <h2 style="text-align: center; color: rgb(5, 132, 243)">
          ACKNOWLEDGEMENT
        </h2>
        <p>
          We would like to express our deepest gratitude to Professor
          <span style="color: cornflowerblue">Dr. P. Shunmuga Perumal</span> for
          their invaluable guidance, mentorship, and unwavering support
          throughout this project.
          <br />
          Their expertise, knowledge, and dedication have been instrumental in
          shaping our understanding and pushing us to achieve our best. We are
          incredibly fortunate to have had the opportunity to learn from and
          work alongside such an exceptional educator.
        </p>
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
                    await manage.send_personal_message(f'PARK { car_number } {token}', websocket)
                    await manage.broadcast(f'ENTRY { car_number} { token } { floor } { slot } { entry_time }')
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
                    await manage.send_personal_message(f'LEAVE { car_number } { bill }', websocket)
                    await manage.broadcast(f'EXIT { car_number } { token } { t_floor } { t_slot } { exit_time }')
                else:
                    response = f'INVALID { token }'
                    await manage.send_personal_message(response, websocket)
    except WebSocketDisconnect:
        manage.disconnect(websocket)
        await manage.broadcast(f"Client disconnected!")
        
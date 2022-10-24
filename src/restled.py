import json
import network
import picoweb
import ulogging
from ringlight import RingLamp, RingLampMode
from lamp import Lamp

station = network.WLAN(network.STA_IF)
log = ulogging.getLogger(__name__)
log.setLevel(ulogging.DEBUG)
app = picoweb.WebApp(__name__)

pin1 = 12
pin2 = 13
freq = 5000
lamp = RingLamp(pin1, pin2, freq)


@app.route("/")
def index(req, resp):
    yield from picoweb.start_response(resp)

    html = """
    <html>
	<head>
		<title>ESP Web Server</title>
		<meta name="viewport" content="width=device-width, initial-scale=1">
			<link rel="icon" href="data:,">
				<style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
    h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
    border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
    .button2{background-color: #4286f4;}</style>
			</head>
			<body>
				<h1>ESP Web Server</h1>
				<p>Light state: <strong>""" + lamp.data()["state"] + """</strong></p>
				<p>
					<a href="/toggle">
						<button class="button">toggle</button>
					</a>
				</p>
                <p>Light mode: <strong>""" + lamp.data()["effect"] + """</strong></p>
                <p>
					<a href="/mode?value=1">
						<button class="button">white</button>
					</a>
				</p>
                <p>
					<a href="/mode?value=2">
						<button class="button">yellow</button>
					</a>
				</p>
                <p>
					<a href="/mode?value=3">
						<button class="button">both</button>
					</a>
				</p>   
				<p>Light brightness: <strong>""" + str(lamp.data()["brightness"]) + """</strong></p>
                <p>
                    <form action="/brightness" method="get">
                        Between 0 and 255 <br>
                        <label for="value">Brightness:</label>
                        <input type="number" id="value" name="value">
                        <input type="submit" value="Submit">
                    </form>
				</p>   
			</body>
		</html>
    """
    yield from resp.awrite(html)


@app.route("/status")
def status(req, resp):
    yield from picoweb.start_response(resp)
    yield from resp.awrite(json.dumps(lamp.data()))


@app.route("/toggle")
def toggle(req, resp):
    lamp.toggle()
    return index(req, resp)


@app.route("/brightness")
def setBrightness(req, resp):
    req.parse_qs()
    params = req.form
    log.debug("Params: %s", params)
    value = int(params["value"])
    if 0 <= value <= 255:
        lamp.brightness = int(params["value"])
    return index(req, resp)


@app.route("/mode")
def setMode(req, resp):
    req.parse_qs()
    params = req.form
    log.debug("Params: %s", params)
    value = int(params["value"])
    if 0 <= value <= 3:
        lamp.mode = RingLampMode.fromValue(value)
    return index(req, resp)


def main():
    app.run(debug=True, host=station.ifconfig()[0], port=80)

import machine
import picoweb
import ulogging
import slutils

log = ulogging.getLogger(__name__)
log.setLevel(ulogging.DEBUG)
app = picoweb.WebApp(__name__)


@app.route("/")
def index(req, resp):
    if req.method == "POST":
        yield from req.read_form_data()
    else:
        req.parse_qs()
    yield from picoweb.start_response(resp)

    secrets = slutils.read_secrets()
    wifi_secrets = secrets["wifi"]
    mqtt_secrets = secrets["mqtt"]

    if req.method == "POST":
        form = req.form
        wifi_secrets["ssid"] = form["ssid"]
        wifi_secrets["password"] = form["ssid_password"]
        mqtt_secrets["host"] = form["mqtt_host"]
        mqtt_secrets["port"] = form["mqtt_port"]
        mqtt_secrets["user"] = form["mqtt_user"]
        mqtt_secrets["password"] = form["mqtt_password"]
        slutils.write_secrets(secrets)

    f = open("configure.html", 'r')
    html = f.read()
    f.close()
    html = html.replace("\n", "").replace(
        "\t", "").replace("{", "{{").replace("}", "}}").replace("%s", "{}")
    html = f"{html}".format(
        wifi_secrets["ssid"],
        "" if "password" not in wifi_secrets else wifi_secrets["password"],
        mqtt_secrets["host"],
        mqtt_secrets["port"],
        mqtt_secrets["user"],
        mqtt_secrets["password"],
    )
    yield from resp.awrite(html)

    if req.method == "POST":
        machine.reset()


def start(station):
    app.run(debug=True, host=station.ifconfig()[0], port=80)

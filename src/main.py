import network
import mqttlamp

if network.WLAN(network.AP_IF).active():
    import configure
    configure.start(network.WLAN(network.AP_IF))
else:
    mqttlamp.main()

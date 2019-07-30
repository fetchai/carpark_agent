
try:
    import board
    import adafruit_gps
    import serial

    has_gps = True
except ImportError:
    print("Failed to load Raspberry Pi gps module")
    has_gps = False

if has_gps:
    class GPS:
        def __init__(self):
            self.RX = board.RXD
            self.TX = board.TXD
            uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=3000)
            self.gps = adafruit_gps.GPS(uart, debug=False)
            self.gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
            self.gps.send_command(b'PMTK220,1000')

        def GetValues(self):
            self.gps.update()
            if self.gps.has_fix:
                return self.gps.latitude, self.gps.longitude
            else:
                return None, None
else:
    class GPS:
        def __init__(self):
            pass

        def GetValues(self):
            return None, None

import threading
from collections import namedtuple
import platform

import busio
import digitalio

if platform.system().lower().startswith('win'):
    FAKE_MODE = True
    import math
elif platform.system().lower().startswith('lin'):
    FAKE_MODE = False
    import board
    import adafruit_mcp3xxx.mcp3004 as MCP
    from adafruit_mcp3xxx.analog_in import AnalogIn
import time

##################################################
#  0V    - at 1.75V
#  PITCH - MIN=C0=1.78V, C1=1.67V, C2=1.55V, C3=1.44699V, C4=1.3342, C5=1.2214V, C6=1.1086V, C7=0.9958V, C8=0.8862V
#          MAX=C10=0.6606V
#  CLOCK - KeyStep = 1.78V and 1.41V oscillating
#  GATE  - 0.3706V on hit, 1.78V otherwise
#  MOD   - 1.78V to 1.19V
##################################################
from typing import List


def convert_range(value, oldmin, oldmax, newmin, newmax):
    return (((value - oldmin) * (newmax - newmin)) / (max(oldmax, 0.01) - oldmin)) + newmin


class InputChannel:
    chtype = namedtuple("chtype", ["General", "Pitch", "Clock", "Gate", "Audio"])(0, 1, 2, 3, 4)

    def __init__(self, chtype=0, pin=0):
        self.type = chtype
        self.min_voltage = float("inf")
        self.max_voltage = float("-inf")
        self.last_voltage = 0.0
        self.voltage_lock = threading.Lock()
        self.pin_number = pin

    def get_value(self):
        self.voltage_lock.acquire()
        v = self.last_voltage
        vmin = self.min_voltage
        vmax = self.max_voltage
        self.voltage_lock.release()
        if self.type == InputChannel.chtype.General:
            return 1.0 - convert_range(v, vmin, vmax, 0.0, 1.0)
        elif self.type == InputChannel.chtype.Pitch:
            return 1.0 - convert_range(v, 0.6606, 1.78, 0.0, 1.0)
        elif self.type == InputChannel.chtype.Clock:
            return v < 1.6
        elif self.type == InputChannel.chtype.Gate:
            return v < 1
        elif self.type == InputChannel.chtype.Audio:
            return 0.0  # TODO: Implement


def listener_thread(channels: List[InputChannel]):
    if FAKE_MODE:
        class fake_in:
            def __init__(self, speed=1.0):
                self.speed = speed

            @property
            def voltage(self):
                return fake_in.get_sin(self.speed)

            @staticmethod
            def get_sin(f):
                return math.sin(time.time() * f * 2 * math.pi)

            def readonly_set(self):
                pass

        ins = [fake_in(), fake_in(0.2), fake_in(0.1), fake_in()]
    else:
        spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = digitalio.DigitalInOut(board.D5)
        mcp = MCP.MCP3004(spi, cs)
        ins = [AnalogIn(mcp, ch.pin_number) for ch in channels]
    print(ins)
    print(ins[0].voltage)
    global ANI_STOPPING_THREADS
    while not ANI_STOPPING_THREADS:
        i = 0
        for ch in channels:
            ch.voltage_lock.acquire()
            ch.last_voltage = ins[i].voltage
            if ch.last_voltage > 0:
                ch.min_voltage = min(ch.min_voltage, ch.last_voltage)
            ch.max_voltage = max(ch.max_voltage, ch.last_voltage)
            ch.voltage_lock.release()
            i = i + 1
        time.sleep(0.001)


ANI_STOPPING_THREADS = False


class InputManager:
    def __init__(self, channels=None):
        if channels is None:
            channels = [InputChannel(InputChannel.chtype.General, 0), InputChannel(InputChannel.chtype.General, 1),
                        InputChannel(InputChannel.chtype.General, 2), InputChannel(InputChannel.chtype.General, 3)]
        self.channels = channels
        self.thread = None

    def start(self):
        if not self.thread:
            self.thread = threading.Thread(target=listener_thread, args=(self.channels,))
            self.thread.start()

    def stop(self):
        if self.thread:
            global ANI_STOPPING_THREADS
            ANI_STOPPING_THREADS = True
            self.thread.join()
            self.thread = None
            ANI_STOPPING_THREADS = False

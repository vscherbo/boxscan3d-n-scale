#!/usr/bin/env python3

from gpiodmonitor import gpiodmonitor

def dummy_active(pin: int):
    """Dummy function."""
    print(f'{pin} is active')

def dummy_inactive(pin: int):
    """Dummy function."""
    print(f'{pin} is inactive')

def dummy_pulsed_active(pin: int):
    """Dummy function."""
    print(f'{pin} is still active')

def dummy_long_active(pin: int):
    """Dummy function."""
    print(f'{pin} has been active for a long time')

monitor = gpiodmonitor.GPIODMonitor(chip_number=0)

for gpio_pin in [69]:
#for gpio_pin in [12,13]:
    # register some functions to be called on activity on pins 12 and 13
    monitor.register(int(gpio_pin),
                     on_active=dummy_active,
                     on_inactive=dummy_inactive)
    # register function that will be called every 300 ms as long as the
    # pin is active
    monitor.register_pulsed_active(int(gpio_pin),
                                 callback=dummy_pulsed_active,
                                 seconds=0.3)
    # register a function to be called when the button is pressed for 3
    # seconds
    monitor.register_long_active(int(gpio_pin),
                                 callback=dummy_long_active,
                                 seconds=3)

with monitor.open_chip():
    try:
        while True:
            # check according to interval
            time.sleep(monitor.check_interval / 1000)
            monitor.tick()
    except KeyboardInterrupt:
        sys.exit(130)
    # or use (equivalent but you don't have controll over the loop):
    # chip.monitor()

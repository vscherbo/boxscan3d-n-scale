#!/usr/bin/env python3

from datetime import timedelta
import time
import gpiod
import threading

import log_app

class GPIOEventHandler:
    def __init__(self, chip_name, line_numbers, edge_type, callback):
        """
        Initialize the GPIOEventHandler.

        :param chip_name: The GPIO chip name (e.g., 'gpiochip0').
        :param line_numbers: A list of GPIO line numbers to monitor.
        :param edge_type: The edge type to detect ('rising', 'falling', 'both').
        :param callback: The callback function to execute on edge detection.
        """
        self.chip_name = chip_name
        self.line_numbers = tuple(line_numbers)
        self.edge_type = edge_type
        self.callback = callback
        self.running = True

        # Open the GPIO chip
        self.chip = gpiod.Chip(chip_name)

        # Configure the GPIO lines
        self._configure_lines()

        # Start the event listener in a separate thread
        self.event_thread = threading.Thread(target=self._event_listener)
        self.event_thread.daemon = True
        self.event_thread.start()

    def _configure_lines(self):
        """Configure the GPIO lines for edge detection."""
        # Define edge event type
        if self.edge_type == 'rising':
            event_type = gpiod.line.Edge.RISING
        elif self.edge_type == 'falling':
            event_type = gpiod.line.Edge.FALLING
        elif self.edge_type == 'both':
            event_type = gpiod.line.Edge.BOTH
        else:
            raise ValueError("Invalid edge_type. Use 'rising', 'falling', or 'both'.")

        # Request lines with event detection
        """
        self.lines = self.chip.request_lines({
            "consumer": "gpio-event-handler",
            "lines": self.line_numbers,
            "edge": event_type
        })
        """
        self.request = gpiod.request_lines(self.chip_name, consumer="watch-lines-edge",
                                             config={
                                                 self.line_numbers: gpiod.LineSettings(edge_detection=event_type, debounce_period=timedelta(microseconds=0))
                                                 #tuple(self.line_numbers): gpiod.LineSettings(edge_detection=event_type, debounce_period=timedelta(microseconds=0))
                                                 }
                                             )


    def _event_listener(self):
        """Listen for GPIO edge events."""
        while self.running:
            # Block until an event occurs
            events = self.request.read_edge_events()
            if events:
                for event in events:
                    #self.callback(event.line.offset, event)
                    self.callback(event.line_offset, event)


    def _event_listener_timeout(self):
        """Listen for GPIO edge events."""
        while self.running:
            # Use a timeout to prevent hanging when no events occur
            try:
                events = self.request.read_edge_events(timeout=1.0)  # Set timeout to 1 second
                if events:
                    for event in events:
                        self.callback(event.line_offset, event)
            except gpiod.TimeoutError:
                # No event occurred within the timeout period, continue checking `self.running`
                print('timeout')
                pass

            time.sleep(0.1)  # Sleep for 100ms to avoid high CPU usage


    def start(self):
        """Start the event listener thread."""
        self.running = True
        if not self.event_thread.is_alive():
            #self.event_thread = threading.Thread(target=self._event_listener)
            self.event_thread = threading.Thread(target=self._event_listener_timeout)
            self.event_thread.daemon = True
            self.event_thread.start()

    def stop(self):
        """Stop the event listener thread."""
        self.running = False
        self.event_thread.join()

    def __del__(self):
        """Clean up resources."""
        self.stop()  # Stop the thread if not stopped
        if hasattr(self, 'request'):
            self.request.release()

# Example callback function
def edge_detected(line_offset, event):
    print(f"Edge detected on line {line_offset}! Event: {event.event_type}")

class Ruler3D(log_app.LogApp):
    def __init__(self, args):
        log_app.LogApp.__init__(self, args=args)
        config_filename = args.conf
        self.get_config(config_filename)

        #super().__init__(self.config['PG']['pg_host'], self.config['PG']['pg_user'])
        #if self.pg_connect():
        #    self.set_session(autocommit=True)

        self.timestamp_rising = {}
        self.dist3 = {}

        self.line_def = {}
        self.line_def[int(self.config['length']['line'])] = {
                       'base': float(self.config['length']['base']),
                       'name': self.config['length']['name']
                }
        self.line_def[int(self.config['width']['line'])] = {
                       'base': float(self.config['width']['base']),
                       'name': self.config['width']['name']
                }
        self.line_def[int(self.config['heigth']['line'])] = {
                       'base': float(self.config['heigth']['base']),
                       'name': self.config['heigth']['name']
                }



    def event_handler(self, line_offset, event):
        #print(f"Edge detected on line {line_offset}! Event: {event.event_type}")
        if event.event_type == event.Type.RISING_EDGE:
            #print(f'=== RISING {self.dist3}')
            self.timestamp_rising[event.line_offset] = event.timestamp_ns
            #print(f'=== {self.timestamp_rising}')
            try:
                if len(self.dist3[event.line_offset]) == 2:
                    #print(f' empty {self.dist3[event.line_offset]}')
                    self.dist3[event.line_offset] = []
            except KeyError:
                self.dist3[event.line_offset] = []
                pass

        elif event.event_type == event.Type.FALLING_EDGE:
            #print(f'=== FALL {self.timestamp_rising}')
            try:
                ts_delta = event.timestamp_ns - self.timestamp_rising[event.line_offset]
            except KeyError:
                print(f'NO rising. Skip: {self.dist3}')
            else:
                #print(f'delta={ts_delta}')
                #dist_cm = round(ts_delta/1000/58.8, 1)
                dist_cm = round(ts_delta/1000/57.72, 1)
                #print(f'   {line_def[event.line_offset]["name"]}', f'dist(cm)={dist_cm}')
                print(f'   {event.line_offset}', f'dist(cm)={dist_cm}')
                self.dist3[event.line_offset].append(dist_cm)
                #print(f'=== FALLING {self.dist3}')
                if len(self.dist3[event.line_offset]) == 2:
                    dist_avg = round((self.dist3[event.line_offset][0] + self.dist3[event.line_offset][1])/2.0, 1)
                    self.dist3[event.line_offset] = []
                    #print(f'{line_offset}', f'dist_avg={dist_avg}')
                    size = round(self.line_def[event.line_offset]['base'] - dist_avg, 1)
                    #print(f'{self.line_def[event.line_offset]["name"]}', f'dist_avg={dist_avg}', f'size={size}')
                    logging.debug(f'{self.line_def[event.line_offset]["name"]}, dist_avg={dist_avg}, size={size}')
                    self.timestamp_rising[event.line_offset] = {}



def main():
    """ Just main
    """

# Example usage
if __name__ == "__main__":
    import logging
    #log_app.PARSER.add_argument('--uuid', type=str, help='an order uuid to check status')
    ARGS = log_app.PARSER.parse_args()
    ruler3d = Ruler3D(args=ARGS)    
    if ruler3d:
        logging.debug(ruler3d.line_def)
        handler = GPIOEventHandler(chip_name="/dev/gpiochip0", line_numbers=[69, 75, 79], edge_type="both", callback=ruler3d.event_handler)

        try:
            while True:
                pass  # Keep the program running
                time.sleep(1)
                #print('loop')
        except KeyboardInterrupt:
            print('\ncaught keyboard interrupt!')
            handler.stop()
            print("Program terminated")


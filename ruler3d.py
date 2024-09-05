#!/usr/bin/env python3

from datetime import timedelta

import gpiod
import threading

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

    def start(self):
        """Start the event listener thread."""
        self.running = True
        if not self.event_thread.is_alive():
            self.event_thread = threading.Thread(target=self._event_listener)
            self.event_thread.daemon = True
            self.event_thread.start()

    def stop(self):
        """Stop the event listener thread."""
        self.running = False
        self.event_thread.join()

    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'lines'):
            self.request.release()

# Example callback function
def edge_detected(line_offset, event):
    print(f"Edge detected on line {line_offset}! Event: {event.event_type}")


# Example usage
if __name__ == "__main__":
    handler = GPIOEventHandler(chip_name="/dev/gpiochip0", line_numbers=[69, 75, 79], edge_type="both", callback=edge_detected)

    try:
        while True:
            pass  # Keep the program running
    except KeyboardInterrupt:
        handler.stop()
        print("Program terminated")


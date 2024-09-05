#!/usr/bin/env python3

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
        self.line_numbers = line_numbers
        self.edge_type = edge_type
        self.callback = callback

        self.chip = gpiod.Chip(chip_name)
        self.lines = [self.chip.get_line(line_number) for line_number in line_numbers]

        self.event_thread = threading.Thread(target=self._event_listener)
        self.event_thread.daemon = True
        self.running = True

        self._configure_lines()

    def _configure_lines(self):
        """Configure the GPIO lines for edge detection."""
        config = gpiod.line_request()
        config.consumer = "gpio-event-handler"
        if self.edge_type == 'rising':
            config.request_type = gpiod.line_request.EVENT_RISING_EDGE
        elif self.edge_type == 'falling':
            config.request_type = gpiod.line_request.EVENT_FALLING_EDGE
        elif self.edge_type == 'both':
            config.request_type = gpiod.line_request.EVENT_BOTH_EDGES
        else:
            raise ValueError("Invalid edge_type. Use 'rising', 'falling', or 'both'.")

        for line in self.lines:
            line.request(config)

    def _event_listener(self):
        """Listen for GPIO edge events."""
        while self.running:
            for line in self.lines:
                event = line.event_wait(sec=1)
                if event:
                    event = line.event_read()
                    self.callback(line, event)

    def start(self):
        """Start the event listener thread."""
        self.event_thread.start()

    def stop(self):
        """Stop the event listener thread."""
        self.running = False
        self.event_thread.join()

    def __del__(self):
        """Clean up resources."""
        for line in self.lines:
            line.release()

# Example callback function
def edge_detected(line, event):
    print(f"Edge detected on line {line.offset}! Event: {event}")

# Example usage
if __name__ == "__main__":
    handler = GPIOEventHandler(chip_name="/dev/gpiochip0", line_numbers=[73, 228, 229], edge_type="both", callback=edge_detected)
    handler.start()

    try:
        while True:
            pass  # Keep the program running
    except KeyboardInterrupt:
        handler.stop()
        print("Program terminated")


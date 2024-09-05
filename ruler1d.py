import gpiod
import threading

class GPIOEventHandler:
    def __init__(self, chip_name, line_number, edge_type, callback):
        """
        Initialize the GPIOEventHandler.

        :param chip_name: The GPIO chip name (e.g., 'gpiochip0').
        :param line_number: The GPIO line number to monitor.
        :param edge_type: The edge type to detect ('rising', 'falling', 'both').
        :param callback: The callback function to execute on edge detection.
        """
        self.chip_name = chip_name
        self.line_number = line_number
        self.edge_type = edge_type
        self.callback = callback

        self.chip = gpiod.Chip(chip_name)
        self.line = self.chip.get_line(line_number)

        self.event_thread = threading.Thread(target=self._event_listener)
        self.event_thread.daemon = True
        self.running = True

        self._configure_line()

    def _configure_line(self):
        """Configure the GPIO line for edge detection."""
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

        self.line.request(config)

    def _event_listener(self):
        """Listen for GPIO edge events."""
        while self.running:
            event = self.line.event_wait(sec=1)
            if event:
                event = self.line.event_read()
                self.callback(event)

    def start(self):
        """Start the event listener thread."""
        self.event_thread.start()

    def stop(self):
        """Stop the event listener thread."""
        self.running = False
        self.event_thread.join()

    def __del__(self):
        """Clean up resources."""
        if self.line:
            self.line.release()

# Example callback function
def edge_detected(event):
    print(f"Edge detected! Event: {event}")

# Example usage
if __name__ == "__main__":
    handler = GPIOEventHandler(chip_name="gpiochip0", line_number=17, edge_type="rising", callback=edge_detected)
    handler.start()

    try:
        while True:
            pass  # Keep the program running
    except KeyboardInterrupt:
        handler.stop()
        print("Program terminated")


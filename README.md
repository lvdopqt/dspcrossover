# DSP Crossover Project

## Overview

This project is a Digital Signal Processing (DSP) crossover system designed to manage audio signal using a ESP32 microcontroller and a ADAU1401. The system allows users to adjust crossover filter settings, such as cutoff frequencies, and navigate through different menus in a LCD display using a rotary encoder and a back button.

## Schematics

The project physical schematic is placed in the docs folder. 

## Key Components

### 1. **DSP Processing (`features/crossover/`)**
   - **`service.py`**: Contains the `CrossoverService` class, which handles the calculation and setting of crossover filter coefficients. It includes methods for setting bandpass cutoff frequencies, calculating filter coefficients, and reading/writing coefficients to the DSP.
   - **`controller.py`**: Implements the `TwoWayCrossover` class, which manages the user interface for adjusting crossover settings. It handles cursor movement, frequency adjustment, and interaction with the rotary encoder and back button.

### 2. **Rotary Encoder (`features/rotary_encoder/`)**
   - **`rotary_encoder.py`**: Implements the `RotaryEncoder` class, which reads the state of the rotary encoder and emits events (`left`, `right`, `click`) based on user input. These events are sent to the `EventBus` for further processing.

### 3. **LCD Display (`external/lcd/i2c_lcd.py`)**
   - **`i2c_lcd.py`**: Provides an interface for controlling an I2C-connected LCD display. It supports basic operations like writing text, clearing the display, and controlling the cursor.

### 4. **Event Bus (`features/events/`)**
   - **`event_bus.py`**: Implements the `EventBus` class, which acts as a central hub for event handling. Components can subscribe to events (e.g., `click`, `right`, `left`, `back`) and respond accordingly.

### 5. **Back Button (`features/back_button/`)**
   - **`back_button.py`**: Implements the `BackButton` class, which handles the back button input. It emits a `back` event when the button is pressed, allowing the system to navigate back to previous menus or cancel actions.

### 6. **Navigator (`features/navigator/`)**
   - **`controller.py`**: Implements the `Navigator` class, which manages the current page or state of the system. It interacts with the LCD display and handles navigation events from the rotary encoder and back button.

### 7. **Main Application (`main.py`)**
   - **`main.py`**: The entry point of the application. It initializes the `EventBus`, `Navigator`, `RotaryEncoder`, and `BackButton`. It also sets up event listeners and runs the main loop to continuously check for encoder input.

## Usage

1. **Setup**: Ensure that the hardware components (ESP32, rotary encoder, back button, LCD display, and DSP) are properly connected to the microcontroller.
2. **Run the Application**: Execute `main.py` to start the application. The LCD will display the current state of the system, and the rotary encoder can be used to navigate and adjust settings.
3. **Adjust Crossover Settings**: Use the rotary encoder to select a filter and adjust its cutoff frequency. Press the encoder button to confirm the selection or the back button to cancel.

## Testing

The project includes several test scripts to verify the functionality of individual components:

- **`test_lcd.py`**: Tests the LCD display by writing a scrolling text message.
- **`test_adau.py`**: Tests the DSP by writing and reading crossover coefficients.
- **`test_rotary_encoder.py`**: Tests the rotary encoder by simulating rotations and button presses.
- **`test_back_button.py`**: Tests the back button by simulating button presses.

## Dependencies

- **MicroPython**: The project is designed to run on MicroPython-compatible hardware.
- **I2C LCD Library**: The `i2c_lcd.py` library is used to control the LCD display.
- **Sigma DSP Library**: The `sigma_dsp` library provides the necessary functionality to interact with the DSP.

## License

This project is open-source and available under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgments

- The project uses the `i2c_lcd.py` library for controlling the LCD display.
- The DSP processing is based on the Sigma DSP library, which provides a comprehensive interface for managing audio signal processing.
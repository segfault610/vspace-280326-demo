## How it works
The Carry-Chain Logic Lock is a hardware security primitive designed to protect chip functionality through timing-based obfuscation. The design is broken down into three main hardware modules:

+ **The Authorization Register (SIPO):** This is a 16-bit Serial-In Parallel-Out shift register. It uses a rising-edge detector on the `key_shift` input to synchronously sample the `key_data` bitstream, allowing a microcontroller to load a 16-bit authorization key.

+ **The Identity Comparator:** A 16-bit combinational equality block that continuously compares the current shift register value against a hardcoded Master Key (`16'hA5C3`). If the keys do not match, the `is_locked` signal remains HIGH.

+ **The Obfuscated Counter Stage:** This 24-bit counter is split into an 8-bit time-base and a 16-bit functional stage. An XOR gate intercepts the carry signal between these stages. 
    - **Unlocked:** When authorized, the XOR gate is transparent, and the 16-bit stage increments normally to produce a 1 Hz blink.
    - **Locked:** The carry is inverted, forcing the functional stage to increment on nearly every clock cycle, resulting in a high-speed "scrambled" output.

## How to test
To physically test this security primitive (or when using the Tiny Tapeout Commander app):

+ **Power & Clock:** Ensure the Tiny Tapeout board is powered and the system clock is set to 10 MHz.

+ **Reset:** Press the system reset button (rst_n LOW) to clear the internal 16-bit key. The `unlocked_led` (uo[0]) should be OFF, and the `blinker_output` (uo[1]) should show a high-frequency flicker.

+ **Key Entry:** Using a microcontroller or manual switches, provide the 16-bit bitstream for `0xA5C3` on `ui[0]`. For each bit, pulse the `key_shift` input (`ui[1]`) HIGH then LOW.

+ **Unlock Verification:** Once the 16th bit is shifted in, the `unlocked_led` (uo[0]) will immediately turn HIGH, and the `blinker_output` (uo[1]) will transition to a stable 1 Hz blink.

+ **Tamper Test:** If an incorrect bit is shifted in, the `unlocked_led` will remain LOW or turn OFF, and the output frequency will immediately return to the "scrambled" state.

## External hardware
To view and interact with this project, you will need:

+ **Tiny Tapeout Demo Board** (or equivalent carrier board).

+ **Status LEDs:** Connected to `uo_out[0]` (Status) and `uo_out[1]` (Obfuscated signal). An oscilloscope is recommended for viewing the frequency shift on `uo_out[1]`.

+ **Microcontroller (Optional):** An Arduino or ESP32 (operating at 3.3V) to automate the serial key entry via `ui_in[0]` and `ui_in[1]`.

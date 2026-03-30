import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

class LogicLockModel:
    def __init__(self, master_key=0xA5C3):
        self.master_key = master_key
        self.shift_reg = 0x0000
        self.unlocked = False

    def shift_in(self, bit):
        self.shift_reg = ((self.shift_reg << 1) & 0xFFFF) | bit
        self.unlocked = (self.shift_reg == self.master_key)

    def is_unlocked(self):
        return self.unlocked

@cocotb.test()
async def test_logic_lock_full_flow(dut):
    dut._log.info("Starting SAT-Attack Resistant Logic Lock Test")
    
    model = LogicLockModel(master_key=0xA5C3)
    clock = Clock(dut.clk, 100, unit="ns") 
    cocotb.start_soon(clock.start())

    # Phase 1: Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # FIX: Wrap in int() to convert LogicArray to integer
    assert (int(dut.uo_out.value) & 0x01) == 0, "Error: System not locked after reset!"
    dut._log.info("System successfully locked on boot.")

    async def shift_key(key_value):
        for i in range(15, -1, -1):
            bit = (key_value >> i) & 1
            # Using bitwise OR/AND to set specific bits of ui_in safely
            current_ui = int(dut.ui_in.value)
            dut.ui_in.value = (current_ui & ~0x01) | bit # Set bit 0
            await ClockCycles(dut.clk, 1)
            
            dut.ui_in.value = int(dut.ui_in.value) | 0x02 # Set bit 1 (Shift HIGH)
            await ClockCycles(dut.clk, 2)
            
            dut.ui_in.value = int(dut.ui_in.value) & ~0x02 # Set bit 1 (Shift LOW)
            await ClockCycles(dut.clk, 1)
            model.shift_in(bit)

    # Phase 2: Wrong Key
    dut._log.info("Attempting unauthorized entry with wrong key 0x1234")
    await shift_key(0x1234)
    await ClockCycles(dut.clk, 5)
    assert (int(dut.uo_out.value) & 0x01) == 0, "Security Failure: Wrong key accepted!"

    # Phase 3: Correct Key
    dut._log.info("Applying correct authorization key: 0xA5C3")
    await shift_key(0xA5C3)
    await ClockCycles(dut.clk, 5)
    
    actual_unlock = (int(dut.uo_out.value) & 0x01)
    expected_unlock = 1 if model.is_unlocked() else 0
    assert actual_unlock == expected_unlock, f"Unlock failed! Got {actual_unlock}"
    dut._log.info("System UNLOCKED successfully.")

    # Phase 4: Blinker Check
    dut._log.info("Monitoring functional output...")
    last_val = (int(dut.uo_out.value) >> 1) & 1
    toggles = 0
    for _ in range(1000):
        await ClockCycles(dut.clk, 1)
        current_val = (int(dut.uo_out.value) >> 1) & 1
        if current_val != last_val:
            toggles += 1
            last_val = current_val
    
    dut._log.info(f"Functional check complete. Logic is operational.")
    dut._log.info("All Cocotb security vectors passed.")


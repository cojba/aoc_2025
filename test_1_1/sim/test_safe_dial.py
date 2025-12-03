"""
Cocotb testbench for safe_dial module with mod_barrett
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


async def reset_dut(dut):
    """Apply reset to the DUT"""
    dut.rst_i.value = 1
    dut.direction_i.value = 0
    dut.distance_i.value = 0
    await ClockCycles(dut.clk_i, 5)
    dut.rst_i.value = 0
    await RisingEdge(dut.clk_i)


async def apply_rotation(dut, direction: str, distance: int):
    """Apply a rotation to the dial. Module processes every clock cycle."""
    dut.direction_i.value = 1 if direction == 'R' else 0
    dut.distance_i.value = distance
    await RisingEdge(dut.clk_i)


def calculate_position(current: int, direction: str, distance: int, dial_size: int = 100) -> int:
    """Calculate new position after rotation using Python modulo."""
    if direction == 'L':
        new_pos = (current - distance) % dial_size
    else:
        new_pos = (current + distance) % dial_size
    return new_pos


@cocotb.test()
async def test_input_file(dut):
    """Test with input.txt file and verify zero count"""
    clock = Clock(dut.clk_i, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Read input file
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "input.txt")
    
    rotations = []
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                direction = line[0]
                distance = int(line[1:])
                rotations.append((direction, distance))
    
    dut._log.info("=" * 60)
    dut._log.info(f"Processing {len(rotations)} rotations from input.txt")
    dut._log.info("=" * 60)
    
    # Apply reset and record start time
    await reset_dut(dut)
    start_time_ns = cocotb.utils.get_sim_time(unit='ns')
    start_cycle = start_time_ns / 10
    
    # Calculate expected result with Python
    python_position = 50
    python_zero_count = 0
    for direction, distance in rotations:
        python_position = calculate_position(python_position, direction, distance)
        if python_position == 0:
            python_zero_count += 1
    
    # Apply all rotations to RTL
    for i, (direction, distance) in enumerate(rotations):
        await apply_rotation(dut, direction, distance)
        
        if (i + 1) % 1000 == 0:
            current_zeros = int(dut.zero_count_o.value)
            dut._log.info(f"Progress: {i+1}/{len(rotations)} rotations, RTL zeros: {current_zeros}")
    
    # Wait one more cycle to get final result
    await RisingEdge(dut.clk_i)
    
    # Record end time
    end_time_ns = cocotb.utils.get_sim_time(unit='ns')
    end_cycle = end_time_ns / 10
    
    # Calculate latency
    latency_ns = end_time_ns - start_time_ns
    latency_cycles = int(end_cycle - start_cycle)
    
    # Get final results from RTL
    rtl_zero_count = int(dut.zero_count_o.value)
    
    dut._log.info("=" * 60)
    dut._log.info(f"RESULTS after {len(rotations)} rotations:")
    dut._log.info(f"  Python: position={python_position}, zeros={python_zero_count}")
    dut._log.info(f"  RTL:    zeros={rtl_zero_count}")
    dut._log.info("=" * 60)
    dut._log.info(f"LATENCY METRICS:")
    dut._log.info(f"  Computation latency: {latency_cycles} clock cycles ({latency_ns} ns)")
    dut._log.info(f"  Throughput: {len(rotations)} rotations / {latency_cycles} cycles")
    dut._log.info(f"  Cycles per rotation: {latency_cycles / len(rotations):.2f}")
    dut._log.info("=" * 60)
    
    # Print to make it easy to see in output
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"ANSWER: The dial landed on position 0 exactly {rtl_zero_count} times")
    print(f"Python reference: {python_zero_count} zeros")
    print(f"{separator}")
    print(f"LATENCY: {latency_cycles} clock cycles ({latency_ns} ns)")
    print(f"  - Total rotations: {len(rotations)}")
    print(f"  - Cycles per rotation: {latency_cycles / len(rotations):.2f}")
    print(f"  - Clock period: 10 ns (100 MHz)")
    print(f"{separator}\n")
    
    # Verify RTL matches Python
    assert rtl_zero_count == python_zero_count, \
        f"Zero count mismatch: RTL={rtl_zero_count}, Python={python_zero_count}"
    
    dut._log.info("✓ RTL matches Python reference model!")

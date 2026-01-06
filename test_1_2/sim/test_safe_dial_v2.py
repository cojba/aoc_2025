"""
Cocotb testbench for safe_dial_v2 - validates RTL against Python reference model.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import os


def count_zeros_during_rotation(position, direction, distance, dial_size=100):
    """Count how many times we pass through 0 during a rotation."""
    if distance == 0:
        return 0
    
    count = 0
    if direction == 'R':
        if position == 0:
            count = distance // dial_size
        else:
            steps_to_first_zero = dial_size - position
            if distance >= steps_to_first_zero:
                remaining = distance - steps_to_first_zero
                count = 1 + (remaining // dial_size)
    else:  # direction == 'L'
        if position == 0:
            count = distance // dial_size
        else:
            steps_to_first_zero = position
            if distance >= steps_to_first_zero:
                remaining = distance - steps_to_first_zero
                count = 1 + (remaining // dial_size)
    
    return count


def calculate_position(position, direction, distance, dial_size=100):
    """Calculate new position after rotation."""
    if direction == 'R':
        return (position + distance) % dial_size
    else:  # direction == 'L'
        return (position - distance) % dial_size


async def apply_rotation(dut, direction, distance):
    """Apply a single rotation."""
    dut.direction_i.value = 0 if direction == 'L' else 1
    dut.distance_i.value = distance
    await RisingEdge(dut.clk_i)
    await Timer(1, unit="ns")


@cocotb.test()
async def test_input_file(dut):
    """Test with input.txt file and verify zero count."""
    
    clock = Clock(dut.clk_i, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_i.value = 1
    dut.direction_i.value = 0
    dut.distance_i.value = 0
    await RisingEdge(dut.clk_i)
    await Timer(1, unit="ns")
    dut.rst_i.value = 0
    await RisingEdge(dut.clk_i)
    await Timer(1, unit="ns")
    
    # Load rotations
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
    
    dut._log.info(f"Loaded {len(rotations)} rotations from input.txt")
    
    # Track state
    py_position = 50
    py_zeros = 0
    
    # Process rotations
    for i, (direction, distance) in enumerate(rotations):
        # Calculate Python expected values
        zeros_this_rotation = count_zeros_during_rotation(py_position, direction, distance)
        py_zeros += zeros_this_rotation
        new_py_position = calculate_position(py_position, direction, distance)
        
        # Apply rotation to RTL
        await apply_rotation(dut, direction, distance)
        
        # Read RTL values
        rtl_position = int(dut.position_q.value)
        rtl_zeros = int(dut.zero_count_o.value)
        
        # Check for discrepancies
        if rtl_position != new_py_position or rtl_zeros != py_zeros:
            dut._log.error(f"\n=== DISCREPANCY FOUND at rotation {i+1} ===")
            dut._log.error(f"Rotation: {direction}{distance} from position {py_position}")
            dut._log.error(f"  Python: zeros_this={zeros_this_rotation}, new_pos={new_py_position}, total_zeros={py_zeros}")
            dut._log.error(f"  RTL:    new_pos={rtl_position}, total_zeros={rtl_zeros}")
            dut._log.error(f"  Position diff: {rtl_position - new_py_position}")
            dut._log.error(f"  Zeros diff: {rtl_zeros - py_zeros}")
            
            # Show previous few rotations for context
            if i >= 3:
                dut._log.info(f"\nPrevious rotations:")
                for j in range(max(0, i-3), i):
                    d, dist = rotations[j]
                    dut._log.info(f"  {j+1}: {d}{dist}")
            
            break
        
        # Update Python state
        py_position = new_py_position
        
        # Progress indicator
        if (i + 1) % 500 == 0:
            dut._log.info(f"Progress: {i+1}/{len(rotations)}, py_zeros={py_zeros}, rtl_zeros={rtl_zeros}")
    else:
        dut._log.info(f"\n=== ALL ROTATIONS PROCESSED ===")
        dut._log.info(f"  Python: position={py_position}, zeros={py_zeros}")
        dut._log.info(f"  RTL:    position={rtl_position}, zeros={rtl_zeros}")

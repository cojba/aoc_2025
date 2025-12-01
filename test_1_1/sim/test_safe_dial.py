"""
Cocotb testbench for safe_dial module

Tests the safe dial puzzle solver which counts how many times
the dial lands on position 0 after rotations.

The dial has 100 positions (0-99), starts at 50, and can rotate:
- Left (L): toward lower numbers, wraps from 0 to 99
- Right (R): toward higher numbers, wraps from 99 to 0
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


async def reset_dut(dut):
    """Apply reset to the DUT"""
    dut.rst_i.value = 1
    dut.valid_i.value = 0
    dut.direction_i.value = 0
    dut.distance_i.value = 0
    await ClockCycles(dut.clk_i, 5)
    dut.rst_i.value = 0
    await RisingEdge(dut.clk_i)


async def apply_rotation(dut, direction: str, distance: int):
    """
    Apply a rotation to the dial.
    
    Args:
        dut: Device under test
        direction: L for left, R for right
        distance: Distance to rotate (0-99)
    """
    # Set inputs
    dut.valid_i.value = 1
    dut.direction_i.value = 1 if direction == 'R' else 0
    dut.distance_i.value = distance
    
    # Wait for one clock cycle for operation to complete
    await RisingEdge(dut.clk_i)
    
    # Deassert valid
    dut.valid_i.value = 0


def calculate_position(current: int, direction: str, distance: int, dial_size: int = 100) -> int:
    """
    Calculate new position after rotation using Python modulo.
    
    Args:
        current: Current dial position
        direction: L or R
        distance: Distance to rotate
        dial_size: Size of dial (default: 100)
        
    Returns:
        New position after rotation
    """
    if direction == 'L':
        # Left (toward lower numbers)
        new_pos = (current - distance) % dial_size
    else:
        # Right (toward higher numbers)
        new_pos = (current + distance) % dial_size
    return new_pos


@cocotb.test()
async def test_initial_state(dut):
    """Test that dial starts at position 50 with zero count of 0"""
    # Start clock
    clock = Clock(dut.clk_i, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Apply reset
    await reset_dut(dut)
    
    # Check initial state
    assert dut.position_o.value == 50, f"Initial position should be 50, got {dut.position_o.value}"
    assert dut.zero_count_o.value == 0, f"Initial zero count should be 0, got {dut.zero_count_o.value}"
    assert dut.ready_o.value == 1, "Module should be ready initially"
    
    dut._log.info("✓ Initial state verified: position=50, zero_count=0")


@cocotb.test()
async def test_basic_rotations(dut):
    """Test basic left and right rotations without wrapping"""
    clock = Clock(dut.clk_i, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    
    # Test right rotation: 50 + 8 = 58
    await apply_rotation(dut, 'R', 8)
    await RisingEdge(dut.clk_i)
    assert dut.position_o.value == 58, f"After R8 from 50, expected 58, got {dut.position_o.value}"
    dut._log.info(f"✓ R8: 50 → {dut.position_o.value}")
    
    # Test left rotation: 58 - 30 = 28
    await apply_rotation(dut, 'L', 30)
    await RisingEdge(dut.clk_i)
    assert dut.position_o.value == 28, f"After L30 from 58, expected 28, got {dut.position_o.value}"
    dut._log.info(f"✓ L30: 58 → {dut.position_o.value}")


@cocotb.test()
async def test_wrap_around(dut):
    """Test that rotations wrap around correctly"""
    clock = Clock(dut.clk_i, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    
    # Go to position 5: 50 - 45 = 5
    await apply_rotation(dut, 'L', 45)
    await RisingEdge(dut.clk_i)
    assert dut.position_o.value == 5, f"Expected position 5, got {dut.position_o.value}"
    
    # Test left wrap: 5 - 10 = -5 → 95 (wrap around)
    await apply_rotation(dut, 'L', 10)
    await RisingEdge(dut.clk_i)
    expected = 95
    actual = int(dut.position_o.value)
    assert actual == expected, f"After L10 from 5, expected {expected}, got {actual}"
    dut._log.info(f"✓ L10 from 5: wraps to {actual}")
    
    # Test right wrap: 95 + 10 = 105 → 5 (wrap around)
    await apply_rotation(dut, 'R', 10)
    await RisingEdge(dut.clk_i)
    expected = 5
    actual = int(dut.position_o.value)
    assert actual == expected, f"After R10 from 95, expected {expected}, got {actual}"
    dut._log.info(f"✓ R10 from 95: wraps to {actual}")


@cocotb.test()
async def test_landing_on_zero(dut):
    """Test that landing on zero increments the counter"""
    clock = Clock(dut.clk_i, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    
    # Go directly to zero: 50 - 50 = 0
    await apply_rotation(dut, 'L', 50)
    await RisingEdge(dut.clk_i)
    assert dut.position_o.value == 0, f"Position should be 0, got {dut.position_o.value}"
    assert dut.zero_count_o.value == 1, f"Zero count should be 1, got {dut.zero_count_o.value}"
    dut._log.info(f"✓ First zero: position=0, count={dut.zero_count_o.value}")
    
    # Go away from zero: 0 + 25 = 25
    await apply_rotation(dut, 'R', 25)
    await RisingEdge(dut.clk_i)
    assert dut.position_o.value == 25, f"Position should be 25, got {dut.position_o.value}"
    assert dut.zero_count_o.value == 1, f"Zero count should still be 1, got {dut.zero_count_o.value}"
    dut._log.info(f"✓ Moved to 25: count still {dut.zero_count_o.value}")
    
    # Return to zero: 25 - 25 = 0
    await apply_rotation(dut, 'L', 25)
    await RisingEdge(dut.clk_i)
    assert dut.position_o.value == 0, f"Position should be 0, got {dut.position_o.value}"
    assert dut.zero_count_o.value == 2, f"Zero count should be 2, got {dut.zero_count_o.value}"
    dut._log.info(f"✓ Second zero: position=0, count={dut.zero_count_o.value}")


@cocotb.test()
async def test_example_sequence(dut):
    """Test the example sequence from the problem statement"""
    clock = Clock(dut.clk_i, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    
    # Example rotations from problem
    rotations = [
        ('L', 68),
        ('L', 30),
        ('R', 48),
        ('L', 5),
        ('R', 60),
        ('L', 55),
        ('L', 1),
        ('L', 99),
        ('R', 14),
        ('L', 82),
    ]
    
    # Expected positions after each rotation (from problem description)
    expected_positions = [82, 52, 0, 95, 55, 0, 99, 0, 14, 32]
    expected_zero_count = 3
    
    current_pos = 50
    zero_count = 0
    
    dut._log.info("=" * 60)
    dut._log.info("Testing example sequence from problem statement")
    dut._log.info("=" * 60)
    dut._log.info(f"Start: position = {current_pos}")
    
    for i, (direction, distance) in enumerate(rotations):
        # Calculate expected position using Python
        new_pos = calculate_position(current_pos, direction, distance)
        
        # Apply rotation to hardware
        await apply_rotation(dut, direction, distance)
        await RisingEdge(dut.clk_i)
        
        # Check position
        actual_pos = int(dut.position_o.value)
        assert actual_pos == expected_positions[i], \
            f"Step {i+1}: After {direction}{distance}, expected position {expected_positions[i]}, got {actual_pos}"
        
        # Track zeros
        if new_pos == 0:
            zero_count += 1
        
        # Log with visual indicator for zeros
        zero_marker = " ← ZERO!" if actual_pos == 0 else ""
        dut._log.info(f"Step {i+1:2d}: {direction}{distance:2d}: {current_pos:2d} → {actual_pos:2d}{zero_marker}")
        
        current_pos = new_pos
    
    # Check final zero count
    final_count = int(dut.zero_count_o.value)
    assert final_count == expected_zero_count, \
        f"Expected {expected_zero_count} zeros, got {final_count}"
    
    dut._log.info("=" * 60)
    dut._log.info(f"✓ Example sequence completed!")
    dut._log.info(f"✓ Final position: {dut.position_o.value}")
    dut._log.info(f"✓ Times landed on zero: {final_count} (expected: {expected_zero_count})")
    dut._log.info("=" * 60)


@cocotb.test()
async def test_sequential_zeros(dut):
    """Test multiple sequential landings on zero"""
    clock = Clock(dut.clk_i, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    
    # Go to zero
    await apply_rotation(dut, 'L', 50)
    await RisingEdge(dut.clk_i)
    assert dut.zero_count_o.value == 1
    
    # Full rotation right (100) should return to zero
    await apply_rotation(dut, 'R', 100)
    await RisingEdge(dut.clk_i)
    assert dut.position_o.value == 0, "Full rotation should return to 0"
    assert dut.zero_count_o.value == 2, "Second landing on zero"
    
    # Full rotation left (100) should return to zero
    await apply_rotation(dut, 'L', 100)
    await RisingEdge(dut.clk_i)
    assert dut.position_o.value == 0, "Full rotation should return to 0"
    assert dut.zero_count_o.value == 3, "Third landing on zero"
    
    dut._log.info(f"✓ Sequential zeros test passed: {dut.zero_count_o.value} landings")

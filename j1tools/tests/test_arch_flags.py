import os
import pytest
from pathlib import Path

from j1tools.assembler.asm import J1Assembler

def test_default_arch_flags():
    """Test default architecture flags"""
    assembler = J1Assembler(debug=False)
    
    # Check default flags
    assert assembler.arch_flags["fetch_type"] == "quickstore"
    assert assembler.arch_flags["alu_ops"] == "extended"
    
    # Check default constants
    assert assembler.constants["ARCH_FETCH_TYPE"] == 0
    assert assembler.constants["ARCH_ALU_OPS"] == 1


def test_set_fetch_type_symbolic():
    """Test setting fetch_type flag with symbolic value"""
    assembler = J1Assembler(debug=False)
    
    # Manually call the arch_flag_directive method
    items = ['.arch_flag', 'fetch_type', 'dualport']
    assembler.arch_flag_directive(items)
    
    # Check flags
    assert assembler.arch_flags["fetch_type"] == "dualport"
    assert assembler.constants["ARCH_FETCH_TYPE"] == 1


def test_set_fetch_type_numeric():
    """Test setting fetch_type flag with numeric value"""
    assembler = J1Assembler(debug=False)
    
    # Manually call the arch_flag_directive method
    items = ['.arch_flag', 'fetch_type', '1']
    assembler.arch_flag_directive(items)
    
    # Check flags
    assert assembler.arch_flags["fetch_type"] == "dualport"
    assert assembler.constants["ARCH_FETCH_TYPE"] == 1


def test_set_alu_ops_symbolic():
    """Test setting alu_ops flag with symbolic value"""
    assembler = J1Assembler(debug=False)
    
    # Manually call the arch_flag_directive method
    items = ['.arch_flag', 'alu_ops', 'original']
    assembler.arch_flag_directive(items)
    
    # Check flags
    assert assembler.arch_flags["alu_ops"] == "original"
    assert assembler.constants["ARCH_ALU_OPS"] == 0


def test_set_alu_ops_numeric():
    """Test setting alu_ops flag with numeric value"""
    assembler = J1Assembler(debug=False)
    
    # Manually call the arch_flag_directive method
    items = ['.arch_flag', 'alu_ops', '0']
    assembler.arch_flag_directive(items)
    
    # Check flags
    assert assembler.arch_flags["alu_ops"] == "original"
    assert assembler.constants["ARCH_ALU_OPS"] == 0


def test_invalid_flag_name():
    """Test error on invalid flag name"""
    assembler = J1Assembler(debug=False)
    
    # Manually call the arch_flag_directive method
    items = ['.arch_flag', 'invalid_flag', 'value']
    with pytest.raises(ValueError, match="Unknown architecture flag: invalid_flag"):
        assembler.arch_flag_directive(items)


def test_invalid_fetch_type_value():
    """Test error on invalid fetch_type value"""
    assembler = J1Assembler(debug=False)
    
    # Manually call the arch_flag_directive method
    items = ['.arch_flag', 'fetch_type', 'invalid_value']
    with pytest.raises(ValueError, match="Invalid value for fetch_type"):
        assembler.arch_flag_directive(items)


def test_invalid_alu_ops_value():
    """Test error on invalid alu_ops value"""
    assembler = J1Assembler(debug=False)
    
    # Manually call the arch_flag_directive method
    items = ['.arch_flag', 'alu_ops', 'invalid_value']
    with pytest.raises(ValueError, match="Invalid value for alu_ops"):
        assembler.arch_flag_directive(items)


def test_multiple_arch_flags():
    """Test setting multiple architecture flags"""
    assembler = J1Assembler(debug=False)
    
    # Manually call the arch_flag_directive method
    items1 = ['.arch_flag', 'fetch_type', 'dualport']
    items2 = ['.arch_flag', 'alu_ops', 'original']
    
    assembler.arch_flag_directive(items1)
    assembler.arch_flag_directive(items2)
    
    # Check flags
    assert assembler.arch_flags["fetch_type"] == "dualport"
    assert assembler.arch_flags["alu_ops"] == "original"
    
    # Check constants
    assert assembler.constants["ARCH_FETCH_TYPE"] == 1
    assert assembler.constants["ARCH_ALU_OPS"] == 0 
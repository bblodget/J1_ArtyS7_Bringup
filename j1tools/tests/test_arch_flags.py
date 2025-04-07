import os
import pytest
from pathlib import Path

from j1tools.assembler.asm import J1Assembler
from j1tools.assembler.directives import Directives
from j1tools.assembler.asm_types import AssemblerState
from j1tools.assembler.address_space import AddressSpace


def test_default_arch_flags():
    """Test default architecture flags"""
    state = AssemblerState(
        current_file="<unknown>", include_paths=[], include_stack=[], source_lines=[]
    )
    addr_space = AddressSpace()
    directives = Directives(state, addr_space, debug=False)

    # Check default flags
    assert (
        directives.constants["ARCH_FETCH_TYPE"] == 0
    )  # Defaults to FETCH_TYPE_QUICKSTORE
    assert directives.constants["ARCH_ALU_OPS"] == 0  # Defaults to ALU_OPS_ORIGINAL

    # Check default constants
    assert directives.constants["FETCH_TYPE_QUICKSTORE"] == 0
    assert directives.constants["FETCH_TYPE_DUALPORT"] == 1
    assert directives.constants["ALU_OPS_ORIGINAL"] == 0
    assert directives.constants["ALU_OPS_EXTENDED"] == 1


def test_set_fetch_type():
    """Test setting fetch_type flag"""
    state = AssemblerState(
        current_file="<unknown>", include_paths=[], include_stack=[], source_lines=[]
    )
    addr_space = AddressSpace()
    directives = Directives(state, addr_space, debug=False)

    # Set fetch_type to dualport
    items = [".arch_flag", "fetch_type", "FETCH_TYPE_DUALPORT"]
    directives.arch_flag_directive(items)

    # Check flags
    assert directives.constants["ARCH_FETCH_TYPE"] == 1  # FETCH_TYPE_DUALPORT value


def test_set_alu_ops():
    """Test setting alu_ops flag"""
    state = AssemblerState(
        current_file="<unknown>", include_paths=[], include_stack=[], source_lines=[]
    )
    addr_space = AddressSpace()
    directives = Directives(state, addr_space, debug=False)

    # Set alu_ops to extended
    items = [".arch_flag", "alu_ops", "ALU_OPS_EXTENDED"]
    directives.arch_flag_directive(items)

    # Check flags
    assert directives.constants["ARCH_ALU_OPS"] == 1  # ALU_OPS_EXTENDED value


def test_invalid_flag_name():
    """Test error on invalid flag name"""
    state = AssemblerState(
        current_file="<unknown>", include_paths=[], include_stack=[], source_lines=[]
    )
    addr_space = AddressSpace()
    directives = Directives(state, addr_space, debug=False)

    # Try to set invalid flag
    items = [".arch_flag", "invalid_flag", "value"]
    with pytest.raises(ValueError, match="Unknown architecture flag: invalid_flag"):
        directives.arch_flag_directive(items)


def test_invalid_fetch_type_value():
    """Test error on invalid fetch_type value"""
    state = AssemblerState(
        current_file="<unknown>", include_paths=[], include_stack=[], source_lines=[]
    )
    addr_space = AddressSpace()
    directives = Directives(state, addr_space, debug=False)

    # Try to set invalid fetch_type value
    items = [".arch_flag", "fetch_type", "INVALID_VALUE"]
    with pytest.raises(ValueError, match="Invalid value for fetch_type: INVALID_VALUE"):
        directives.arch_flag_directive(items)


def test_invalid_alu_ops_value():
    """Test error on invalid alu_ops value"""
    state = AssemblerState(
        current_file="<unknown>", include_paths=[], include_stack=[], source_lines=[]
    )
    addr_space = AddressSpace()
    directives = Directives(state, addr_space, debug=False)

    # Try to set invalid alu_ops value
    items = [".arch_flag", "alu_ops", "INVALID_VALUE"]
    with pytest.raises(ValueError, match="Invalid value for alu_ops: INVALID_VALUE"):
        directives.arch_flag_directive(items)


def test_multiple_arch_flags():
    """Test setting multiple architecture flags"""
    state = AssemblerState(
        current_file="<unknown>", include_paths=[], include_stack=[], source_lines=[]
    )
    addr_space = AddressSpace()
    directives = Directives(state, addr_space, debug=False)

    # Set fetch_type to dualport
    items1 = [".arch_flag", "fetch_type", "FETCH_TYPE_DUALPORT"]
    directives.arch_flag_directive(items1)

    # Set alu_ops to extended
    items2 = [".arch_flag", "alu_ops", "ALU_OPS_EXTENDED"]
    directives.arch_flag_directive(items2)

    # Check flags
    assert directives.constants["ARCH_FETCH_TYPE"] == 1  # FETCH_TYPE_DUALPORT value
    assert directives.constants["ARCH_ALU_OPS"] == 1  # ALU_OPS_EXTENDED value

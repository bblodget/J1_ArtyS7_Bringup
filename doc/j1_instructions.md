# J1 Processor Instruction Set Documentation

The J1 processor uses 16-bit instructions with three main instruction types:

## 1. Literal (15-bit)
```
Bit num:5432_1098_7654_3210
Format: 1xxx_xxxx_xxxx_xxxx
MSB=1: Push 15-bit immediate value onto data stack
```
- Bit 15: Always 1
- Bits 14-0: Immediate value (sign extended)
- Example: `8041` = Push 0x0041 (ASCII 'A')

## 2. Jump Instructions (13-bit)
```
Bit num:5432_1098_7654_3210
Format: 000x_xxxx_xxxx_xxxx  - Jump
Format: 001x_xxxx_xxxx_xxxx  - Conditional Jump
Format: 010x_xxxx_xxxx_xxxx  - Call
```
- Bits 15-13: Operation type
  - 000: Unconditional Jump
  - 001: Conditional Jump (jump if TOS = 0)
  - 010: Call (push return address to R stack)
- Bits 12-0: Target address (word address, not byte address)
  - Each word is 16 bits
  - Word address 1 = byte address 2
  - Word address N = byte address N*2
- Example: `0003` = Jump to word address 3 (byte address 6)

### Memory Addressing Note
The J1 uses word addressing for all memory operations:
- Instructions are 16 bits (2 bytes) each
- Memory addresses in jump/call instructions refer to word locations
- To convert between addressing modes:
  - Word address = Byte address ÷ 2
  - Byte address = Word address × 2

## 3. ALU Operations (13-bit)
```
Bit num:5432_1098_7654_3210
Format: 011a_aaaa_ssss_rrdd
```
- Bits 15-13: 011 (ALU operation)
- Bits 12-8: ALU operation
- Bits 7-4: Stack/Memory operations
- Bits 3-2: Return stack delta
- Bits 1-0: Data stack delta

### ALU Operations (aaaaa)
```
0000: T          (copy T)
0100: N          (copy NOS)
0200: T+N        (add)
0300: T&N        (and)
0400: T|N        (or)
0500: T^N        (xor)
0600: ~T         (invert)
0700: N==T       (equal)
0800: N<T        (signed less)
0900: T2/        (shift right)
0A00: T2*        (shift left)
0B00: rT         (copy R stack top)
0C00: N-T        (subtract)
0D00: io[T]      (I/O read)
0E00: status     (depth)
0F00: Nu<T       (unsigned less)
```

### Stack/Memory Operations (ssss)
```
0010: T->N       (copy T to N)
0020: T->R       (copy T to R)
0030: N->[T]     (memory write)
0040: N->io[T]   (I/O write)
0050: IORD       (I/O read)
0060: fDINT      (disable interrupts)
0070: fEINT      (enable interrupts)
0080: RET        (return)
```

### Stack Delta Bits
```
Return Stack (rr):
00: unchanged
01: r+1 (push)
10: r-2 (pop two)
11: r-1 (pop one)

Data Stack (dd):
00: unchanged
01: d+1 (push)
10: d-2 (pop two)
11: d-1 (pop one)
```

## Example Program
```
8041  // Push 'A' onto data stack
9000  // Push UART address (0x1000)
6042  // ALU: I/O write and pop both values
0003  // Jump to word address 3 (self)
```

### Instruction Breakdown
1. `8041`: Literal push
   - 1000 0000 0100 0001
   - Pushes value 0x41 ('A')

2. `9000`: Literal push
   - 1001 0000 0000 0000
   - Pushes value 0x1000 (UART address)

3. `6042`: ALU operation
   - 0110 0000 0100 0010
   - I/O write (0040)
   - Pop two values from data stack (0002)

4. `0003`: Jump
   - 0000 0000 0000 0011
   - Jump to word address 3

## Program Counter and Interrupts

### Program Counter (PC)
- The PC uses byte addresses internally (unlike jump instructions which use word addresses)
- PC[15:1] contains the byte address of the current instruction
  - Each instruction is 2 bytes (16 bits)
  - PC[15:1] will be even numbers (0,2,4,6...)
  - To get word address: PC[15:1] ÷ 2
  - Example: PC[15:1] = 6 means word address 3
- PC[0] is used as the interrupt enable flag
  - PC[0] = 0: Interrupts disabled
  - PC[0] = 1: Interrupts enabled
- When calculating next instruction:
  - Normal execution: PC += 2 (moves to next word)
  - Jumps/Calls: PC = {target_address × 2, interrupt_enable}
  - Example: JMP 3 sets PC to {3 × 2, interrupt_enable} = {6, interrupt_enable}

### Interrupt Handling
- When an interrupt occurs (and enabled):
  - PC[0] is cleared (disables nested interrupts)
  - Current PC is pushed to return stack
  - PC is set to interrupt vector (word address 2)
- EINT instruction (0x6070):
  - Sets PC[0] to 1
  - Usually used at end of interrupt handler
- DINT instruction (0x6060):
  - Clears PC[0] to 0
  - Used to disable interrupts
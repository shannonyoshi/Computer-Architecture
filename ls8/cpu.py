"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.register = [0] * 8
        self.register[7] = 0xF4 # stack pointer
        self.ram = [0] * 256  # add 256 bytes
        self.pc = 0 

    def clean_bin(self, instruction):
        instruction.strip() # removes whitespace
        if instruction.startswith("0") or instruction.startswith("1"):
            return int(instruction[:8], 2) # returns fist 8 characters on the line in binary

    def load(self, program_name):
        """Load a program into memory."""

        address = 0

        with open("examples/" + program_name) as program:
            for instruction in program:
                clean_instruction = self.clean_bin(instruction)
                # print("cleaned_instruction: ", clean_instruction)
                if clean_instruction is not None:
                    # print(instruction)
                    self.ram[address] = clean_instruction
                    address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        reg_a = self.ram[self.pc+1]
        reg_b = self.ram[self.pc+2]

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        # elif op == "SUB": etc
        elif op == "MULT":
            self.register[reg_a] *= self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def LDI(self):
        # print("instruction: ", instruction)
        reg_num = self.ram[self.pc+1]
        # print(f"reg_num: {reg_num}")
        value = self.ram[self.pc+2]
        # print(f"Value: {value}")
        self.register[reg_num] = value
        print(f"LDI: {value} saved to register {reg_num}")
        print(f"REGISTERS: {self.register}")

    def PRN(self):
        print("PRINT")
        reg_num = self.ram[self.pc+1]
        print(self.register[reg_num])

    def POP(self):
        "Copy the value from the address pointed to by `SP` to the given register."
        stack_value = self.ram_read(self.register[7])
        reg_num = self.ram_read(self.pc+1)
        self.register[reg_num] = stack_value
        print(f"POP {stack_value} to register {reg_num}")
        self.register[7]+=1

    def PUSH(self):

        self.register[7]-=1 # decrement stack pointer
        reg_num = self.ram_read(self.pc+1) # get the register number
        register_value = self.register[reg_num] #value to be copied
        self.ram_write(self.register[7], register_value)
        print(f"PUSH value: {self.ram[self.register[7]]} to self.ram {self.register[7]}")

    def CALL(self):
        reg_num = self.ram_read(self.pc+1)
        register_value = self.register[reg_num]
        stack_value = self.pc+2
        self.register[7]-=1
        self.ram_write(self.register[7], stack_value)
        self.pc = register_value

    def RET(self):
        stack_value = self.ram_read(self.register[7])
        print("STACK VALUE", stack_value)
        self.pc = stack_value
        self.register[7]+=1

    def func_switcher(self, instruction):
        switcher = {
            0b10000010: lambda: self.LDI(),
            0b01000111: lambda: self.PRN(),
            0b10100010: lambda: self.alu("MULT", self.ram[self.pc+1], self.ram[self.pc+2]),
            0b10100000: lambda: self.alu("ADD", self.ram[self.pc+1], self.ram[self.pc+2]),
            0b01000110: lambda: self.POP(),
            0b01000101: lambda: self.PUSH(),
            0b01010000: lambda: self.CALL(),
            0b00010001: lambda: self.RET()
        }
        return switcher.get(instruction, lambda: "Invalid command")

    def run(self):
        # print("RUN")
        halted = False
        print(f"Stack pointer = {self.register[7]}")
        while not halted:
            print("PC", self.pc)
            instruction = self.ram[self.pc]
            # print("instruction in run: ", instruction)
            # print("self.pc: ", self.pc)
            # print("instruction", instruction)
            if instruction == 0b00000001:
                halted = True
            else:
                func = self.func_switcher(instruction)
                func()
                if instruction not in (0b01010000, 0b00010001):
                    operand_count = instruction >> 6
                    instruction_length = operand_count+1
                    self.pc += instruction_length

"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.register = [0] * 8
        self.ram = [0] * 256  # add 256 bytes
        self.pc = 0

    def clean_bin(self, instruction):
        instruction.strip()
        if instruction.startswith("0") or instruction.startswith("1"):
            # print("instruction: ", instruction)
            first8 = instruction[:8]
            # print("CLEAN_BIN INSTRUCTION: ", first8)
            return int(first8, 2)

    def load(self, program_name):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]
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
        if op == "MULT":
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
        return self.register[address]

    def ram_write(self, address, value):
        self.register[address] = value

    def LDI(self):
        # print("instruction: ", instruction)
        reg_num = self.ram[self.pc+1]
        # print(f"reg_num: {reg_num}")
        value = self.ram[self.pc+2]
        # print(f"Value: {value}")
        self.ram_write(reg_num, value)
        # print(f"{value} saved to register {reg_num}")

    def PRN(self):
        # print("PRINT")
        reg_num = self.ram[self.pc+1]
        print(self.register[reg_num])

    def func_switcher(self, instruction):
        switcher = {
            0b10000010: lambda: self.LDI(),
            0b01000111: lambda: self.PRN(),
            0b10100010: lambda: self.alu("MULT", self.ram[self.pc+1], self.ram[self.pc+2])
        }
        return switcher.get(instruction, lambda: "Invalid command")


    def run(self):
        # print("RUN")
        halted = False


        while not halted:
            instruction = self.ram[self.pc]
            # print("instruction in run: ", instruction)
            # print("self.pc: ", self.pc)
            # print("instruction", instruction)
            if instruction == 0b00000001:
                halted = True
            else:
                func = self.func_switcher(instruction)
                func()
            operand_count = instruction >> 6
            instruction_length = operand_count+1
            self.pc += instruction_length

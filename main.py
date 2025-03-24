import pyglet
import sys
import random

class CPU(pyglet.window.Window):
    def initialise(self):
        self.clear()
        self.key_inputs = [0]*16 #16 inputs on a chip-8 keyboard
        self.display_buffer = [0]*32*64 #32x64 pixel screen
        self.memory = [0]*4096  #4kb memory
        self.gpio = [0]*16
        self.sound_timer = 0
        self.delay_timer = 0
        self.index = 0
        self.op_code = 0
        self.stack = []
        self.should_draw = False
        self.sound = pyglet.media.load('vine-boom.mp3', streaming=False)

        self.pc = 0x200

        self.funcmap = {0x0000: self._0ZZZ,
                        0x00e0: self.CLS,
                        0x00ee: self.RET,
                        0x1000: self.JUMP,
                        0x2000: self.CALL,
                        0x3000: self.SKIPEQUAL,
                        0X4000: self.SKIPUNEQUAL,
                        0x5000: self.SKIPREGISTEREQUAL,
                        0x6000: self.SETREGISTER,
                        0x7000: self.ADDTOREGISTER,
                        0x8000: self.which8func, #not sure how to prevent conflict with 8xy0
                        0x8000: self.SETVXVY,
                        0x8001: self.SETVXORVY,
                        0x8002: self.SETVXANDVY,
                        0x8003: self.SETVXXORVY,
                        0x8004: self.ADDVXVY,
                        0x8005: self.SUBVXVY,
                        0x8006: self.SHIFTRIGHTVX,
                        0x8007: self.SUBNVXVY,
                        0x800E: self.SHIFTLEFTVX,
                        0x9000: self.SKIPREGISTERUNEQUAL,
                        0xA000: self.SETINDEX,
                        0xB000: self.JUMPV0,
                        0xC000: self.VXANDRAND,
                        0xD000: self.DRAWVXVY

        }   


        i = 0
        while i < 80:
            self.memory[i] = self.fonts[i]
            i+=1

    def _0ZZZ(self):
        extracted_op = self.opcode & 0xf0ff
        try:
            self.funcmap[extracted_op]()
        except:
            print("Unknown instruction: %X" % self.opcode)
    
    def CLS(self): #clear screen
        self.display_buffer = [0]*32*64
        self.should_draw = True

    def RET(self):
        self.pc = self.stack.pop()

    def JUMP(self): #0x1nnn
        self.pc = self.op_code & 0x0fff

    def CALL(self): #0x2nnn
        self.stack.pop()
        self.stack.append(self.pc)
        self.pc = self.op_code & 0x0fff

    def SKIPEQUAL(self): #0x3xkk
        op_code_checker = self.op_code & 0x00ff
        register_checker = list(hex(self.op_code))[3]
        
        if self.gpio[register_checker] == op_code_checker:
            self.pc + 2
    
    def SKIPUNEQUAL(self): #0x4xkk
        op_code_checker = self.op_code & 0x00ff
        register_checker = list(hex(self.op_code))[3]
        
        if self.gpio[register_checker] != op_code_checker:
            self.pc + 2

    def SKIPREGISTEREQUAL(self): #0x5xy0
        vx = list(hex(self.op_code))[3]
        vy = list(hex(self.op_code))[4]
        if self.gpio[vx] == self.gpio[vy]:
            self.pc + 2

    def SETREGISTER(self): #0x6xkk
        op_code_checker = self.op_code & 0x00ff
        vx = list(hex(self.op_code))[3]
        self.gpio[vx] = op_code_checker

    def ADDTOREGISTER(self): #0x7xkk
        op_code_checker = self.op_code & 0x00ff
        vx = list(hex(self.op_code))[3]
        self.gpio[vx] += op_code_checker

    def SETVXVY(self):
        vx = list(hex(self.op_code))[3]
        vy = list(hex(self.op_code))[4]
        self.gpio[vx] = self.gpio[vy]

    def SETVXORVY(self):
        vx = list(hex(self.op_code))[3]
        vy = list(hex(self.op_code))[4]
        vx_or_vy = self.gpio[vx] | self.gpio[vy]
        self.gpio[vx] = vx_or_vy

    def SETVXANDVY(self):
        vx = list(hex(self.op_code))[3]
        vy = list(hex(self.op_code))[4]
        vx_and_vy = self.gpio[vx] & self.gpio[vy]
        self.gpio[vx] = vx_and_vy

    def SETVXXORVY(self):
        vx = list(hex(self.op_code))[3]
        vy = list(hex(self.op_code))[4]
        vx_xor_vy = self.gpio[vx] ^ self.gpio[vy]
        self.gpio[vx] = vx_xor_vy

    def ADDVXVY(self):
        vx = list(hex(self.op_code))[3]
        vy = list(hex(self.op_code))[4]
        sum = self.gpio[vx] + self.gpio[vy]
        if sum > 255:
            self.gpio[15] = 1
        else:
            self.gpio[15] = 0
        self.gpio[vx] = sum & 0xff

    def SUBVXVY(self):
        vx = list(hex(self.op_code))[3]
        vy = list(hex(self.op_code))[4]
        difference = self.gpio[vx] - self.gpio[vy]
        if difference > 0:
            self.gpio[15] = 1
        else:
            self.gpio[15] = 0
        self.gpio[vx] = difference

    def SUBNVXVY(self): #dubious
        vx = list(hex(self.op_code))[3]
        vy = list(hex(self.op_code))[4]
        difference = self.gpio[vy] - self.gpio[vx]
        if difference > 0:
            self.gpio[15] = 1
        else:
            self.gpio[15] = 0
        self.gpio[vx] = difference

    def SHIFTRIGHTVX(self): #dubious
        vx = list(hex(self.op_code))[3]
        self.gpio[vx] = self.gpio[vx] >> 1
        # TODO MORE

    def SHIFTLEFTVX(self): #dubious
        vx = list(hex(self.op_code))[3]
        self.gpio[vx] = self.gpio[vx] >> 1
        # TODO MORE

    def SKIPREGISTERUNEQUAL(self): #0x9xy0
        vx = list(hex(self.op_code))[3]
        vy = list(hex(self.op_code))[4]
        if self.gpio[vx] != self.gpio[vy]:
            self.pc + 2

    def SETINDEX(self): #0xAnnn
        self.index = self.op_code & 0x0fff

    def JUMPV0(self): #0xBnnn
        sum = self.op_code & 0x0fff
        self.pc = sum + self.gpio[0]

    def VXANDRAND(self): #0xCxkk
        op_code_checker = self.op_code & 0x00ff
        vx = list(hex(self.op_code))[3]
        rand = random.randint(0, 255)
        self.gpio[vx] = op_code_checker & rand

    def DRAWVXVY(self): #0xDxyn
        pass
    def load_rom(self, rom_path):
        # log("Loading %s..." % rom_path)
        binary = open(rom_path, "rb").read()
        i = 0
        while i < len(binary):
            self.memory[i+0x200] = ord(binary[i])
            i+=1

    def on_key_press(self, symbol, modifiers):
        pass 
        # DO SOME INSTRUCTION
    
    def on_key_release(self, symbol, modifiers):
        pass
        # DO SOME INSTRUCTION

    def decrement_sound_timer(self):
        if self.sound_timer > 0:
            self.sound_timer-=1
            if self.sound_timer != 0:
                self.sound.play()

    def decrement_delay_timer(self):
        if self.delay_timer > 0:
            self.delay_timer-=1

    def process_opcode(self):
        # self.vx = (self.opcode & 0x0f00) >> 8
        # self.vy = (self.opcode & 0x00f0) >> 4
        # self.pc += 2

        extracted_op = self.opcode & 0xf000
        try:
            self.funcmap[extracted_op]() # call the associated method
        except:
            print("Unknown instruction: %X" % self.opcode)

    def cycle(self):
        self.op_code = self.memory[self.pc]
        
        self.process_opcode()

        self.pc+=2

        self.decrement_sound_timer()
        self.decrement_delay_timer()



    def main(self):
        self.__init__()
        self.load_rom(sys.argv[1])
        while not self.has_exit:
            self.dispatch_events()
            self.cycle()
            self.draw()
    
cpu = CPU()

cpu.main()
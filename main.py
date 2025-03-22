import pyglet
import sys

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
    
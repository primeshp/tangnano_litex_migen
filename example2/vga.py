from migen import *
from litex.soc.interconnect.csr import *
from math import *


V_BackPorch   = 12
V_Pulse       = 11
HightPixel    = 272
V_FrontPorch  = 8
H_BackPorch   = 50
H_Pulse       = 10
WidthPixel    = 480
H_FrontPorch  = 8
PixelsForHS  =   WidthPixel + H_BackPorch + H_FrontPorch
LinesForVS   =   HightPixel + V_BackPorch + V_FrontPorch


class _VGA(Module):
    #This module expect a clock of 33.3MHz
    def __init__(self):

      self.LCD_R = Signal(5)
      self.LCD_G = Signal(6)
      self.LCD_B = Signal(5)
      self.LCD_HSYNC = Signal()
      self.LCD_VSYNC = Signal() 
      self.LCD_DEN = Signal()
      self.LCD_CLK = Signal()
      self.LCD_COLOR = Signal(16)
      

      
      self.color = Signal(16)  #16 Bits color[0:5] = b  color[5:11] = b  color[11:15] = b  Reset with 
      self.PixelCount = Signal(16,reset=0)
      self.LineCount  = Signal(16,reset=0)
      self.FramebufferPoition = Signal(10)
      
      self.sync += If((self.PixelCount == PixelsForHS), #at the end of the Horizontal scan move to next line
                            self.PixelCount.eq(0),
                            self.LineCount.eq(self.LineCount+1)
                        ).Elif((self.LineCount == LinesForVS), #At the end of the frame move back to begining of next Frame
                            self.LineCount.eq(0),
                            self.PixelCount.eq(0),
                        ).Else(
                            self.PixelCount.eq(self.PixelCount+1) #Increase Pixel
                        )
      self.sync += If(self.LCD_DEN, self.FramebufferPoition.eq(self.FramebufferPoition+1)).Else(self.FramebufferPoition.eq(0))
                        
                
      
      self.comb += If(((self.PixelCount>H_Pulse-1) & (self.PixelCount < (PixelsForHS-H_FrontPorch+1))), 
                             self.LCD_HSYNC.eq(0)
                   ).Else(self.LCD_HSYNC.eq(1))

      self.comb += If(((self.LineCount>V_Pulse-1) & (self.LineCount < LinesForVS+1)),
                             self.LCD_VSYNC.eq(0)
                   ).Else(self.LCD_VSYNC.eq(1))
      self.comb += If(((self.PixelCount > H_BackPorch-1) & (self.PixelCount<PixelsForHS-H_FrontPorch+1) & (self.LineCount > V_BackPorch-1) & ( self.LineCount < LinesForVS-V_FrontPorch+1 )),
                             self.LCD_DEN.eq(1)
                   ).Else(self.LCD_DEN.eq(0)) 
      

      self.comb += self.LCD_R.eq(self.LCD_COLOR[11:16])
      self.comb += self.LCD_G.eq(self.LCD_COLOR[5:11])
      self.comb += self.LCD_B.eq(self.LCD_COLOR[0:5])
      self.comb += self.LCD_CLK.eq(ClockSignal())   #this is how you can connect to sys clock signal


class LCD_Module(Module,AutoCSR):
    #This module expect a clock of 33.3MHz
    def __init__(self, pads):
      lcd = _VGA()
      self.submodules += lcd 
      
      self.specials.mem = Memory(16,480,init=[0x001F]*480) 
      self.specials.rdport = self.mem.get_port()
      
      self.comb += self.rdport.adr.eq(lcd.FramebufferPoition[0:9])
      self.comb += lcd.LCD_COLOR.eq(self.rdport.dat_r)
      #self.comb += lcd.LCD_COLOR.eq(self.color.storage)
      
      self.comb +=[
      pads.LCD_R.eq(lcd.LCD_R),
      pads.LCD_G.eq(lcd.LCD_G),
      pads.LCD_B.eq(lcd.LCD_B), 
      pads.LCD_HSYNC.eq(lcd.LCD_HSYNC),
      pads.LCD_VSYNC.eq(lcd.LCD_VSYNC),
      pads.LCD_DEN.eq(lcd.LCD_DEN),
      pads.LCD_CLK.eq(lcd.LCD_CLK),
      ]
      





if __name__ == '__main__':
    # LCD Display Simulation
    print("LCD Simulation")
    dut = _VGA()

    def dut_tb(dut):
        for i in range(512*1024):
            yield

    run_simulation(dut, dut_tb(dut), vcd_name="vga_lcd.vcd")
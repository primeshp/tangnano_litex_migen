# Build/Use
# ---------
#This code is burrowed from the https://github.com/litex-hub/litex-boards/tree/master/litex_boards/targets
#Only two Modifications done to the original file
# 1. Change the clock speed of the system to 33.3MHz
# 2. Added LCD Interface using _lcd_ios and extended the platform platform.add_extension(_lcd_ios)
# 3. Created the LCD module using self.submodules.lcd = LCD_Module(pads=lcd_interface)



# 1) Build/Load design: ./base.py --csr-csv=csr.csv --build --load
# 2) litex_server --uart --uart-port=/dev/ttyUSB1 --uart-baudrate=1000000
# 5) Test UARTBone ex: litex_cli --regs


import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.soc.cores.clock.gowin_gw1n import  GW1NPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from vga import LCD_Module
from litex.build.generic_platform import *

from litex_boards.platforms import tang_nano


#When you want to define additional Pins than the original platform provide you use the following to define it
#Then once the platform object created you do platform.add_extension(_lcd_ios)

_lcd_ios = [("lcd_interface",0,
                Subsignal("LCD_R",Pins("27 28 29 30 31")),
                Subsignal("LCD_G",Pins("32 33 34 38 39 40")),
                Subsignal("LCD_B",Pins("41 42 43 44 45")),
                Subsignal("LCD_HSYNC",Pins("10")),
                Subsignal("LCD_VSYNC",Pins("46")),
                Subsignal("LCD_DEN",Pins("5")),
                Subsignal("LCD_CLK",Pins("11")),
                IOStandard("LVCMOS33")
            ),]
          

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys   = ClockDomain()

        # # #

        # Clk / Rst.
        clk24 = platform.request("clk24")
        rst_n = platform.request("user_btn", 0)

        #Need to use SSPI and MSPI as regular IO
        platform.toolchain.options["use_sspi_as_gpio"] = 1
        platform.toolchain.options["use_mspi_as_gpio"] = 1

        # PLL.
        self.submodules.pll = pll = GW1NPLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk24, 24e6)   #Input clock to the PLL
        pll.create_clkout(self.cd_sys, sys_clk_freq) #Create the output clock


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCMini):
    def __init__(self, sys_clk_freq=int(33e3), with_led_chaser=False, **kwargs):
        platform = tang_nano.Platform()
        platform.add_extension(_lcd_ios)
        lcd_interface = platform.request("lcd_interface")
        
        # SoCMini ----------------------------------------------------------------------------------
        SoCMini.__init__(self, platform, sys_clk_freq,
            ident         = "LiteX SoC on Tang Nano",
            ident_version = True)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        self.submodules.lcd = LCD_Module(pads=lcd_interface) #This is the LCD custom module

        # UARTBone ---------------------------------------------------------------------------------
        self.add_uartbone(baudrate=int(1e6)) # CH552 firmware does not support traditional baudrates.

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)
        # Led
        


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Tang Nano")
    parser.add_argument("--build",       action="store_true", help="Build bitstream")
    parser.add_argument("--load",        action="store_true", help="Load bitstream")
    parser.add_argument("--flash",       action="store_true", help="Flash Bitstream")
    parser.add_argument("--sys-clk-freq",default=33.3e6,        help="System clock frequency (default: 48MHz)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq      = int(float(args.sys_clk_freq)), 
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, "impl", "pnr", "project.fs"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, os.path.join(builder.gateware_dir, "impl", "pnr", "project.fs"))

if __name__ == "__main__":
    main()

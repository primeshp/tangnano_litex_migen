One of the challenges with Migen is that not too many example projects exist. This is to address this concerns

This is examples of using Litex/Migen to program the FPGA of Tang Nano $5 FPGA board
You need a Tang Nano 1K board and a 480X272 LCD display to do these examples without any modifications.

example1 create a SOC with a single CSR register to control the color of the LCD display. Its using UARTBridge to commnicate from local host to FPGA wishbone
example2 exapnds the original example to have a memory mapped color controls horizontaly

Credits
    the VGA code is translated to Migen using Sipeed orignial Verilog code at https://github.com/sipeed/Tang-Nano-examples
    base.py is a modification from the tang nano target file in https://github.com/litex-hub/litex-boards/tree/master/litex_boards
    
    
Primesh Pinto 

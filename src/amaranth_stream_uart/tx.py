from amaranth import *
from amaranth.sim import Simulator
from amaranth.back import rtlil, verilog
from amaranth.lib import stream,wiring
from amaranth.lib.wiring import In, Out

class UARTTransmitter(wiring.Component):
    """
    A module for transmitting bytes on a 8N1 UART at a configurable baudrate.
    Input is 8bit stream, outputn is tx pad.
    """

    stream: In(stream.Signature(signed(8)))

    tx: Out(1, init=1)

    def __init__(self, divider):
        super().__init__()

        self.divider = divider

    def elaborate(self, platform):
        m = Module()

        ctr_div = Signal(range(self.divider))
        buffer = Signal(8)
        bit_index = Signal(4)
        uart_clk = Signal()

        # uart-clk is running continous, so packets can be transferred in a constant raster
        with m.If(ctr_div == 0):
            m.d.sync += ctr_div.eq(self.divider - 1)
        m.d.sync += ctr_div.eq(ctr_div - 1)
        m.d.comb += uart_clk.eq(ctr_div == 0)

        with m.FSM():
            with m.State("Idle"):
                with m.If(self.stream.valid):
                    m.d.sync += buffer.eq(self.stream.payload)
                    m.next = "Armed"
                m.d.comb += self.tx.eq(1)
                m.d.comb += self.stream.ready.eq(1)

            with m.State("Armed"):
                with m.If(uart_clk):
                    m.next = "Start"
                m.d.comb += self.tx.eq(1)
                m.d.comb += self.stream.ready.eq(0)

            with m.State("Start"):
                m.d.sync += bit_index.eq(0)
                m.d.comb += self.stream.ready.eq(0)
                m.d.comb += self.tx.eq(0)
                with m.If(uart_clk):
                    m.next = "Data out"

            with m.State("Data out"):
                m.d.comb += self.stream.ready.eq(0)
                m.d.comb += self.tx.eq(buffer.bit_select(bit_index, 1))

                # A baud period has elapsed
                with m.If(uart_clk):
                    # Clock out another bit if there are any left
                    with m.If(bit_index < 7):
                        m.d.sync += bit_index.eq(bit_index + 1)

                    with m.Else():
                        m.next = "Stop"

            with m.State("Stop"):
                m.d.comb += self.stream.ready.eq(0)
                m.d.comb += self.tx.eq(1)
                with m.If(uart_clk):
                    # when there is nothing more to transmit go to idle, immediately start the next packet otherwise
                    with m.If(self.stream.valid):
                        m.next = "Start"
                        m.d.comb += self.stream.ready.eq(1)
                        m.d.sync += buffer.eq(self.stream.payload)
                    with m.Else():
                        m.next = "Idle"

        return m

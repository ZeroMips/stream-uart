from amaranth import *
from amaranth.lib import stream,wiring
from amaranth.lib.wiring import In, Out

class UARTReceiver(wiring.Component):
    """
    A module for receiving bytes on a 8N1 UART at a configurable baudrate.
    Output is 8bit stream, input is rx pad.
    """

    stream: Out(stream.Signature(signed(8)))

    rx: In(1)

    def __init__(self, divider):
        super().__init__()

        self.divider = divider

    def elaborate(self, platform):
        m = Module()

        ctr_div = Signal(range(self.divider))
        buffer = Signal(8)
        bit_index = Signal(4)
        uart_clk = Signal()
        reset_ctr = Signal(5)
        rx_sync = Signal()
        rx_synced = Signal()

        m.d.sync += rx_sync.eq(self.rx)
        m.d.sync += rx_synced.eq(rx_sync)

        with m.If(self.stream.valid & self.stream.ready):
            m.d.sync += self.stream.valid.eq(0)

        with m.FSM():
            with m.State("Idle"):
                with m.If(~rx_synced):
                    m.d.sync += ctr_div.eq((self.divider - 1) >> 1)
                    m.next = "Start"

            with m.State("Start"):
                with m.If(rx_synced):
                    m.next = "Idle"
                with m.Elif(ctr_div == 0):
                    m.d.sync += ctr_div.eq(self.divider - 1)
                    m.d.sync += bit_index.eq(0)
                    m.next = "Data in"
                with m.Else():
                    m.d.sync += ctr_div.eq(ctr_div - 1)

            with m.State("Data in"):
                with m.If(ctr_div == 0):
                    m.d.sync += buffer.bit_select(bit_index, 1).eq(rx_synced)
                    m.d.sync += ctr_div.eq(self.divider - 1)
                    m.d.sync += bit_index.eq(bit_index + 1)
                    with m.If(bit_index == 7):
                        m.next = "Stop"
                with m.Else():
                    m.d.sync += ctr_div.eq(ctr_div - 1)

            with m.State("Stop"):
                with m.If(ctr_div == 0):
                    with m.If(rx_synced):
                        m.d.sync += self.stream.valid.eq(1)
                        m.d.sync += self.stream.payload.eq(buffer)
                        m.next = "Idle"
                    with m.Else():
                        m.next = "Error"
                with m.Else():
                    m.d.sync += ctr_div.eq(ctr_div - 1)

            with m.State("Error"):
                with m.If(rx_synced):
                    m.next = "Idle"

            return m
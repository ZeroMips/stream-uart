from amaranth import *

from amaranth_boards.icestick import ICEStickPlatform
from amaranth_boards.versa_ecp5 import VersaECP5Platform
from amaranth.lib import stream,wiring
from amaranth.lib.wiring import In, Out

from .tx import UARTTransmitter
from .rx import UARTReceiver


class Toplevel(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.submodules.uart_tx = uart_tx = UARTTransmitter(divider=217)
        m.submodules.uart_rx = uart_rx = UARTReceiver(divider=217)
        uart_resource = platform.request("uart", 0)
        m.d.comb += uart_resource.tx.o.eq(uart_tx.tx)
        m.d.comb += uart_rx.rx.eq(uart_resource.rx.i)

        wiring.connect(m, uart_rx=uart_rx.stream, uart_tx=uart_tx.stream)

        return m


def build_ice40():
    ICEStickPlatform().build(Toplevel())


def build_ecp5():
    VersaECP5Platform().build(Toplevel())


def build_gowin():
    TangNanoPlatform().build(Toplevel())

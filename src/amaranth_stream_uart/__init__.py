from amaranth import *

from amaranth_boards.icestick import ICEStickPlatform
from amaranth_boards.versa_ecp5 import VersaECP5Platform

from .tx import UARTTransmitter


class Toplevel(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.submodules.uart = uart = UARTTransmitter(divider=int(platform.default_clk_frequency//115200))
        m.d.comb += platform.request("uart", 0).tx.o.eq(uart.tx)

        return m


def build_ice40():
    ICEStickPlatform().build(Toplevel())


def build_ecp5():
    VersaECP5Platform().build(Toplevel())


def build_gowin():
    TangNanoPlatform().build(Toplevel())

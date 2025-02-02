from amaranth.sim import Simulator

from amaranth_stream_uart.tx import UARTTransmitter
from amaranth_stream_uart.rx import UARTReceiver
from amaranth.lib import stream,wiring
from amaranth.lib.wiring import In, Out
from amaranth import *

class HelloWorld(wiring.Component):
    o_stream: Out(stream.Signature(signed(8), always_valid=True))

    def elaborate(self, platform):
        m = Module()

        message = b"Hello world\n"
        m.submodules.memory = memory = \
            Memory(width=8, depth=len(message), init=message)

        rd_port = memory.read_port(domain="comb")
        with m.If(self.o_stream.ready):
            with m.If(rd_port.addr == memory.depth - 1):
                m.d.sync += rd_port.addr.eq(0)
            with m.Else():
                m.d.sync += rd_port.addr.eq(rd_port.addr + 1)

        character = Signal(8)
        m.d.comb += character.eq(rd_port.data)
        m.d.comb += self.o_stream.payload.eq(character)

        return m

class LoopPipeline(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.submodules.uart_tx = uart_tx = UARTTransmitter(divider=10)
        m.submodules.uart_rx = self.uart_rx = UARTReceiver(divider=10)

        m.submodules.helloworld = helloworld = HelloWorld()

        m.d.comb += self.uart_rx.rx.eq(uart_tx.tx)
        wiring.connect(m, helloworld.o_stream, uart_tx.stream)

        return m


def test():
    dut = LoopPipeline()

    async def stream_get(ctx, stream):
        ctx.set(stream.ready, 1)
        payload, = await ctx.tick().sample(stream.payload).until(stream.valid)
        ctx.set(stream.ready, 0)
        return payload

    async def testbench_input(ctx):
        for i in range(10000):
            await ctx.tick()

    async def testbench_output(ctx):
        message = b"Hello world\n"
        for char in message:
            payload = await stream_get(ctx, dut.uart_rx.stream)
            assert payload == char

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_testbench(testbench_input)
    sim.add_testbench(testbench_output)
#    sim.run()
    with sim.write_vcd("example1.vcd"):
        sim.run()

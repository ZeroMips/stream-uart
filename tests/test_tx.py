from amaranth.sim import Simulator

from amaranth_stream_uart.tx import UARTTransmitter

def test_tx():
    uart_tx = UARTTransmitter(divider=10)

    async def stream_put(ctx, stream, payload):
        ctx.set(stream.valid, 1)
        ctx.set(stream.payload, payload)
        await ctx.tick().until(stream.ready)
        ctx.set(stream.valid, 0)

    async def testbench(ctx):
        await stream_put(ctx, uart_tx.stream, 0xaa)
        await ctx.tick().until(uart_tx.stream.ready)
        for i in range(5):
            await ctx.tick()
        await stream_put(ctx, uart_tx.stream, 0x55)
        await stream_put(ctx, uart_tx.stream, 0x11)
        await ctx.tick().until(uart_tx.stream.ready)

    sim = Simulator(uart_tx)
    sim.add_clock(1e-6)
    sim.add_testbench(testbench)
    sim.run()
#    with sim.write_vcd("example1.vcd"):
#        sim.run()

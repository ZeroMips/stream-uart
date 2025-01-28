# Stream UART

This project provides a stream based UART implementation for the Amaranth HDL.

[stream]: https://amaranth-lang.org/docs/amaranth/latest/stdlib/stream.html#

The UART ist a simple 8N1 implementation, the baudrate can be configured with
a divisor.

## Installation

```shell
$ pipx install pdm
$ pdm install
$ pdm run build_ice40
$ pdm run build_ecp5
```

## License

This project is released under the [two-clause BSD license](LICENSE.txt). You are permitted to use it for open-source and proprietary designs provided that the copyright notice in the license file is reproduced.

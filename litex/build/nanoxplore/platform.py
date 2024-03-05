#
# This file is part of LiteX.
#
# Copyright (c) 2024 Miodrag Milanovic <mmicko@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

from litex.build.generic_platform import GenericPlatform
from litex.build.nanoxplore import impulse, beyond

# NanoXplorePlatform ----------------------------------------------------------------------------------

class NanoXplorePlatform(GenericPlatform):
    _bitstream_ext  = ".nxb"
    _jtag_support  = False

    _supported_toolchains = ["impulse", "beyond"]

    def __init__(self, device, *args, toolchain="impulse", **kwargs):
        GenericPlatform.__init__(self, device, *args, **kwargs)
        if toolchain == "impulse":
            self.toolchain = impulse.ImpulseToolchain()
        elif toolchain == "beyond":
            self._bitstream_ext = ".json"
            self.toolchain = beyond.BeyondToolchain()
        else:
            raise ValueError(f"Unknown toolchain {toolchain}")

    def get_verilog(self, *args, special_overrides=dict(), **kwargs):
        #so = dict(common.nanoxplore_special_overrides)
        #so.update(special_overrides)
        return GenericPlatform.get_verilog(self, *args,
            #special_overrides = so,
            attr_translate    = self.toolchain.attr_translate,
            **kwargs
        )

    def build(self, *args, **kwargs):
        return self.toolchain.build(self, *args, **kwargs)

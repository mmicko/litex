#
# This file is part of LiteX.
#
# Copyright (c) 2024 Miodrag Milanovic <mmicko@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import subprocess
import sys
from shutil import which

from migen.fhdl.structure import _Fragment

from litex.build.generic_platform import *
from litex.build import tools
from litex.build.yosys_nextpnr_toolchain import YosysNextPNRToolchain, yosys_nextpnr_args, yosys_nextpnr_argdict

# BeyondToolchain --------------------------------------------------------------------------

class BeyondToolchain(YosysNextPNRToolchain):
    attr_translate = {
        "keep": ("keep", "true"),
    }

    family     = "nanoxplore"
    synth_fmt  = "json"
    constr_fmt = "csv"
    pnr_fmt    = "json"
    is_himbaechel = True

    def __init__(self):
        super().__init__()

    def build(self, platform, fragment,
        **kwargs):
        self._synth_opts  = "-iopad"
        return YosysNextPNRToolchain.build(self, platform, fragment, is_himbaechel=True, **kwargs)

    def finalize(self):
        # Translate device to Nextpnr architecture/package
        self._pnr_opts     += f"--device=NG-ULTRA --vopt csv={self._build_name}.csv --debug"
        return YosysNextPNRToolchain.finalize(self)

    # IO Constraints (.csv) ------------------------------------------------------------------------
    def build_io_constraints(self):
        csv = []

        csv.append("#NxMap Ring configuration CSV export!")
        csv.append("#PADS!")
        csv.append("#HDL Name,#Location,#Standard,#Drive,#WeakTermination,#SlewRate,#Termination,#InputDelay Line,#OutputDelay Line,#Differential,#Terminationreference,#Turbo,#Signal Slope,#Output Capacity,#Register Path")
        for sig, pins, others, resname in self.named_sc:
            if len(pins) > 1:
                for i, p in enumerate(pins):
                    csv.append(sig + "[" + str(i) + "]"+ ","+p +",LVCMOS,2mA,PullUp,Medium,,0,0,False,VT,False,0,0,Auto")
            else:
                csv.append(sig + ","+ pins[0] +",LVCMOS,2mA,PullUp,Medium,,0,0,False,VT,False,0,0,Auto")
        #if self.named_pc:
        #    csv.append("\n\n".join(self.named_pc))

        csv.append("!")
        csv.append("#BANKS!")
        csv.append("#Bank Name,#Voltage,#Type")
        csv.append("IOB0,3.3V,Direct")
        csv.append("IOB1,3.3V,Direct")
        csv.append("IOB2,1.8V,Complex")
        csv.append("IOB3,1.8V,Complex")
        csv.append("IOB4,1.8V,Complex")
        csv.append("IOB5,1.8V,Complex")
        csv.append("IOB6,3.3V,Direct")
        csv.append("IOB7,3.3V,Direct")
        csv.append("IOB8,1.5V,Complex")
        csv.append("IOB9,1.5V,Complex")
        csv.append("IOB10,1.8V,Complex")
        csv.append("IOB11,1.8V,Complex")
        csv.append("IOB12,1.8V,Complex")
        csv.append("IOB13,1.8V,Complex")
        csv.append("!")
        csv.append("#CKGS!")
        csv.append("#HDL Name,#Location")
        tools.write_to_file(self._build_name + ".csv", "\n".join(csv))

def beyond_args(parser):
    toolchain_group = parser.add_argument_group(title="Beyond toolchain options")
    yosys_nextpnr_args(toolchain_group)

def beyond_argdict(args):
    return {
        **yosys_nextpnr_argdict(args)
    }

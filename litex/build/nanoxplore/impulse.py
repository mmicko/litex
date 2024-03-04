#
# This file is part of LiteX.
#
# Copyright (c) 2024 Miodrag Milanovic <mmicko@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import math
import subprocess
import datetime
from shutil import which

from migen.fhdl.structure import _Fragment

from litex.build.generic_platform import *
from litex.build.generic_toolchain import GenericToolchain
from litex.build import tools

# ImpulseToolchain -----------------------------------------------------------------------------

class ImpulseToolchain(GenericToolchain):
    attr_translate = {}

    def __init__(self):
        super().__init__()

    def finalize(self):
        self.parse_device()

    def build_io_constraints(self):
        return ("top.io")

    # Script ---------------------------------------------------------------------------------------

    def build_script(self):
        script = []

        script.append("from nxpython import *")
        #script.append("enableFeature(\"bitstream::Ifif\")")
        #script.append("enableFeature(\"bitstream::JSON\")")
        script.append("")
        script.append("prj = createProject()")
        # Set Device.
        script.append(f"prj.setVariantName(\"{self.platform.device}\")")

        script.append("prj.setOption('ManageUnconnectedOutputs', 'Ground')")
        script.append("prj.setOption('ManageUnconnectedSignals', 'Ground')")
        #script.append("prj.setOption('DisableDSPFullRecognition', 'Yes')")

        # Add IOs Constraints.
        flat_sc = []
        for name, pins, other, resource in self.named_sc:
            if len(pins) > 1:
                for i, p in enumerate(pins):
                    flat_sc.append((f"{name}[{i}]", p, other))
            else:
                flat_sc.append((name, pins[0], other))

        for name, pin, other in flat_sc:
            line = f"prj.addPad('{name}',{{'location': '{pin}', 'standard': 'LVCMOS', 'drive':'2mA'}})"
            #for c in other:
            #    if isinstance(c, IOStandard):
            #        line += f" IOSTANDARD = {c.name}; "
            #line += f"}}"
            script.append(line)

        if self.named_pc:
            script.extend(self.named_pc)

        # Add Sources.
        for f, typ, lib in self.platform.sources:
            script.append(f"prj.addFile('{f}')")

        # Elaborate.
        script.append(f"prj.setTopCellName('{self._build_name}')")

        # Perform PnR.
        script.append("prj.synthesize()")
        script.append("prj.place()")
        script.append("prj.route()")
        script.append(f"prj.generateBitstream('{self._build_name}.nxb')")

        # Generate .by.
        tools.write_to_file("build.py", "\n".join(script))

        return "build.py"

    def run_script(self, script):
            if which("nxpython") is None:
                msg = "Unable to find NanoXplore Impulse toolchain, please:\n"
                msg += "- Add Impulse toolchain to your $PATH."
                raise OSError(msg)

            if subprocess.call(["nxpython", script]) != 0:
                raise OSError("Error occured during NanoXplore's script execution.")

    def parse_device(self):
        device = self.platform.device

        devices = { "NG-ULTRA" }

        if device not in devices:
            raise ValueError("Invalid device {}".format(device))

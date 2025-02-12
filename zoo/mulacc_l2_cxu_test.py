## mulacc_l2_cxu_test.py: mulacc_l2_cxu (stateful serializable streaming L2 CXU) testbench

'''
Copyright (C) 2019-2023, Gray Research LLC.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import cocotb
from cocotb.clock import Clock
from cocotb.handle import SimHandleBase
from cocotb.queue import Queue
from cocotb.triggers import FallingEdge, RisingEdge, Timer

from enum import IntEnum
import random
import math

from cxu_li import *
from tb import TB
from imulacc import *

# testbench
@cocotb.test()
async def mulacc_l2_cxu_tb(dut):
    for frac in [1.0,0.9,0.1]:
        tb = TB(dut, Level.l2_stream)
        tb.resp_ready_frac = frac
        await tb.start()
        await IStateContext_tests(tb)
        await IMulAcc_tests(tb)
        await tb.idle()


# cocotb-test, follows Alex Forencich's helpful examples to sweep over dut module parameters

import os
import pytest
from cocotb_test.simulator import run

@pytest.mark.parametrize("latency", [0,1,2])
@pytest.mark.parametrize("states", [1,2,3])
@pytest.mark.parametrize("width", [32,64])

def test_mulacc_l2(request, latency, states, width):
    dut = "mulacc_l2_cxu"
    module = os.path.splitext(os.path.basename(__file__))[0]
    parameters = {}
    parameters['CXU_LATENCY'] = latency
    parameters['CXU_N_STATES'] = states
    parameters['CXU_STATE_ID_W'] = (states-1).bit_length()
    parameters['CXU_DATA_W'] = width
    sim_build = os.path.join(".", "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))

    run(
        includes=["."],
        verilog_sources=["common.svh", "cxu.svh", f"{dut}.sv", "cvt12_cxu.sv", "mulacc_cxu.sv", "shared.sv"],
        toplevel=dut,
        module=module,
        parameters=parameters,
        defines=['MULACC_L2_CXU_VCD'],
        extra_env={ 'CXU_N_STATES':str(states), 'CXU_LATENCY':str(latency), 'CXU_DATA_W':str(width) },
        sim_build=sim_build
    )

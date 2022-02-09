# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Created by kyoRan on 2021/12/29 22:00
"""

"""
"""
在xxx.sumocfg文件中加入，以下设置，可以运行直接开始
<gui_only>
    <start value="t"/>
    <quit-on-end value="e"/>
</gui_only>
"""

import os
import sys
import yaml
import time
import datetime

import traci
from sumolib import checkBinary

from src.SD_M3AP import SD_M3AP

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# sumo的可执行文件
is_show_gui = True  # 是否开启可视化
if not is_show_gui:
    sumoBinary = checkBinary('sumo')
else:
    sumoBinary = checkBinary('sumo-gui')

#
def createVehicle(t):
    # for i in range(0, 20, 5):
    if t == 1:
        # declaring the name(unique), route(from demand.route.xml), type of vehicle(declared in demand.route.xml),
        # depart time, and line
        traci.vehicle.add(
            'v%i' % 0, 'route_0', 'vType_HDV',
            depart="now", departLane="random",
            arrivalLane="E3_0"  # 最终目标车道
        )


if __name__ == '__main__':

    # 读取配置文件
    cfg = yaml.load(
        open("./cfg/cfg.yaml", 'r', encoding="utf-8").read(),
        Loader=yaml.FullLoader,
    )
    print(cfg)

    # 调用配置sumo文件
    sumoCmd = [
        sumoBinary, "-c", cfg["sumo"]["cfg-path"],
        "--lateral-resolution", str(cfg["sumo"]["lateral-resolution"]),  # 开启subline模式：https://sumo.dlr.de/docs/Simulation/SublaneModel.html
        "--step-length", str(cfg["sumo"]["step-length"]), # run the simulation using time steps of 10ms：https://sumo.dlr.de/docs/Simulation/Basic_Definition.html
        # "--default.action-step-length", "0.01",
    ]
    traci.start(sumoCmd, traceFile=f'{eval(cfg["sumo"]["log-path"])}.log')

    veh_ids_cp = []

    step = 0
    arch = SD_M3AP(cfg)
    while traci.simulation.getMinExpectedNumber() > 0:
        # time.sleep(0.01)
        # traci.simulationStep(step+1)
        traci.simulationStep()  # 一步是0.01s
        current_time = traci.simulation.getTime()
        print("当前仿真时间为：", current_time)

        try:

            # 0. 获取预备数据
            # 0.1 获取所有车的ID和Position
            all_vehicle_ids = traci.vehicle.getIDList()
            # all_vehicle_positions = [(i, traci.vehicle.getPosition(i)) for i in all_vehicle_ids]
            print(all_vehicle_ids)

            for one_veh_id in all_vehicle_ids:
                if one_veh_id not in veh_ids_cp:
                    # 若有新加入的车辆，先加入备份id
                    veh_ids_cp.append(one_veh_id)

            # 阶段1：Topology Construction
            arch.doStage1(all_vehicle_ids)
            #
            # 阶段2：
            arch.doStage2()
            #
            # 阶段3
            arch.doStage3(all_vehicle_ids)


            # createVehicle(step)
            # if step == 5:
            #     traci.vehicle.moveToXY("v0", -1, -1, 200, -7.111)
            #     print(traci.vehicle.getPosition("v0"))

                # traci.vehicle.moveToXY("flow_0.0", "E2", "E2_0", 200, 100)
                # for each_vehicle_id in all_vehicle_ids:
                #     traci.vehicle.setStop(
                #         "E1", each_vehicle_id
                #     )


        except traci.TraCIException as e:
            raise e

        finally:
            step += 1
    print("total veh:", len(veh_ids_cp))
    print("step:", step)
    print("time:", traci.simulation.getTime())
    traci.close()


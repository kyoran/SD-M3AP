# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Created by kyoRan on 2021/12/29 22:00

import time
import os, sys

import traci
from sumolib import checkBinary

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

def createVehicle():
    # for i in range(0, 20, 5):
    # if t == 1:
    # declaring the name(unique), route(from demand.route.xml), type of vehicle(declared in demand.route.xml),
    # depart time, and line
    print("id before:", traci.vehicle.getIDList())
    traci.vehicle.add(
        f'v{len(traci.vehicle.getIDList())+1}', 'route_0', 'vType_HDV',
        depart="now", departLane="free",
        arrivalLane="first"  # 最终目标车道
    )
    print("id after:", traci.vehicle.getIDList())


step = 0
vehs = []
if __name__ == '__main__':

    # sumo的可执行文件
    is_show_gui = True  # 是否开启可视化
    if not is_show_gui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # 调用配置sumo文件
    # 开启subline模式：https://sumo.dlr.de/docs/Simulation/SublaneModel.html
    sumoCmd = [sumoBinary, "-c", "./map/LR.sumocfg", "--lateral-resolution", "5"]
    traci.start(sumoCmd)
    # traci.start(sumoCmd, traceFile="./log.txt")


    while step < 1000:
        time.sleep(0.1)
        # traci.simulationStep(step+1)
        traci.simulationStep()
        current_time = traci.simulation.getTime()
        print("当前仿真时间为：", current_time)

        try:
            # 0. 新增车辆
            # createVehicle()

            # 获取所有车的ID
            all_vehicle_ids = traci.vehicle.getIDList()

            # 获取所有车的position
            all_vehicle_positions = [(i, traci.vehicle.getPosition(i)) for i in all_vehicle_ids]
            print(len(all_vehicle_ids), all_vehicle_positions)


        except traci.TraCIException as e:
            raise e

        finally:
            step += 1

    """
    在xxx.sumocfg文件中加入，以下设置，可以运行直接开始
    <gui_only>
        <start value="t"/>
        <quit-on-end value="e"/>
    </gui_only>
    """
    traci.close()
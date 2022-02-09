# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Created by kyoRan on 2022/1/1 21:42

import traci

class SD_M3AP():

    def __init__(self, cfg):
        self.cfg = cfg

        self.D_c = self.cfg["veh"]["D_c"]  # 通信距离
        self.F = self.cfg["veh"]["minGap"]  # 安全间距
        self.L = self.cfg["veh"]["length"]  # 车身长度
        self.step_len = self.cfg["sumo"]["step-length"]  # 时间间隔

        self.p_s = self.cfg["scenario"]["p_s"]
        self.p_c = self.cfg["scenario"]["p_c"]
        self.p_d = self.cfg["scenario"]["p_d"]
        self.p_e = self.cfg["scenario"]["p_e"]
        self.p_inf = self.cfg["scenario"]["p_inf"]

        self.CS = []    # 构造集合
        self.DS = []    # 决策集合
        self.vid2cs = {}    # 记录所有车辆对应的CS集合；已领导车id为key，val为列表，存放跟随车id
        self.vid2type = {}  # 记录每辆车的类型，L，F，HL（head leader），RL（rear leader），
        self.veh_ids_cp = []   # 记录所有车辆id的拷贝副本，用来判断是否有新车加入


    def doStage1(self, all_vehicle_ids,):
        """Topology Construction Algorithm"""
        # 判断是否有新加入的车辆
        for one_veh_id in all_vehicle_ids:
            if one_veh_id not in self.veh_ids_cp:
                # 若有新加入的车辆，先加入备份id
                self.veh_ids_cp.append(one_veh_id)
                # 加入已有的CS，或者是创建新的CS
                if len(self.CS) == 0:   # 如果为空，则该车为领导车
                    self.CS.append(one_veh_id)
                    self.vid2type[one_veh_id] = "L"
                else:
                    self.CS.append(one_veh_id)
                    self.vid2type[one_veh_id] = "F"

            # 按原速度继续行驶
            one_veh_speed = traci.vehicle.getSpeed(one_veh_id)
            # print("one_veh_id:", one_veh_id, "one_veh_speed:", one_veh_speed, "bf position:", traci.vehicle.getPosition(one_veh_id))

            # 由于这边不涉及横向控制器，速度是纵向的
            one_veh_position_long, one_veh_position_lat = traci.vehicle.getPosition(one_veh_id)    # 之前的位置
            # print("bf one_veh_position_long:", one_veh_position_long)
            one_veh_position_long = one_veh_position_long + one_veh_speed * self.step_len     # 更新后的位置
            # print("af one_veh_position_long:", one_veh_position_long)
            # 移动车辆前进
            traci.vehicle.moveToXY(one_veh_id, -1, -1, one_veh_position_long, one_veh_position_lat)
            # print("one_veh_id:", one_veh_id, "one_veh_speed:", one_veh_speed, "af position:", traci.vehicle.getPosition(one_veh_id))

            # 如果车辆的纵向位置超出了dead_end，则删除该车
            if one_veh_position_long > self.p_inf:
                traci.vehicle.remove(one_veh_id)    # 从traci.vehicle.getIDList()里面删除了

        # 判断CS中的领导车是否已经超过了D_c
        # if len(self.CS) != 0 and traci.vehicle.getPosition(self.CS[0])[0] > self.D_c:
        # 判断CS中的领导车是否超过了p_c
        if len(self.CS) != 0 and traci.vehicle.getPosition(self.CS[0])[0] > self.p_c:
            self.DS.append(self.CS.copy())
            self.CS.clear()
        print(self.DS)

    def doStage2(self):
        """Adaptive Platoon Selection Algorithm"""
        if len(self.DS) != 0:
            if traci.vehicle.getPosition(self.DS[0][0])[0] > self.p_d:
                # maximum allowable capacity
                # 第一个CS的第1辆车  最后一个，这个是最最最优的，每个CS中间的位置都考虑了
                # n_s = (traci.vehicle.getPosition(self.DS[0][0])[0] + traci.vehicle.getPosition(self.DS[-1][-1])[0]) \
                #       / (self.L + self.F)
                # 这个是次优的，每个CS中间的位置没考虑
                n_s = 0
                for one_CS in self.DS:
                    n_s += (traci.vehicle.getPosition(one_CS[0])[0]+traci.vehicle.getPosition(one_CS[-1])[0])/(self.L + self.F)
                n_s = n_s / len(self.DS)
                # average cluster capacity
                n_head = sum([len(each_CS) for each_CS in self.DS]) / len(self.DS)

                print("n:", n_s, n_head)

    def doStage3(self, all_vehicle_ids):
        pass


        # DS中的CS，如果领导车CS[0]不在all_vehicle_ids里面，则删除这个CS
#!/usr/bin/env python
# coding=utf-8
'''
Author: Li Yuhao
Date: 2022-05-13 14:42:55
LastEditTime: 2022-05-16 18:01:42
LastEditors: your name
Description: 
FilePath: \\PWPS\\PWPS\\Config.py
'''

CP_SAT_SOLVER = "CP_SAT_SOLVER" # ortools中的 cp sat model
LP_SOLVER = "LP_SOLVER" # ortools中的linear solver
SCIP_SOLVER = "SCIP_SOLVER"




IDLE = "init" # 初始化
OPTIMAL = "optimal" # 求出最优解
FEASIBLE = "feasible" # 可行解
INFEASIBLE = "infeasible" # 无解
NOT_SOLVED = "not_solved" # 未计算完
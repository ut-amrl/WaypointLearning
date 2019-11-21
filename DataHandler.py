import numpy as np
import subprocess
import csv
import os
import random

class DataHandler():
    def __init__(self, gamma, optimal_data, eval_data, need_features):
        self.gamma = gamma
        self.sol_file = optimal_data
        self.eval_file = eval_data
        self.need_features = need_features
    
    def GetCost(self, T_opt, T_col, T):
        return (T + self.gamma*T_col)/T_opt - 1
    
    def getSolutionCost(self, file):
        f = open(file, "r")
        line = f.readline()
        f.close()
        elems = line.split(',')
        T_opt = float(elems[0])
        T_col = float(elems[-1])
        return T_opt, self.GetCost(T_opt, T_col, T_opt)
    
    def getInitialWaypoint(self, file):
        f = open(file, "r")
        for i in range(3):
            line = f.readline()
        f.close()
        elems = line.split(',')
        wx = float(elems[1])
        wy = float(elems[2])
        wvx = float(elems[3])
        wvy = float(elems[4])
        return np.array([wx,wy,wvx,wvy])
    
    def getSolutionFeatures(self, file):
        features = [];
        with open(file) as f:
            line = f.readline()
            elems = line.split(',')
            for el in elems:
                features += [float(el)]
        return np.array(features)
    
    def getOptimalSolution(self, dx, v0x, vf, obs_t, obs_offset):
        cmd = "./bin/solve {} {} {} {} {} {} {} {}".format(self.sol_file,
            round(dx[0], 3), round(dx[1], 3), round(v0x, 3),
            round(vf[0], 3), round(vf[1], 3), 
            round(obs_t, 3), round(obs_offset, 3))
        try:
            status = subprocess.call(cmd, shell=True, timeout=1)
        except:
            print("timeout on command:")
            print(cmd)
            return float('inf'), []
        if status > 0:
            return float('inf'), []
        
        T, C = self.getSolutionCost(self.sol_file)
        features = []
        if (self.need_features):
            features = self.GetSolutionFEatures(self.sol_file)
            features = np.hstack([dx, v0x, vf, obs_t, obs_offset, features])
        return T, C, self.sol_file, features
        
    def Evaluate(self, dx, v0x, vf, wpt, obs_t, obs_offset):
        cmd = "./bin/eval {} {} {} {} {} {} {} {} {} {} {} {}".format(
            self.eval_file,round(dx[0],3),round(dx[1],3),round(v0x, 3),
            round(vf[0],3),round(vf[1],3),round(wpt[0],3),round(wpt[1],3),
            round(wpt[2],3),round(wpt[3],3),round(obs_t,3),round(obs_offset,3))
        try:
            status = subprocess.call(cmd, shell=True, timeout=1)
        except:
            print("timeout on command:")
            print(cmd)
            return float('inf'), float('inf')
            
        if status > 0:
            return float('inf'), float('inf')
        
        f = open(self.eval_file, "r")
        line = f.readline()
        f.close()
        elems = line.split(',')
        T = float(elems[0])
        T_col = float(elems[1])
        return T, T_col
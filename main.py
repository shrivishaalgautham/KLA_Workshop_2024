import json
from collections import defaultdict
import copy
import sys

class Wafer:
    def __init__(self,type,steps,time):
        self.type = type
        self.steps = steps
        self.done = [False] * len(steps)
        self.count = 0
        self.last_time = 0
        self.time = time

class Machine:
    def __init__(self,mach_id,step_id,initial_para,fluc,num):
        self.mach_id = mach_id
        self.step_id = step_id
        self.initial_para = initial_para
        self.fluc = fluc
        self.num = num
        self.endtime = 0
    
class Step:
    def __init__(self,id,parameters,dependency,machines):
        self.id = id
        self.parameters = parameters
        self.dependecy = dependency
        self.machines = machines
with open(r"C:\Users\csuser\Desktop\Wafer processing optimization\Input\Milestone3a.json") as file:
    data = json.load(file)

steps = {}
for mach in data['machines']:
    temp = Machine(mach['machine_id'],mach['step_id'],mach['initial_parameters'],mach['fluctuation'],mach['n'])
    if mach['step_id'] in steps.keys():
        steps[mach['step_id']].append(temp)
    else:
        steps[mach['step_id']] = [copy.deepcopy(temp)]
'''for i in range(len(data['steps'])):
    for j in data['steps'][i]:
        depe'''

machines_map = {}
for step in data['steps']:
    temp = Step(step['id'],step['parameters'],step['dependency'],steps[step['id']])
    machines_map[step['id']] = temp
wafers = []

print(machines_map['S2'].machines)

for wafer in data['wafers']:
    for i in range(wafer['quantity']):
        wafers.append(Wafer(wafer['type'] + '-' +str(i + 1),list(wafer['processing_times'].keys()),list(wafer['processing_times'].values())))
schedule = {'schedule':[]}

completed = 0
n = len(wafers)

def perform(type,step,dur,last,machine):
    start = max(machine.endtime,last)
    machine.endtime = start + dur
    schedule['schedule'].append({'wafer_id':type,'step':step,'start_time':start,'machine':machine.mach_id,'end_time':machine.endtime})
    return machine.endtime

def find_min(wafer):
    min_step = None
    min_time = sys.maxsize
    min_mach = None
    for i in range(len(wafer.steps)):
        if wafer.done[i]:
            continue
        for mach in machines_map[wafer.steps[i]].machines:
            if mach.endtime < min_time:
                min_time = mach.endtime
                min_step = i
                min_mach = mach
    wafer.done[min_step] = True
    return min_step,min_mach

'''while completed < n:

    for wafer in wafers:
        min_time = 0
        min_step = 0
        for i in range(len(wafer.steps)):
            if not wafer.done[i]:
                wafer.last_time = perform(wafer.type,wafer.steps[i],wafer.time[i],wafer.last_time)
                wafer.done[i] = True
                wafer.count += 1
                break
            print(completed)
        
        if wafer.count == len(wafer.steps):
            completed += 1'''

while completed < n:
    for wafer in wafers:
        if wafer.count == len(wafer.steps):
            completed += 1
            continue
        i,mach = find_min(wafer)
        wafer.last_time = perform(wafer.type,wafer.steps[i],wafer.time[i],wafer.last_time,mach)
        wafer.count += 1
with open("output3a.json","w") as file:
    json.dump(schedule,file,ensure_ascii=False,allow_nan=False,indent=4)
            
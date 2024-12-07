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
    def __init__(self,mach_id,step_id,cooldown,initial_para,fluc,num):
        self.mach_id = mach_id
        self.step_id = step_id
        self.cooldown = cooldown
        self.initial_para = initial_para
        self.current_para = initial_para
        self.processed = 0
        self.fluc = fluc
        self.num = num
        self.endtime = 0
    
class Step:
    def __init__(self,id,parameters,dependency,machines):
        self.id = id
        self.parameters = parameters
        self.dependecy = dependency
        self.machines = machines

def topologicalSorting(dependency,indegree,no_dependency_step):

    stack = []
    queue = copy.deepcopy(no_dependency_step)

    while queue:
        temp = queue.pop()
        stack.append(temp)
        if temp not in dependency.keys():
            continue
        for i in dependency[temp]:
            indegree[i] -= 1
            if indegree[i] == 0:
                queue.insert(0,i)
    return stack




with open(r"C:\Users\csuser\Desktop\Wafer processing optimization\Input\Milestone5b.json") as file:
    data = json.load(file)

steps = {}
for mach in data['machines']:
    temp = Machine(mach['machine_id'],mach['step_id'],mach['cooldown_time'],mach['initial_parameters']["P1"],mach['fluctuation']["P1"],mach['n'])
    if mach['step_id'] in steps.keys():
        steps[mach['step_id']].append(temp)
    else:
        steps[mach['step_id']] = [copy.deepcopy(temp)]

dependency_list = {}
indegree = {}

no_dependency_steps = []

machines_map = {}
for step in data['steps']:
    if step['dependency'] is None:
        indegree[step['id']] = 0
        no_dependency_steps.append(step['id'])
    else:
        for dependent in step['dependency']:
            if dependent not in dependency_list.keys():
                dependency_list[dependent] = []
            dependency_list[dependent].append(step['id'])
            if step['id'] not in indegree.keys():
                indegree[step['id']] = 1
            else:
                indegree[step['id']] += 1
    temp = Step(step['id'],step['parameters']['P1'],step['dependency'],steps[step['id']])
    machines_map[step['id']] = temp

sorted_steps = topologicalSorting(dependency_list,indegree,no_dependency_steps)

wafers = []

for wafer in data['wafers']:
    for i in range(wafer['quantity']):
        wafers.append(Wafer(wafer['type'] + '-' +str(i + 1),list(wafer['processing_times'].keys()),list(wafer['processing_times'].values())))
schedule = {'schedule':[]}

completed = 0
n = len(wafers)

def check_para(mach,step):
    step_obj = machines_map[step]
    if mach.current_para < step_obj.parameters[0] or mach.current_para > step_obj.parameters[1]:
        mach.endtime += mach.cooldown
        mach.current_para = mach.initial_para
test = []
def perform(type,step,dur,last,machine):
    start = max(machine.endtime,last)
    machine.endtime = start + dur
    schedule['schedule'].append({'wafer_id':type,'step':step,'start_time':start,'machine':machine.mach_id,'end_time':machine.endtime})
    test.append([type,step,machine.mach_id,machine.current_para,machine.processed,machine.endtime])
    machine.processed += 1
    if machine.processed == machine.num:
        machine.current_para += machine.fluc
        machine.processed = 0
        check_para(machine,step)

    return machine.endtime

def find_min(wafer):
    min_step = None
    min_time = sys.maxsize
    min_mach = None
    for i in range(len(wafer.steps)):
        if wafer.done[i]:
            continue
        flag = 0
        if wafer.steps[i] not in no_dependency_steps:
            for k in range(sorted_steps.index(wafer.steps[i]) - 1, -1, -1):
                print(no_dependency_steps)
                try:
                    index = wafer.steps.index(sorted_steps[k])
                except:
                    continue
                if not wafer.done[index]:
                    flag = 1
            if flag == 1:
                continue
        for mach in machines_map[wafer.steps[i]].machines:
            if mach.endtime < min_time:
                min_time = mach.endtime
                min_step = i
                min_mach = mach
    wafer.done[min_step] = True
    return min_step,min_mach

while completed < n:
    for wafer in wafers:
        if wafer.count == len(wafer.steps):
            completed += 1
            continue
        index,mach = find_min(wafer)
        wafer.last_time = perform(wafer.type,wafer.steps[index],wafer.time[index],wafer.last_time,mach)
        wafer.count += 1

with open("output5b.json","w") as file:
    json.dump(schedule,file,indent=4)

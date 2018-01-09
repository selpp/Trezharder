'''
    Profiler file used to monitor memory usage and time used for 
    specified section of the code.
    
    TimeProfiler:
        Just put a @time_profiled(name, parent) decorator on the methods you wish to track
        
        e.g: @time_profiled("entity_draw", "draw")
        e.g: @time_profiled("backpropagation", "ai_training")
        
        The first argument is the custom_name of the profiler section,
        The second argument is the parent of the profiler section.
        
        In the earlier example, "entity_draw" is a sub part of "draw", 
        there could be other parts such as "map_draw" or "debug_draw"
        
        If there is no parent, the profiler section is considered os a root section 
        
        Use profiler.show_time_graph to pop a real-time graph of the profiler
        
    MemoryProfiler:
        Just put a @memory_profiled decorator on the classes you wish to track
        
        
'''

from time import time 
from time import sleep
from multiprocessing import Queue
from threading import Thread
from multiprocessing import Value
from functools import wraps
from openpyxl.chartsheet import custom
import matplotlib.pyplot as plt

class MemoryProfiler:
     
    instance = None 

    @staticmethod
    def initiate():
        if(MemoryProfiler.instance != None):
            return
        
        MemoryProfiler.instance = MemoryProfiler()
     
    def __init__(self):
        pass


class ProfilerTreeNode():
    
    def __init__(self, name):            
        self.name   = name
        self.is_root = False
        self.children = []
        
    def append_child(self, name):
        self.children.append(ProfilerTreeNode(name))
        
    def get_children_as_names(self):
        l = []
        for c in self.children:
            l.append(c.name)
            
        return l       


class TimeProfiler:
    instance = None
    default_element_name = "root"
    
    @staticmethod
    def initiate():
        if(TimeProfiler.instance != None):
            return
        
        TimeProfiler.instance = TimeProfiler()        
    

    def __init__(self):
        self.processQueue = Queue(50) #maxsize is mandatory to avoid system crash in case of Profiler failure
        self.times = {}
        self._show_chart = Value('b')
        self._chart_selected_element = self.default_element_name
        
        self.tree = ProfilerTreeNode(self.default_element_name) #root node
        self.tree.is_root = True
        
        t = Thread(target=self.profiler_treatement_target)
        t.setDaemon(True)
        t.start()
    
    def push(self, func, t, custom_name, parent):
        self.processQueue.put((func, t, custom_name, parent))
        
    def get_tree_element_by_name(self, name):
        if(name == None or name == self.default_element_name):
            return self.tree
        return self._get_tree_element_recursive(self.tree, name)
        
    def _get_tree_element_recursive(self, current, name):
        if(current.name == name):
            return current
        
        for child in current.children:
            o = self._get_tree_element_recursive(child, name)
            if(o != None):
                return o
            
        return None
    
    def get_children(self, name):
        return self.get_tree_element_by_name(name).get_children_as_names()
    
    def append_children(self, parent, name):
        self.get_tree_element_by_name(parent).append_child(name)
            
        
    def profiler_treatement_target(self):
        print("Started time profiler")
        
        while(True):
            element = self.processQueue.get()
            
            func, t, custom_name, parent = element
            
            self.ensure_tree(custom_name, parent)
            
            self._update_element(custom_name, t)  #element update
            self._update_element(parent, t, 0)    #parent update
            
     
    def ensure_tree(self, name, parent):
        if(name in self.times.keys()):
            return
                
        if(self.get_tree_element_by_name(parent) == None):
            self.append_children(None, parent)
        
        if(self.get_tree_element_by_name(name) == None):
            self.append_children(parent, name)
                        
    def get_moy(self, name = None):
        return self.get_total_time(name) / self.get_call_count(name)
            
    def get_total_time(self, name = None):
        return self._get_element(name, 0)
       
    def get_call_count(self, name = None):
        return self._get_element(name, 1)
        
    def _get_element(self, name, i):
        if(name is None):
            name = self.default_element_name
        
        if(not name in self.times):
            raise 0
        
        return self.times[name][i] 
                            
    def _update_element(self, name, t, c = 1):
        if(name is None):
            name = self.default_element_name
        
        if(not name in self.times):
            self.times[name] = [0.0, 0]            
        
        self.times[name][0] += t
        self.times[name][1] += c
        
    def show_chart(self, value = True):
        self._show_chart.value = value
        if(value):
            th = Thread(target = self._chart_refresh_traget)
            th.setDaemon(True)
            th.start()
        
    def get_totals(self, element = None, factor = 1):
        if(element is None):
            element = self.default_element_name
        
        elements = self.get_children(element)
        
        t = []
        for v in elements: #TODO fetch from elemen with children
            t.append(self.times[v][0]*factor)
            
        return t
    
    def _chart_refresh_traget(self):
        plt.ion()
        fig1, ax1 = plt.subplots()
        #ax1.axis('equal')  
        
        plt.show()
        while(self._show_chart.value):
            # Pie chart, where the slices will be ordered and plotted counter-clockwise:
            labels = self.get_children(self._chart_selected_element)
            sizes = self.get_totals(self._chart_selected_element, 10)
            if(len(sizes) == 0):
                continue
        
            ax1.clear()
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            plt.pause(0.01)
            fig1.canvas.draw_idle()
        
            
'''
def memory_profiled(cls):
    class Wrapper(object):
    
        def __new__(cls):
            print("new")
            return __loader__.__new__(cls)
        
    return Wrapper
'''

def time_profiled(custom_name, parent = None):
    def _time_profiled(func):
        def wrapper(*args, **kwargs):
            start = time()
            o = func(*args)
            end = time()
            t = end - start
            try:
                TimeProfiler.instance.push(id(func), t, custom_name, parent)
            except:
                pass
            
            return o
        return wraps(func)(wrapper)
    return _time_profiled

def show_time_chart(value = True):
    TimeProfiler.instance.show_chart(value)

TimeProfiler.initiate()
#MemoryProfiler.initiate() #not implemented


if __name__ == "__main__":
    
    @time_profiled("method1")
    def method1():
        sleep(0.001)
    
    @time_profiled("method2")    
    def method2(i):
        sleep(0.001 * i)
        #method3()
        
    @time_profiled("method3", "method2")    
    def method3():
        sleep(0.001)
        #method1()       
    
    show_time_chart()
    
    i = 0
    while(i < 10000):
        method2(i)
        method1()
        
        i += 1
        
    print(TimeProfiler.instance.get_total_time())
    print(TimeProfiler.instance.get_moy("method1"))
    print(TimeProfiler.instance.get_moy("method2"))
    
        
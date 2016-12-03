from flask import abort, Flask, make_response, jsonify, Response, request, url_for
from flask_restful import Api, reqparse, Resource, fields, marshal
import glob
import os
import sys
from threading import Thread
import time
import math
import traceback
from CustomConfigObj import CustomConfigObj

if hasattr(sys, "frozen"): #we're running compiled with py2exe
    AppPath = sys.executable
else:
    AppPath = sys.argv[0]
APP_NAME = "flaskServer"
if "backpackServer.py" in sys.argv[0]:
    app = Flask(__name__, static_url_path='', static_folder='../../../../js/backpack/src/')
else:   # running executable
    app = Flask(__name__, static_url_path='', static_folder='webGUI/')
     
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))
api = Api(app)
app.config.update(SEND_FILE_MAX_AGE_DEFAULT=0)

class JSON_Remote_Procedure_Error(RuntimeError):
    pass
    
class BatteryVoltageMonitor(object):
    def __init__(self):
        self.old_voltage = 0
        self.count = 0
        
    def checkValue(self, voltage):
        if (self.old_voltage - self.voltageThreshold) * (voltage - self.voltageThreshold) < 0:
            self.count = 1
            ret = (self.old_voltage < self.voltageThreshold)
        elif voltage < self.voltageThreshold:
            ret = True if self.count >= self.pointsTriggerAlarm else False
            self.count += 1
        elif voltage > self.voltageThreshold:
            if self.count == 0:
                ret = False
            elif self.count == self.pointsCancelAlarm:
                ret = False
                self.count = 0
            else:
                ret = True
                self.count += 1
        self.old_voltage = voltage
        return ret
        
        
class AlarmRegister(object):
    def __init__(self):
        self.register = 0x00000000
        self.alarmMask = {
            "battery_voltage": 0x00000001
        }
        
    def setAlarm(self, alarmName, value):
        if value:
            self.register |= self.alarmMask[alarmName]
        else:
            self.register &= ~self.alarmMask[alarmName]

class BackpackServer(object):
    def __init__(self, configFile, simulation):
        if os.path.exists(configFile):
            self.config = CustomConfigObj(configFile)
        else:
            print "Configuration file not found: %s" % configFile
            sys.exit(1)
        self.simulation = simulation
        self.battery_monitor = BatteryVoltageMonitor()
        self.alarmStatus = AlarmRegister()
        self.driver = None
        self.inst_mgr = None
        self.logger = None
    
    def loadConfig(self):
        self.setup = {'host' : self.config.get('Setup', "Host_IP", "0.0.0.0"),
                      'port' : self.config.getint('Setup', "Port", 3000),
                      'debug' : self.config.getboolean('Setup', "Debug_Mode", True)}
        self.userlog = self.config.get('Setup', "UserLog_Files")
        self.battery_monitor.pointsTriggerAlarm = self.config.getint("BatteryMonitor", "Points_Trigger_Alarm", 10)
        self.battery_monitor.pointsCancelAlarm = self.config.getint("BatteryMonitor", "Points_Cancel_Alarm", 3)
        self.battery_monitor.voltageThreshold = self.config.getfloat("BatteryMonitor", "Voltage_Threshold", 18.9)
        if self.simulation:
            self.simulation_dict = {}
            if self.config.has_option('Simulation', 'Replay_Data'):
                replay_data = self.config.get('Simulation', 'Replay_Data', '')
                self.simulation_dict["Files"] = replay_data.split(',')
                for f in self.simulation_dict["Files"]:
                    if not os.path.exists(f):
                        raise Exception("Data file not found: %s" % f)
                self.simulation_dict["CurrentFile"] = self.simulation_dict["Files"][0]
                self.simulation_dict["CurrentFileIndex"] = 0
                fp = open(self.simulation_dict["Files"][0], 'r')
                self.simulation_dict["CurrentFileHeader"] = fp.readline().split()
                self.simulation_dict["CurrentFileHandle"] = fp
            else:
                self.simulation_dict["CH4"] = self.config.get('Simulation', 'CH4', '')
                self.simulation_dict["CO2"] = self.config.get('Simulation', 'CO2', '')
                self.simulation_dict["H2O"] = self.config.get('Simulation', 'H2O', '')
                self.simulation_dict["Battery"] = self.config.get('Simulation', 'BatteryVoltage', '')
                self.simulation_env = {func: getattr(math, func) for func in dir(math) if not func.startswith("__")}
                self.simulation_max_index = self.config.getint('Simulation', 'Max_Index', 100)
                self.simulation_index_increment = 1
    
    def getData(self, startRow):
        if self.simulation:
            return self.simulate_data(startRow)
        name = self._getFileName()
        if name is not None:
            fp = file(name,'rb')
        else:
            return {'filename':''}
        fp.seek(0,0)
        header = fp.readline().split()
        data = dict(EPOCH_TIME=[],CH4=[],CO2=[],H2O=[])
        lineLength = fp.tell()
        fp.seek(0,2)
        if fp.tell() < startRow*lineLength:
            startRow = 1
        fp.seek(startRow*lineLength,0)
        for line in fp:
            if len(line) != lineLength:
                break
            vals = line.split()
            if len(vals)!=len(header):
                break
            for col,val in zip(header,vals):
                if col in data: 
                    data[col].append(float(val))
                if col == "Battery_Voltage":
                    self.alarmStatus.setAlarm("battery_voltage", self.battery_monitor.checkValue(float(val)))
            startRow += 1
        fp.close()
        result = {"next_row" : startRow,
                  "file_name" :  name,
                  "alarm" : self.alarmStatus.register,
                  "data" : data}
        return result
        
    def _getFileName(self):
        try:
            year = max(os.listdir(self.userlog))
            month = max(os.listdir(os.path.join(self.userlog, year)))
            day = max(os.listdir(os.path.join(self.userlog, year, month)))
            names = sorted(glob.glob(os.path.join(self.userlog, year, month, day, "*.dat")))
            return names[-1]
        except:
            return None
            
    def simulate_data(self, startRow):
        if "Files" in self.simulation_dict: # replay data from files
            data = dict(EPOCH_TIME=[],CH4=[],CO2=[],H2O=[])
            fp = self.simulation_dict["CurrentFileHandle"]
            buf = fp.readline()
            while len(buf) == 0:    # reach the end of file
                fp.close()
                self.simulation_dict["CurrentFileIndex"] += 1
                if self.simulation_dict["CurrentFileIndex"] >= len(self.simulation_dict["Files"]):
                    self.simulation_dict["CurrentFileIndex"] = 0
                self.simulation_dict["CurrentFile"] = self.simulation_dict["Files"][self.simulation_dict["CurrentFileIndex"]]
                fp = open(self.simulation_dict["CurrentFile"], "r")
                self.simulation_dict["CurrentFileHeader"] = fp.readline().split()
                self.simulation_dict["CurrentFileHandle"] = fp
                buf = fp.readline()
            vals = buf.split()
            for col, val in zip(self.simulation_dict["CurrentFileHeader"], vals):
                if col == "Battery_Voltage":
                    self.alarmStatus.setAlarm("battery_voltage", self.battery_monitor.checkValue(float(val)))
                elif col in data:
                    data[col].append(float(val))
            result = {"next_row" : -1,
                      "file_name" :  self.simulation_dict["CurrentFile"],
                      "alarm" : self.alarmStatus.register,
                      "data" : data}
        else:   # calculate data from predefined functions
            data = {}
            for k in self.simulation_dict:
                if k == "Battery":
                    self.alarmStatus.setAlarm("battery_voltage", 
                        self.battery_monitor.checkValue(self.run_simulation_expression(self.simulation_dict[k], startRow)))
                else:
                    data[k] = [self.run_simulation_expression(self.simulation_dict[k], startRow)]
            data["EPOCH_TIME"] = [time.time()]
            if startRow == self.simulation_max_index:
                self.simulation_index_increment = -1
            elif startRow == 1:
                self.simulation_index_increment = 1
            result = {"next_row" : startRow + self.simulation_index_increment,
                      "file_name" :  "simulation",
                      "alarm" : self.alarmStatus.register,
                      "data" : data}
        return result
        
    def run_simulation_expression(self, expression, startRow):
        if len(expression) > 0:
            self.simulation_env["x"] = startRow
            exec "simulation_result=" + expression in self.simulation_env
            return self.simulation_env["simulation_result"]
        else:
            return 0.0
    
    def act_on_command(self, command):
        if command == "shutdown":
            if self.simulation:
                print "Shut down analyzer per request of the user."
            else:
                self.inst_mgr.INSTMGR_ShutdownRpc(2)  # Turn Off Analyzer in Current State
        elif command == "restartUserlog":
            if self.simulation:
                print "Restart userlog per request of the user."
            else:
                self.logger.startUserLogs(["DataLog_User_Minimal"], True)
        elif command == "about":
            if self.simulation:
                print "Version information requested."
                return {'host release': 'mobile-2.4.2.24 (3102146b)', 
                    'config - app version no': '1.0.5', 
                    'config - instr version no': '9fa0b2b'}
            else:
                return self.driver.allVersions()
    
    def run(self):
        self.loadConfig()
        #self.startServer()
     
HELP_STRING = \
"""\
backpackServer.py [-h] [-c<FILENAME>]

Where the options can be a combination of the following:
-h              Print this help.
-c              Specify a different config file.  Default = "./backpackServer.ini"
-s              Simulation mode.
"""

def PrintUsage():
    print HELP_STRING
def HandleCommandSwitches():
    import getopt
    shortOpts = 'hc:s'
    longOpts = ["help"]
    try:
        switches, args = getopt.getopt(sys.argv[1:], shortOpts, longOpts)
    except getopt.GetoptError, data:
        print "%s %r" % (data, data)
        sys.exit(1)

    #assemble a dictionary where the keys are the switches and values are switch args...
    options = {}
    for o, a in switches:
        options[o] = a

    if "/?" in args or "/h" in args:
        options["-h"] = ""

    executeTest = False
    if "-h" in options or "--help" in options:
        PrintUsage()
        sys.exit()
    
    #Start with option defaults...
    configFile = os.path.dirname(AppPath)  + "backpackServer.ini"

    if "-c" in options:
        configFile = options["-c"]
        print "Config file specified at command line: %s" % configFile
    simulation = True if "-s" in options else False
    
    return (configFile, simulation)    
    
backpack_server = BackpackServer(*HandleCommandSwitches())
            
class SeriesAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('startRow', type=int, required=True)
        request_dict = parser.parse_args()
        print request_dict
        return backpack_server.getData(request_dict['startRow'])
        
class ControlAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('command', type=str, required=True)
        request_dict = parser.parse_args()
        print "CAPIget:",request_dict
        return backpack_server.act_on_command(request_dict['command'])
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('command', type=str, required=True)
        request_dict = parser.parse_args()
        backpack_server.act_on_command(request_dict['command'])
        print "CAPIpost:", request_dict
        return {}
            
if __name__ == '__main__':
    backpack_server.run()
    api.add_resource(SeriesAPI, '/api/v1.0/series', endpoint='series')
    api.add_resource(ControlAPI, '/api/v1.0/control', endpoint='control')
    app.run(**backpack_server.setup)

from .common import *
from .ha_interface import HAInterface
#from pytomation.devices import State
'''
http://sourceforge.net/apps/mediawiki/mochad/index.php?title=Mochad_Reference
'''

class Mochad(HAInterface):
    
    VERSION='0.2.2'
        
#     def _init(self, *args, **kwargs):
#         super(Mochad, self)._init(*args, **kwargs)

    def _readInterface(self, lastPacketHash):
        """
    	01/27 23:41:23 Rx RF HouseUnit: A3 Func: Off
    	0     1        2  3  4          5  6     7 
    	01/27 23:48:23 Rx RF HouseUnit: A1 Func: On
    	12/07 20:49:37 Rx RFSEC Addr: C6:1B:00 Func: Motion_alert_MS10A
    	0     1        2  3     4     5        6     7
	    """
        
        responses = self._interface.read()
        if len(responses) == 0:
            return
        
        response = responses.split('\n')
        if len(response) == 1 :
            self._logger.debug('responses> ' + responses)
            data=responses.split(' ')
            #date=data[0]
            #time=data[1]
            direction=data[2]
            method=data[3]
            ua=data[4]
            addr=data[5]
            #func junk
            
            if direction=="Rx":
                func=data[7].strip().rsplit('_',1)[0] #removing _devicemodel
        
                if func=="On":
                    self._onCommand(command=Command.ON,address=addr)
                elif func=="Off":
                    self._onCommand(command=Command.OFF,address=addr)
                elif func=="Motion_alert":
                    self._onCommand(command=Command.MOTION,address=addr)
                elif func=="Motion_normal":
                    self._onCommand(command=Command.STILL,address=addr)
                elif func=="Arm":
                    self._onCommand(command=Command.VACATE,address=addr)
                elif func=="Disarm":
                    self._onCommand(command=Command.OCCUPY,address=addr)
                elif func=="Lights_On":
                    self._onCommand(command=Command.ON,address=addr)
                elif func=="Lights_Off":
                    self._onCommand(command=Command.OFF,address=addr)
                    
        """
        command sent > st
        02/01 16:44:23 Device selected
        02/01 16:44:23 House A: 2
        02/01 16:44:23 House B: 1
        02/01 16:44:23 Device status
        02/01 16:44:23 House A: 1=0,2=0,3=0,4=1,5=1,6=1,7=1,8=1,10=0,11=0
        0     1        2     3  4
        02/01 16:44:23 Security sensor status
        02/01 16:44:23 Sensor addr: 000003 Last: 1102:40 Arm_KR10A
        02/01 16:44:23 Sensor addr: 000093 Last: 1066:33 Disarm_SH624
        02/01 16:44:23 Sensor addr: 055780 Last: 1049:59 Contact_alert_max_DS10A
        02/01 16:44:23 Sensor addr: 27B380 Last: 01:42 Motion_normal_MS10A
        02/01 16:44:23 Sensor addr: AF1E00 Last: 238:19 Lights_Off_KR10A
        02/01 16:44:23 End status
        """    
        if len(response) > 1:
            print len(response)
            _devicestatus = False
            _securitystatus = False
            #print response
            for line in response:
                #print line.split(' ')[2:4]
                words = line.split(' ')
                if words[2:5] == ["Security","sensor","status"]:
                    _devicestatus=False
                    _securitystatus=True
                    
                if words[2:4] == ["End","status"]:
                    _securitystatus=False
                    
                if _devicestatus:                   
                    housecode = words[3].strip(":")
                    
                    for device in words[4].split(','):
                        devicestatus=device.split('=')
                        print housecode+devicestatus[0]+" is "+devicestatus[1]
                        if devicestatus[1]=='0':
                            self._onCommand(command=Command.OFF,address=str(housecode+devicestatus[0]))
                        if devicestatus[1]=='1':
                            self._onCommand(command=Command.ON,address=str(housecode+devicestatus[0]))
                    
                if _securitystatus:
                    #TODO: Code in Security Status
                    pass
                
                if words[2:4] == ["Device","status"]:
                    print "Device check"
                    _devicestatus=True
    
    def status(self,address):
        self._logger.debug('[Mochad] Querying of last known status all devices including '+address)
        self._interface.write('st'+"\x0D")
        return None 
        
#     def update_status(self):
#         self._logger.debug('Mochad update status called')
#         for d in self._devices:
#             self._logger.debug('... '+ d.address)
#             self.status(d.address)

    def _onCommand(self, command=None, address=None):
        commands = command.split(' ')
        if commands[0] == 'rf':
            address = commands[1]
            command = commands[2][0:len(commands[2])-1]
        self._logger.debug('[Mochad] Command>'+command+' at '+address)
        super(Mochad, self)._onCommand(command=command, address=address)
    
    """ #Causes issues with web interface 
    def __getattr__(self, command):
        return lambda address: self._interface.write('rf ' + address + ' ' + command + "\x0D" ) 
    """

    def on(self, address):
        self._logger.debug('[Mochad] Command on at '+address)
        self._interface.write('rf ' + address + ' on' + "\x0D")

    def off(self, address):
        self._logger.debug('[Mochad] Command off at '+address)
        self._interface.write('rf ' + address + ' off'+ "\x0D")
        
    def disarm(self, address):
        self._logger.debug('[Mochad] Command disarm at '+address)
        self._interface.write('rfsec ' + address + ' disarm'+ "\x0D")
        
    def arm(self, address):
        self._logger.debug('[Mochad] Command sarm at '+address)
        self._interface.write('rfsec ' + address + ' arm'+ "\x0D")

    def version(self):
        self._logger.info("Mochad Pytomation Driver version " + self.VERSION)


## @defgroup Library-Compoments-Energy-Networks-Distribution
# RCAIDE/Library/Compoments/Energy/Networks/Distribution/Electrical_Bus.py 
# 
# Created:  Jul 2023, M. Clarke 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 

# RCAIDE imports  
import RCAIDE 
from RCAIDE.Library.Components                                 import Component
from RCAIDE.Library.Components.Component                       import Container
from RCAIDE.Library.Methods.Energy.Distributors.Electrical_Bus import *


# ----------------------------------------------------------------------------------------------------------------------
#  Electrical_Bus
# ---------------------------------------------------------------------------------------------------------------------- 
## @ingroup Library-Compoments-Energy-Networks-Distribution
class Electrical_Bus(Component):
    """Electrical bus component.
    """ 
    def __defaults__(self):
        """This sets the default values.
    
        Assumptions:
            None
        
        Source:
            None
        """                
        self.tag                                   = 'bus' 
        self.battery_modules                       = Container()
        self.propulsors                            = Container() 
        self.solar_panel                           = None 
        self.avionics                              = RCAIDE.Library.Components.Systems.Avionics()
        self.payload                               = RCAIDE.Library.Components.Payloads.Payload()        
        self.identical_propulsors                  = True
        self.identical_batteries                   = True  
        self.active                                = True
        self.efficiency                            = 1.0
        self.voltage                               = 0.0 
        self.power_split_ratio                     = 1.0
        self.nominal_capacity                      = 0.0
        self.charging_c_rate                       = 0.0
        self.battery_module_electric_configuration = None 
        
    def append_operating_conditions(self, segment):
        append_bus_conditions(self, segment)
        return
    def append_segment_conditions(self, conditions, segment):
        append_bus_segment_conditions(self, conditions, segment)
        return    
    
    def initialize_bus_electrical_properties(self):
        initialize_bus_electrical_properties(self)
        return
    def compute_distributor_conditions(self,state):
        compute_bus_conditions(self, state)
        return    
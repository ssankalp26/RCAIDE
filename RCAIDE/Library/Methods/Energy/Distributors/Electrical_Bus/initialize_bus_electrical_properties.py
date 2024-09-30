#  RCAIDE/Methods/Energy/Distributors/Electrical_Bus/initialize_bus_electrical_properties.py
# 
# Created: Sep 2024, S. Shekar
#
# ----------------------------------------------------------------------------------------------------------------------
#  METHODS
# ---------------------------------------------------------------------------------------------------------------------- 
def initialize_bus_electrical_properties(bus): 
    """ Initializes the bus electrical properties based what is appended onto the bus
        
        Assumptions:
        N/A
    
        Source:
        N/A
    
        Inputs:  
       
        Outputs:
           
        Properties Used:
        None
        """
    if bus.battery_module_electric_configuration is 'Series':
        bus.nominal_capacity = 0
        for battery_module in  bus.battery_modules:
            bus.voltage         +=   battery_module.voltage
            bus.nominal_capacity =  max(battery_module.nominal_capacity, bus.nominal_capacity)  
    elif bus.battery_module_electric_configuration is 'Parallel':
        bus.voltage = 0
        for battery_module in  bus.battery_modules:
            bus.voltage           =  max(battery_module.voltage, bus.voltage)
            bus.nominal_capacity +=  battery_module.nominal_capacity        
    else: raise Exception("Define the electric configuration of the battery modules")    
    
    return
# RCAIDE/Methods/Energy/Distributors/Electrical_Bus.py
# 
# 
# Created: Sep 2024, S. Shekar

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
def compute_bus_conditions(bus,state): 
    """ Computes the conditions of the bus based on the response of the battery modules
        
        Assumptions:
        N/A
    
        Source:
        N/A
    
        Inputs:
               bus
               state  
       
        Outputs:
        None
           
        Properties Used:
        None
        """
    
    bus_conditions                         = state.conditions.energy[bus.tag]
    if bus.battery_module_electric_configuration is  'Series':
        for battery_module in  bus.battery_modules:
            bm_conditions                          =  bus_conditions.battery_modules[battery_module.tag]
            bus_conditions.voltage_open_circuit    += bm_conditions.voltage_open_circuit
            bus_conditions.voltage_under_load      += bm_conditions.voltage_under_load 
            bus_conditions.heat_energy_generated   += bm_conditions.heat_energy_generated
            bus_conditions.temperature             += bm_conditions.temperature
            bus_conditions.energy                  += bm_conditions.energy
        bus_conditions.temperature             =  bus_conditions.temperature / len(bus.battery_modules)
        bus_conditions.SOC                     =  bm_conditions.cell.state_of_charge  
        bus_conditions.efficiency              = (bus_conditions.power_draw+bus_conditions.heat_energy_generated)/bus_conditions.power_draw
    elif bus.battery_module_electric_configuration is 'Parallel':
        for battery_module in  bus.battery_modules:
            bm_conditions                          =  bus_conditions.battery_modules[battery_module.tag]
            bus_conditions.heat_energy_generated   += bm_conditions.heat_energy_generated
            bus_conditions.temperature             += bm_conditions.temperature
            bus_conditions.energy                  += bm_conditions.energy
        bus_conditions.voltage_open_circuit    = bm_conditions.voltage_open_circuit
        bus_conditions.voltage_under_load      = bm_conditions.voltage_under_load             
        bus_conditions.temperature             = bus_conditions.temperature / len(bus.battery_modules)
        bus_conditions.SOC                     = bm_conditions.cell.state_of_charge  
        bus_conditions.efficiency              = (bus_conditions.power_draw+bus_conditions.heat_energy_generated)/bus_conditions.power_draw
              
  
    return 
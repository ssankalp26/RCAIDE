## @ingroup Methods-Energy-Sources-Battery-Lithium_Ion_LFP
# RCAIDE/Methods/Energy/Sources/Battery/Lithium_Ion_LFP/compute_lfp_cell_performance.py
# 
# 
# Created:  Feb 2024, M. Clarke
# Modified: Sep 2024, S. Shekar

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
from RCAIDE.Framework.Core import Units
import numpy as np  
from copy import deepcopy
# ----------------------------------------------------------------------------------------------------------------------
# compute_nmc_cell_performance
# ---------------------------------------------------------------------------------------------------------------------- 
## @ingroup Energy-Sources-Batteries-Lithium_Ion_LFP
def compute_lfp_cell_performance(battery,state,bus,coolant_lines,t_idx, delta_t): 
    """This is an electric cycle model for 18650 lithium-iron_phosphate battery cells. It
       models losses based on an empirical correlation Based on method taken 
       from Datta and Johnson.
       
       Assumptions: 
       1) Constant Peukart coefficient
       2) All battery modules exhibit the same themal behaviour.
       
       Source:
       Internal Resistance:
       Nikolian, Alexandros, et al. "Complete cell-level lithium-ion electrical ECM model 
       for different chemistries (NMC, LFP, LTO) and temperatures (− 5° C to 45° C)–
       Optimized modelling techniques." International Journal of Electrical Power &
       Energy Systems 98 (2018): 133-146.
      
       Voltage:
       Chen, M. and Rincon-Mora, G. A., "Accurate Electrical
       Battery Model Capable of Predicting Runtime and I - V Performance" IEEE
       Transactions on Energy Conversion, Vol. 21, No. 2, June 2006, pp. 504-511
       
       Inputs:
         battery. 
               I_bat             (currnet)                             [Amperes]
               cell_mass         (battery cell mass)                   [kilograms]
               Cp                (battery cell specific heat capacity) [J/(K kg)] 
               E_max             (max energy)                          [Joules]
               E_current         (current energy)                      [Joules]
               Q_prior           (charge throughput)                   [Amp-hrs]
               R_growth_factor   (internal resistance growth factor)   [unitless]
               E_growth_factor   (capactance (energy) growth factor)   [unitless] 
           
         inputs.
               I_bat             (current)                             [amps]
               P_bat             (power)                               [Watts]
       
       Outputs:
         battery.          
              current_energy                                           [Joules]
              heat_energy_generated                                         [Watts] 
              load_power                                               [Watts]
              current                                                  [Amps]
              battery_voltage_open_circuit                             [Volts]
              cell.temperature                                         [Kelvin]
              cell.charge_throughput                                   [Amp-hrs]
              internal_resistance                                      [Ohms]
              battery_state_of_charge                                  [unitless]
              depth_of_discharge                                       [unitless]
              battery_voltage_under_load                               [Volts]   
        
    """ 
     
    # Unpack varibles 
     # Unpack varibles 

    # Battery Properties

    cell_mass          = battery.cell.mass    
    Cp                 = battery.cell.specific_heat_capacity       

    # Bus Conditions
    bus_conditions     =  state.conditions.energy[bus.tag]
    bus_config         =  bus.battery_module_electric_configuration

    I_bus              = bus_conditions.current_draw
    P_bus              = bus_conditions.power_draw

    # Battery Conditions
    battery_conditions = state.conditions.energy[bus.tag].battery_modules[battery.tag]  

    E_max              = battery_conditions.maximum_initial_energy * battery_conditions.cell.capacity_fade_factor
    E_module           = battery_conditions.energy

    V_oc_module        = battery_conditions.voltage_open_circuit
    V_oc_cell          = battery_conditions.cell.voltage_open_circuit   

    P_module           = battery_conditions.power
    P_cell             = battery_conditions.cell.power

    R_0_module         = battery_conditions.internal_resistance
    R_0_cell           = battery_conditions.cell.internal_resistance

    Q_heat_module      = battery_conditions.heat_energy_generated
    Q_heat_cell        = battery_conditions.cell.heat_energy_generated

    V_ul_module         = battery_conditions.voltage_under_load
    V_ul_cell           = battery_conditions.cell.voltage_under_load

    I_module           = battery_conditions.current 
    I_cell             = battery_conditions.cell.current

    T_module           = battery_conditions.temperature                 
    T_cell             = battery_conditions.cell.temperature

    SOC_cell           = battery_conditions.cell.state_of_charge  
    E_cell             = battery_conditions.cell.energy                   
    Q_cell             = battery_conditions.cell.charge_throughput              
    DOD_cell           = battery_conditions.cell.depth_of_discharge
    V_max_cell         = battery.cell.maximum_voltage 
    
    # -------------------------------------------------------------------------
    # Compute battery electrical properties 
    # -------------------------------------------------------------------------    
    # Calculate the current going into one cell  
    n_series          = battery.electrical_configuration.series  
    n_parallel        = battery.electrical_configuration.parallel 
    n_total           = battery.electrical_configuration.total
    no_modules        =  len(bus.battery_modules)
    
    # ---------------------------------------------------------------------------------
    # Examine Thermal Management System
    # ---------------------------------------------------------------------------------
    HAS = None  
    for coolant_line in coolant_lines:
        for tag, item in  coolant_line.items():
            if tag == 'battery_modules':
                for sub_tag, sub_item in item.items():
                    if sub_tag == battery.tag:
                        for btms in  sub_item:
                            HAS = btms    


    # ---------------------------------------------------------------------------------------------------
    # Current State 
    # --------------------------------------------------------------------------------------------------- 
    I_module[t_idx]      = I_bus[t_idx]    
    I_cell[t_idx]        = I_module[t_idx] / n_parallel   

    # ---------------------------------------------------------------------------------
    # Compute battery cell temperature 
    # ---------------------------------------------------------------------------------
    # A voltage model from Chen, M. and Rincon-Mora, G. A., "Accurate Electrical Battery Model Capable of Predicting
    # Runtime and I - V Performance" IEEE Transactions on Energy Conversion, Vol. 21, No. 2, June 2006, pp. 504-511
    V_normalized  = (-1.031*np.exp(-35.*SOC_cell[t_idx]) + 3.685 + 0.2156*SOC_cell[t_idx] - 0.1178*(SOC_cell[t_idx]**2.) + 0.3201*(SOC_cell[t_idx]**3.))/4.1
    V_oc_cell[t_idx] = V_normalized * V_max_cell
    V_oc_cell[t_idx][V_oc_cell[t_idx] > V_max_cell] = V_max_cell
         
    # Voltage under load:
    if state.conditions.energy.recharging:
        V_ul_cell[t_idx]    = V_oc_cell[t_idx]  - I_cell[t_idx]*R_0_cell[t_idx]
    else: 
        V_ul_cell[t_idx]    = V_oc_cell[t_idx]  + I_cell[t_idx]*R_0_cell[t_idx]
        
    # Compute internal resistance
    R_bat                               = -0.0169*(SOC_cell[t_idx]**4) + 0.0418*(SOC_cell[t_idx]**3) - 0.0273*(SOC_cell[t_idx]**2) + 0.0069*(SOC_cell[t_idx]) + 0.0043
    R_0_cell[t_idx]                     = R_bat*battery_conditions.cell.resistance_growth_factor 
    R_0_cell[t_idx][R_0_cell[t_idx]<0]  = 0.0  
    
    # Compute Heat power generated by all cells
    Q_heat_cell[t_idx]   = (I_cell[t_idx]**2.)*R_0_cell[t_idx]
    Q_heat_module[t_idx] = (I_module[t_idx]**2.)*R_0_cell[t_idx]
    
    # Effective Power flowing through battery 
    P_module[t_idx]       = P_bus[t_idx] /no_modules  - np.abs(Q_heat_module[t_idx]) 

        
   # store remaining variables 
    V_oc_module[t_idx]     = V_oc_cell[t_idx]*n_series 
    V_ul_module[t_idx]     = V_ul_cell[t_idx]*n_series  
    T_module[t_idx]        = T_cell[t_idx]   # Assume the cell temperature is the temperature of the module
    P_module[t_idx]        = P_bus[t_idx] / no_modules
    P_cell[t_idx]          = P_module[t_idx]/n_total  
    E_cell[t_idx]          = E_module[t_idx]/n_total  

    # ---------------------------------------------------------------------------------------------------     
    # Future State 
    # --------------------------------------------------------------------------------------------------- 
    if t_idx != state.numerics.number_of_control_points-1:  

       # Compute cell temperature
        if HAS is not None:
            T_cell[t_idx+1]  = HAS.compute_thermal_performance(battery,coolant_line, Q_heat_cell[t_idx],T_cell[t_idx],state,delta_t[t_idx],t_idx)
        else:
            # Considers a thermally insulated system and the heat piles on in the system
            dT_dt              = Q_heat_cell[t_idx]/(cell_mass*Cp)
            T_cell[t_idx+1]    =  T_cell[t_idx] + dT_dt*delta_t[t_idx]
            
        # Compute state of charge and depth of discarge of the battery
        E_module[t_idx+1]                             = E_module[t_idx] -P_module[t_idx]*delta_t[t_idx] 
        E_module[t_idx+1][E_module[t_idx+1] > E_max]  = E_max
        SOC_cell[t_idx+1]                             = E_module[t_idx+1]/E_max 
        SOC_cell[t_idx+1][SOC_cell[t_idx+1]>1]        = 1.
        SOC_cell[t_idx+1][SOC_cell[t_idx+1]<0]        = 0. 
        DOD_cell[t_idx+1]                             = 1 - SOC_cell[t_idx+1]  
    
        # Determine new charge throughput (the amount of charge gone through the battery)
        Q_cell[t_idx+1]    = Q_cell[t_idx] + I_cell[t_idx]*delta_t[t_idx]/Units.hr
        
    stored_results_flag     = True
    stored_battery_tag     = battery.tag  
        
    return stored_results_flag, stored_battery_tag
def reuse_stored_lfp_cell_data(battery,state,bus,coolant_lines, t_idx, delta_t,stored_results_flag, stored_battery_tag):
    '''Reuses results from one propulsor for identical batteries
    
    Assumptions: 
    N/A

    Source:
    N/A

    Inputs:  
    

    Outputs:  
    
    Properties Used: 
    N.A.        
    '''
   
    state.conditions.energy[bus.tag].battery_modules[battery.tag] = deepcopy(state.conditions.energy[bus.tag].battery_modules[stored_battery_tag])
    
        
    return
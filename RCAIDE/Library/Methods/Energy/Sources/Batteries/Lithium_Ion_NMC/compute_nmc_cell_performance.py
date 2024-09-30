# RCAIDE/Methods/Energy/Sources/Battery/Lithium_Ion_NMC/.py
# 
# 
# Created:  Feb 2024, M. Clarke
# Modified: Sep 2024, S. Shekar

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
from RCAIDE.Framework.Core                       import Units 
import numpy as np
from copy import  deepcopy
 
# ----------------------------------------------------------------------------------------------------------------------
# compute_nmc_cell_performance
# ---------------------------------------------------------------------------------------------------------------------- 
def compute_nmc_cell_performance(battery,state,bus,coolant_lines,t_idx, delta_t): 
    '''This is an electric cycle model for 18650 lithium-nickel-manganese-cobalt-oxide
       battery cells. The model uses experimental data performed
       by the Automotive Industrial Systems Company of Panasonic Group 

       Sources:  
       Internal Resistance Model:
       Zou, Y., Hu, X., Ma, H., and Li, S. E., "Combined State of Charge and State of
       Health estimation over lithium-ion battery cellcycle lifespan for electric 
       vehicles,"Journal of Power Sources, Vol. 273, 2015, pp. 793-803.
       doi:10.1016/j.jpowsour.2014.09.146,URLhttp://dx.doi.org/10.1016/j.jpowsour.2014.09.146. 

       Battery Heat Generation Model and  Entropy Model:
       Jeon, Dong Hyup, and Seung Man Baek. "Thermal modeling of cylindrical lithium ion 
       battery during discharge cycle." Energy Conversion and Management 52.8-9 (2011): 
       2973-2981. 

       Assumtions:
       1) All battery modules exhibit the same themal behaviour. 

       Inputs:
         battery.
               I_bat             (maximum_energy)                      [Joules]
               cell_mass         (battery cell mass)                   [kilograms]
               Cp                (battery cell specific heat capacity) [J/(K kg)] 
               t                 (battery age in days)                 [days] 
               T_ambient         (ambient temperature)                 [Kelvin]
               T_current         (pack temperature)                    [Kelvin]
               T_cell            (battery cell temperature)            [Kelvin]
               E_max             (max energy)                          [Joules]
               E_current         (current energy)                      [Joules]
               Q_prior           (charge throughput)                   [Amp-hrs]
               R_growth_factor   (internal resistance growth factor)   [unitless]

         inputs.
               I_bat             (current)                             [amps]
               P_bat             (power)                               [Watts]

       Outputs:
         battery.
              current_energy                                           [Joules]
              temperature                                              [Kelvin]
              heat_energy_generated                                    [Watts]
              load_power                                               [Watts]
              current                                                  [Amps]
              battery_voltage_open_circuit                             [Volts]
              charge_throughput                                        [Amp-hrs]
              internal_resistance                                      [Ohms]
              battery_state_of_charge                                  [unitless]
              depth_of_discharge                                       [unitless]
              battery_voltage_under_load                               [Volts]

    '''


    # Unpack varibles 
   
    # Battery Properties
    electrode_area     = battery.cell.electrode_area 
    As_cell            = battery.cell.surface_area
    cell_mass          = battery.cell.mass    
    Cp                 = battery.cell.specific_heat_capacity       
    battery_data       = battery.cell.discharge_performance_map
    
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
    
    # ---------------------------------------------------------------------------------
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
    if bus_config is 'Series':
        I_module[t_idx]      = I_bus[t_idx]
    elif bus_config is  'Parallel':
        I_module[t_idx]      = I_bus[t_idx] / len(bus.battery_modules)

    I_cell[t_idx]        = I_module[t_idx] / n_parallel   

    # ---------------------------------------------------------------------------------
    # Compute battery cell temperature 
    # ---------------------------------------------------------------------------------
    R_0_cell[t_idx]                     =  (0.01483*(SOC_cell[t_idx]**2) - 0.02518*SOC_cell[t_idx] + 0.1036) *battery_conditions.cell.resistance_growth_factor  
    R_0_cell[t_idx][R_0_cell[t_idx]<0]  = 0. 

    # Determine temperature increase         
    sigma                 = 139 # Electrical conductivity
    n                     = 1
    F                     = 96485 # C/mol Faraday constant    
    delta_S               = -496.66*(SOC_cell[t_idx])**6 +  1729.4*(SOC_cell[t_idx])**5 + -2278 *(SOC_cell[t_idx])**4 +  1382.2 *(SOC_cell[t_idx])**3 + \
                            -380.47*(SOC_cell[t_idx])**2 +  46.508*(SOC_cell[t_idx])  + -10.692  

    i_cell                = I_cell[t_idx]/electrode_area # current intensity 
    q_dot_entropy         = -(T_cell[t_idx])*delta_S*i_cell/(n*F)       
    q_dot_joule           = (i_cell**2)/sigma                   
    Q_heat_cell[t_idx]    = (q_dot_joule + q_dot_entropy)*As_cell 
    Q_heat_module[t_idx]  = Q_heat_cell[t_idx]*n_total  

    V_ul_cell[t_idx]      = compute_nmc_cell_state(battery_data,SOC_cell[t_idx],T_cell[t_idx],I_cell[t_idx]) 

    V_oc_cell[t_idx]      = V_ul_cell[t_idx] + (I_cell[t_idx] * R_0_cell[t_idx])              

    # Effective Power flowing through battery 
    P_module[t_idx]       = P_bus[t_idx] /no_modules  - np.abs(Q_heat_module[t_idx]) 

    # store remaining variables 
    V_oc_module[t_idx]     = V_oc_cell[t_idx]*n_series 
    V_ul_module[t_idx]     = V_ul_cell[t_idx]*n_series  
    T_module[t_idx]        = T_cell[t_idx]   # Assume the cell temperature is the temperature of the module
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


def reuse_stored_nmc_cell_data(battery,state,bus,coolant_lines, t_idx, delta_t,stored_results_flag, stored_battery_tag):
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

## @ingroup Methods-Energy-Sources-Lithium_Ion_NMC
def compute_nmc_cell_state(battery_data,SOC,T,I):
    """This computes the electrical state variables of a lithium ion 
    battery cell with a  lithium-nickel-cobalt-aluminum oxide cathode 
    chemistry from look-up tables 
     
    Assumtions: 
    N/A
    
    Source:  
    N/A 
     
    Inputs:
        SOC           - state of charge of cell     [unitless]
        battery_data  - look-up data structure      [unitless]
        T             - battery cell temperature    [Kelvin]
        I             - battery cell current        [Amperes]
    
    Outputs:  
        V_ul          - under-load voltage          [Volts] 
        
    """ 

    # Make sure things do not break by limiting current, temperature and current 
    SOC[SOC < 0.]   = 0.  
    SOC[SOC > 1.]   = 1.    
    DOD             = 1 - SOC 
    
    T[np.isnan(T)] = 302.65
    T[T<272.65]    = 272.65 # model does not fit for below 0  degrees
    T[T>322.65]    = 322.65 # model does not fit for above 50 degrees
     
    I[I<0.0]       = 0.0
    I[I>8.0]       = 8.0   
     
    pts            = np.hstack((np.hstack((I, T)),DOD  )) # amps, temp, SOC   
    V_ul           = np.atleast_2d(battery_data.Voltage(pts)[:,1]).T  
    
    return V_ul
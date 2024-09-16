# RCAIDE/Methods/Energy/Sources/Battery/Lithium_Ion_NMC/compute_nmc_cell_performance_pybamm.py
# 
# 
# Created: Sep 2024, S. Shekar

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
from RCAIDE.Framework.Core                       import Units 
import numpy as np  

import pybamm
# ----------------------------------------------------------------------------------------------------------------------
# compute_nmc_cell_performance
# ---------------------------------------------------------------------------------------------------------------------- 
def compute_nmc_cell_performance_pybamm(battery,state,bus,coolant_lines,t_idx, delta_t,battery_discharge_flag):
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
       battery_conditions = state.conditions.energy[bus.tag][battery.tag]  
       electrode_area     = battery.cell.electrode_area 
       As_cell            = battery.cell.surface_area
       cell_mass          = battery.cell.mass    
       Cp                 = battery.cell.specific_heat_capacity       
       battery_data       = battery.discharge_performance_map  
       I_bat              = battery_conditions.pack.current_draw
       P_bat              = battery_conditions.pack.power_draw      
       E_max              = battery_conditions.pack.maximum_initial_energy * battery_conditions.cell.capacity_fade_factor
       E_pack             = battery_conditions.pack.energy    
       I_pack             = battery_conditions.pack.current                        
       V_oc_pack          = battery_conditions.pack.voltage_open_circuit           
       V_ul_pack          = battery_conditions.pack.voltage_under_load             
       P_pack             = battery_conditions.pack.power                          
       T_pack             = battery_conditions.pack.temperature                    
       Q_heat_pack        = battery_conditions.pack.heat_energy_generated          
       R_0                = battery_conditions.pack.internal_resistance            
       Q_heat_cell        = battery_conditions.cell.heat_energy_generated          
       SOC                = battery_conditions.cell.state_of_charge                
       P_cell             = battery_conditions.cell.power                          
       E_cell             = battery_conditions.cell.energy                         
       V_ul               = battery_conditions.cell.voltage_under_load             
       V_oc               = battery_conditions.cell.voltage_open_circuit           
       I_cell             = battery_conditions.cell.current                        
       T_cell             = battery_conditions.cell.temperature                    
       Q_cell             = battery_conditions.cell.charge_throughput              
       DOD_cell           = battery_conditions.cell.depth_of_discharge
       
       # ---------------------------------------------------------------------------------
       # Compute battery electrical properties 
       # --------------------------------------------------------------------------------- 
       # Calculate the current going into one cell  
       n_series          = battery.pack.electrical_configuration.series  
       n_parallel        = battery.pack.electrical_configuration.parallel 
       n_total           = battery.pack.electrical_configuration.total
       
       # ---------------------------------------------------------------------------------
       # Examine Thermal Management System
       # ---------------------------------------------------------------------------------
       HAS = None  
       for coolant_line in coolant_lines:
              for tag, item in  coolant_line.items():
                     if tag == 'batteries':
                            for sub_tag, sub_item in item.items():
                                   if sub_tag == battery.tag:
                                          for btms in  sub_item:
                                                 HAS = btms
                               
       # ---------------------------------------------------------------------------------
       # Pybamm Battery Setup
       # ---------------------------------------------------------------------------------                               
       parameter_values = pybamm.ParameterValues("Chen2020")
       model = pybamm.lithium_ion.DFN(options={"thermal":"lumped"})
       
       parameter_values["Initial temperature [K]"] = float(T_cell[t_idx])
       parameter_values["Current function [A]"]    = float(I_bat[t_idx]/n_parallel) 

    
    
       sim = pybamm.Simulation(model,parameter_values=parameter_values)
       sim.solve(t_eval=float(delta_t[t_idx]), initial_soc=float(SOC[t_idx]))
       solution =  sim.solution
       
       
       
       
       T_cell[t_idx+1]       = solution["Volume-averaged cell temperature [C]"].data
       Q_heat_pack[t_idx+1]  = solution["Total heating [W]"].data * battery.pack.electrical_configuration.total
       SOC[t_idx+1]          = solution["Discharge capacity [A.h]"].data[-1] / parameter_values["Nominal cell capacity [A.h]"]
    
       return
## @ingroup Methods-Energy-Propulsors-Networks-turboprop_Propulsor
# RCAIDE/Methods/Energy/Propulsors/Networks/turboprop_Propulsor/compute_turboprop_performance.py
# 
# 
# Created:  Jul 2023, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
# RCAIDE imports  
from RCAIDE.Framework.Core                                           import Data    
from RCAIDE.Library.Methods.Propulsors.Converters.Ram                import compute_ram_performance
from RCAIDE.Library.Methods.Propulsors.Converters.Combustor          import compute_combustor_performance
from RCAIDE.Library.Methods.Propulsors.Converters.Compressor         import compute_compressor_performance
from RCAIDE.Library.Methods.Propulsors.Converters.Turbine            import compute_turbine_performance
from RCAIDE.Library.Methods.Propulsors.Converters.Expansion_Nozzle   import compute_expansion_nozzle_performance 
from RCAIDE.Library.Methods.Propulsors.Converters.Compression_Nozzle import compute_compression_nozzle_performance
from RCAIDE.Library.Methods.Propulsors.Turboshaft_Propulsor          import compute_power

# ----------------------------------------------------------------------------------------------------------------------
# compute_turboprop_performance
# ---------------------------------------------------------------------------------------------------------------------- 
## @ingroup Methods-Energy-Propulsors-Turboshaft_Propulsor
def compute_turboprop_performance(fuel_line,state):   
    ''' Computes the performance of all turboprop engines connected to a fuel tank
    
    Assumptions: 
    N/A

    Source:
    N/A

    Inputs:   
    fuel_line            - data structure containing turboprops on distrubution network  [-]  
    assigned_propulsors  - list of propulsors that are powered by energy source           [-]
    state                - operating data structure                                       [-] 
                     
    Outputs:                      
    outputs              - turboprop operating outputs                                   [-]
    total_power          - power of turboprops                                           [W]
    
    Properties Used: 
    N.A.        
    '''  
    total_power         = 0*state.ones_row(1) 
    thermal_efficiency  = 0*state.ones_row(1) 
    PSFC                = 0*state.ones_row(1) 
    conditions          = state.conditions
    stored_results_flag = False 
    
    for turboprop in fuel_line.propulsors:  
        if turboprop.active == True:  
            if fuel_line.identical_propulsors == False:
                # run analysis  
                total_power, thermal_efficiency, PSFC, stored_results_flag, stored_propulsor_tag = compute_performance(conditions,fuel_line,turboprop,total_power)
            else:             
                if stored_results_flag == False: 
                    # run analysis 
                    total_power, thermal_efficiency, PSFC, stored_results_flag, stored_propulsor_tag = compute_performance(conditions,fuel_line,turboprop,total_power)
                else:
                    # use old results 
                    total_power, thermal_efficiency, PSFC = reuse_stored_data(conditions,fuel_line,turboprop,stored_propulsor_tag,total_power)
                
    return total_power, thermal_efficiency, PSFC 

def compute_performance(conditions,fuel_line,turboprop,total_power):  
    ''' Computes the perfomrance of one turboprop
    
    Assumptions: 
    N/A

    Source:
    N/A

    Inputs:  
    conditions           - operating conditions data structure     [-]  
    fuel_line            - fuelline                                [-] 
    turboprop           - turboprop data structure               [-] 
    total_power          - power of turboprop group               [W] 

    Outputs:  
    total_power          - power of turboprop group               [W] 
    stored_results_flag  - boolean for stored results              [-]     
    stored_propulsor_tag - name of turboprop with stored results  [-]
    
    Properties Used: 
    N.A.        
    ''' 
    #noise_results                                              = conditions.noise[fuel_line.tag][turboprop.tag]  
    #turboprop_results                                         = conditions.energy[fuel_line.tag][turboprop.tag]  
    #ram                                                        = turboprop.ram
    #inlet_nozzle                                               = turboprop.inlet_nozzle
    #compressor                                                 = turboprop.compressor
    #combustor                                                  = turboprop.combustor
    #high_pressure_turbine                                      = turboprop.high_pressure_turbine
    #low_pressure_turbine                                       = turboprop.low_pressure_turbine 
    #core_nozzle                                                = turboprop.core_nozzle  

    ##set the working fluid to determine the fluid properties
    #ram.inputs.working_fluid                                   = turboprop.working_fluid

    ##Flow through the ram , this computes the necessary flow quantities and stores it into conditions
    #compute_ram_performance(ram,conditions)

    ##link inlet nozzle to ram 
    #inlet_nozzle.inputs.stagnation_temperature                 = ram.outputs.stagnation_temperature 
    #inlet_nozzle.inputs.stagnation_pressure                    = ram.outputs.stagnation_pressure

    ##Flow through the inlet nozzle
    #compute_compression_nozzle_performance(inlet_nozzle,conditions)

    ##link compressor to the inlet nozzle
    #compressor.inputs.stagnation_temperature                   = inlet_nozzle.outputs.stagnation_temperature
    #compressor.inputs.stagnation_pressure                      = inlet_nozzle.outputs.stagnation_pressure
                                                               
    ##Flow through the low pressure compressor                  
    #compute_compressor_performance(compressor,conditions)      
                                                               
    ##link the combustor to the compressor                      
    #combustor.inputs.stagnation_temperature                    = compressor.outputs.stagnation_temperature
    #combustor.inputs.stagnation_pressure                       = compressor.outputs.stagnation_pressure
                                                               
    ##flow through the combustor                                
    #compute_combustor_performance(combustor,conditions)        
                                                               
    ##link the high pressure turbine to the combustor           
    #high_pressure_turbine.inputs.stagnation_temperature        = combustor.outputs.stagnation_temperature
    #high_pressure_turbine.inputs.stagnation_pressure           = combustor.outputs.stagnation_pressure
    #high_pressure_turbine.inputs.fuel_to_air_ratio             = combustor.outputs.fuel_to_air_ratio
                                                               
    ##link the high pressure turbine to the compressor          
    #high_pressure_turbine.inputs.compressor                    = compressor.outputs

    ##flow through the high pressure turbine
    #compute_turbine_performance(high_pressure_turbine,conditions)

    ##link the low pressure turbine to the high pressure turbine
    #low_pressure_turbine.inputs.stagnation_temperature         = high_pressure_turbine.outputs.stagnation_temperature
    #low_pressure_turbine.inputs.stagnation_pressure            = high_pressure_turbine.outputs.stagnation_pressure
                                                               
    ##link the low pressure turbine to the combustor            
    #low_pressure_turbine.inputs.fuel_to_air_ratio              = combustor.outputs.fuel_to_air_ratio
                                                               
    ##get the bypass ratio from the thrust component            
    #low_pressure_turbine.inputs.bypass_ratio                   = 0.0

    ##flow through the low pressure turbine
    #compute_turbine_performance(low_pressure_turbine,conditions)

    ##link the core nozzle to the low pressure turbine
    #core_nozzle.inputs.stagnation_temperature                  = low_pressure_turbine.outputs.stagnation_temperature
    #core_nozzle.inputs.stagnation_pressure                     = low_pressure_turbine.outputs.stagnation_pressure

    ##flow through the core nozzle
    #compute_expansion_nozzle_performance(core_nozzle,conditions)

    ## compute the thrust using the thrust component
    ##link the thrust component to the core nozzle
    #turboprop.inputs.core_exit_velocity                       = core_nozzle.outputs.velocity
    #turboprop.inputs.core_area_ratio                          = core_nozzle.outputs.area_ratio
    #turboprop.inputs.core_nozzle                              = core_nozzle.outputs

    ##link the thrust component to the combustor
    #turboprop.inputs.fuel_to_air_ratio                        = combustor.outputs.fuel_to_air_ratio 

    ##link the thrust component to the low pressure compressor 
    #turboprop.inputs.total_temperature_reference              = compressor.inputs.stagnation_temperature
    #turboprop.inputs.total_pressure_reference                 = compressor.inputs.stagnation_pressure 
    #turboprop.inputs.flow_through_core                        =  1.0 #scaled constant to turn on core thrust computation
    #turboprop.inputs.flow_through_fan                         =  0.0 #scaled constant to turn on fan thrust computation        
    
    ##compute the power
    #compute_power(turboprop,conditions,throttle               = turboprop_results.throttle )

    ## getting the network outputs from the power outputs  
    #turboprop_results.power                                   = turboprop.outputs.power  
    #turboprop_results.fuel_flow_rate                          = turboprop.outputs.fuel_flow_rate 
    #total_power                                                += turboprop_results.power
    #thermal_efficiency                                         = turboprop.outputs.thermal_efficiency
    #PSFC                                                       = turboprop.outputs.power_specific_fuel_consumption
    

    ## store data
    #core_nozzle_res = Data(
                #exit_static_temperature             = core_nozzle.outputs.static_temperature,
                #exit_static_pressure                = core_nozzle.outputs.static_pressure,
                #exit_stagnation_temperature         = core_nozzle.outputs.stagnation_temperature,
                #exit_stagnation_pressure            = core_nozzle.outputs.static_pressure,
                #exit_velocity                       = core_nozzle.outputs.velocity
            #)  
    #noise_results.turbofan.core_nozzle                        = core_nozzle_res    
    #stored_results_flag                                        = True
    #stored_propulsor_tag                                       = turboprop.tag
    
    return total_power, thermal_efficiency, PSFC, stored_results_flag,stored_propulsor_tag

def reuse_stored_data(conditions,fuel_line,turboprop,stored_propulsor_tag,total_power):
    '''Reuses results from one turboprop for identical propulsors
    
    Assumptions: 
    N/A

    Source:
    N/A

    Inputs:  
    conditions           - operating conditions data structure     [-]  
    fuel_line            - fuelline                                [-] 
    turboprop            - turboprop data structure              [-] 
    total_power          - power of turboprop group               [W] 

    Outputs:  
    total_power          - power of turboprop group               [W] 
    
    Properties Used: 
    N.A.        
    ''' 
    #turboprop_results_0                   = conditions.energy[fuel_line.tag][stored_propulsor_tag]
    #noise_results_0                       = conditions.noise[fuel_line.tag][stored_propulsor_tag] 
    #turboprop_results                     = conditions.energy[fuel_line.tag][turboprop.tag]  
    #noise_results                         = conditions.noise[fuel_line.tag][turboprop.tag]
    #turboprop_results.throttle            = turboprop_results_0.throttle
    #turboprop_results.power               = turboprop_results_0.power    
    #noise_results.turboprop.core_nozzle   = noise_results_0.turboprop.core_nozzle  
    #total_power                           += turboprop_results.power
    #thermal_efficiency                    = turboprop.outputs.thermal_efficiency
    #PSFC                                  = turboprop.outputs.power_specific_fuel_consumption    
 
    return total_power, thermal_efficiency, PSFC 
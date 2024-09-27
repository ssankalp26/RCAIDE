# RCAIDE/Library/Methods/Propulsors/Turboprop_Propulsor/design_turboprop.py
# (c) Copyright 2023 Aerospace Research Community LLC
# 
# Created:  Jul 2024, RCAIDE Team

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# RCAIDE Imports
import RCAIDE
from RCAIDE.Framework.Mission.Common                                 import Conditions
from RCAIDE.Library.Methods.Propulsors.Converters.Ram                import compute_ram_performance
from RCAIDE.Library.Methods.Propulsors.Converters.Combustor          import compute_combustor_performance
from RCAIDE.Library.Methods.Propulsors.Converters.Compressor         import compute_compressor_performance 
from RCAIDE.Library.Methods.Propulsors.Converters.Propeller          import compute_propeller_performance
from RCAIDE.Library.Methods.Propulsors.Converters.Turbine            import compute_turbine_performance
from RCAIDE.Library.Methods.Propulsors.Converters.Expansion_Nozzle   import compute_expansion_nozzle_performance 
from RCAIDE.Library.Methods.Propulsors.Converters.Compression_Nozzle import compute_compression_nozzle_performance
from RCAIDE.Library.Methods.Propulsors.Turboprop_Propulsor           import size_core
from RCAIDE.Library.Methods.Propulsors.Common                        import compute_static_sea_level_performance


# Python package imports
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
#  Design Turboprop
# ---------------------------------------------------------------------------------------------------------------------- 
def design_turboprop(turboprop):
    """Compute perfomance properties of a turboprop based on polytropic ration and combustor properties.
    Turboprop is created by manually linking the different components
    
    
    Assumtions:
       None 
    
    Source:
    
    Args:
        turboprop (dict): turboprop data structure [-]
    
    Returns:
        None 
    
    """
    # check if mach number and temperature are passed
    if(turboprop.design_mach_number==None) and (turboprop.design_altitude==None): 
        raise NameError('The sizing conditions require an altitude and a Mach number') 
    else:
        #call the atmospheric model to get the conditions at the specified altitude
        atmosphere = RCAIDE.Framework.Analyses.Atmospheric.US_Standard_1976()
        atmo_data  = atmosphere.compute_values(turboprop.design_altitude,turboprop.design_isa_deviation)
        planet     = RCAIDE.Library.Attributes.Planets.Earth()
        
        p   = atmo_data.pressure          
        T   = atmo_data.temperature       
        rho = atmo_data.density          
        a   = atmo_data.speed_of_sound    
        mu  = atmo_data.dynamic_viscosity           
    
        # setup conditions
        conditions = RCAIDE.Framework.Mission.Common.Results()
    
        # freestream conditions    
        conditions.freestream.altitude                    = np.atleast_1d(turboprop.design_altitude)
        conditions.freestream.mach_number                 = np.atleast_1d(turboprop.design_mach_number)
        conditions.freestream.pressure                    = np.atleast_1d(p)
        conditions.freestream.temperature                 = np.atleast_1d(T)
        conditions.freestream.density                     = np.atleast_1d(rho)
        conditions.freestream.dynamic_viscosity           = np.atleast_1d(mu)
        conditions.freestream.gravity                     = np.atleast_1d(planet.compute_gravity(turboprop.design_altitude))
        conditions.freestream.isentropic_expansion_factor = np.atleast_1d(turboprop.working_fluid.compute_gamma(T,p))
        conditions.freestream.Cp                          = np.atleast_1d(turboprop.working_fluid.compute_cp(T,p))
        conditions.freestream.R                           = np.atleast_1d(turboprop.working_fluid.gas_specific_constant)
        conditions.freestream.speed_of_sound              = np.atleast_1d(a)
        conditions.freestream.velocity                    = np.atleast_1d(a*turboprop.design_mach_number) 
    
    fuel_line                = RCAIDE.Library.Components.Energy.Distributors.Fuel_Line()
    segment                  = RCAIDE.Framework.Mission.Segments.Segment()  
    segment.state.conditions = conditions
    segment.state.conditions.energy[fuel_line.tag] = Conditions()
    segment.state.conditions.noise[fuel_line.tag]  = Conditions()
    turboprop.append_operating_conditions(segment,fuel_line) 
    for tag, item in  turboprop.items(): 
        if issubclass(type(item), RCAIDE.Library.Components.Component):
            item.append_operating_conditions(segment,fuel_line,turboprop) 
                    
    ram                       = turboprop.ram
    propeller                 = turboprop.propeller
    compressor                = turboprop.compressor
    combustor                 = turboprop.combustor
    high_pressure_turbine     = turboprop.high_pressure_turbine
    low_pressure_turbine      = turboprop.low_pressure_turbine
    core_nozzle               = turboprop.core_nozzle  

    # unpack component conditions
    turboprop_conditions      = conditions.energy[fuel_line.tag][turboprop.tag]
    ram_conditions            = turboprop_conditions[ram.tag]    
    propeller_conditions      = turboprop_conditions[propeller.tag]
    core_nozzle_conditions    = turboprop_conditions[core_nozzle.tag]
    c_conditions              = turboprop_conditions[compressor.tag]
    lpt_conditions            = turboprop_conditions[low_pressure_turbine.tag]
    hpt_conditions            = turboprop_conditions[high_pressure_turbine.tag]
    combustor_conditions      = turboprop_conditions[combustor.tag] 
     
    # Step 1: Set the working fluid to determine the fluid properties
    ram.working_fluid         = turboprop.working_fluid
    
    # Step 2: Compute flow through the ram , this computes the necessary flow quantities and stores it into conditions
    compute_ram_performance(ram,ram_conditions,conditions)
    
    # Step 3: link inlet nozzle to ram 
    propeller_conditions.inputs.stagnation_temperature             = ram_conditions.outputs.stagnation_temperature
    propeller_conditions.inputs.stagnation_pressure                = ram_conditions.outputs.stagnation_pressure
    
    # Step 4: Compute flow through the inlet nozzle
    compute_propeller_performance(propeller,propeller_conditions,conditions)      
                    
    # Step 5: Link low pressure compressor to the inlet nozzle
    c_conditions.inputs.stagnation_temperature  = propeller_conditions.outputs.stagnation_temperature
    c_conditions.inputs.stagnation_pressure     = propeller_conditions.outputs.stagnation_pressure
    
    # Step 6: Compute flow through the compressor
    compute_compressor_performance(compressor,c_conditions,conditions)
    
    # Step 11: Link the combustor to the high pressure compressor
    combustor_conditions.inputs.stagnation_temperature                = c_conditions.outputs.stagnation_temperature
    combustor_conditions.inputs.stagnation_pressure                   = c_conditions.outputs.stagnation_pressure
    
    # Step 12: Compute flow through the high pressor comprresor
    compute_combustor_performance(combustor,combustor_conditions,conditions)
    
    # Step 13: Link the high pressure turbione to the combustor
    hpt_conditions.inputs.stagnation_temperature    = combustor_conditions.outputs.stagnation_temperature
    hpt_conditions.inputs.stagnation_pressure       = combustor_conditions.outputs.stagnation_pressure
    hpt_conditions.inputs.fuel_to_air_ratio         = combustor_conditions.outputs.fuel_to_air_ratio 
    hpt_conditions.inputs.compressor                = c_conditions.outputs 
    hpt_conditions.inputs.fan                       = propeller_conditions.outputs
    
    # Step 14: Compute flow through the high pressure turbine
    compute_turbine_performance(high_pressure_turbine,hpt_conditions,conditions)
            
    # Step 15: Link the low pressure turbine to the high pressure turbine
    lpt_conditions.inputs.stagnation_temperature     = hpt_conditions.outputs.stagnation_temperature
    lpt_conditions.inputs.stagnation_pressure        = hpt_conditions.outputs.stagnation_pressure
    
    # Step 17: Link the low pressure turbine to the combustor
    lpt_conditions.inputs.fuel_to_air_ratio          = combustor_conditions.outputs.fuel_to_air_ratio
    
    # Step 19: Link the low pressure turbine to the fan
    lpt_conditions.inputs.propeller                  = propeller_conditions.outputs 
    
    # Step 19: Compute flow through the low pressure turbine
    compute_turbine_performance(low_pressure_turbine,lpt_conditions,conditions)
    
    # Step 20: Link the core nozzle to the low pressure turbine
    core_nozzle_conditions.inputs.stagnation_temperature              = lpt_conditions.outputs.stagnation_temperature
    core_nozzle_conditions.inputs.stagnation_pressure                 = lpt_conditions.outputs.stagnation_pressure
    
    # Step 21: Compute flow through the core nozzle
    compute_expansion_nozzle_performance(core_nozzle,core_nozzle_conditions,conditions)
    
    # Step 24: Link the turboprop to outputs from various compoments    
    #turboprop_conditions.bypass_ratio                             = bypass_ratio
    #turboprop_conditions.flow_through_core                        =  1./(1.+bypass_ratio) #scaled constant to turn on core thrust computation
    #turboprop_conditions.flow_through_fan                         =  bypass_ratio/(1.+bypass_ratio) #scaled constant to turn on fan thrust computation  
    #turboprop_conditions.fan_nozzle_exit_velocity                 = fan_nozzle_conditions.outputs.velocity
    #turboprop_conditions.fan_nozzle_area_ratio                    = fan_nozzle_conditions.outputs.area_ratio  
    #turboprop_conditions.fan_nozzle_static_pressure               = fan_nozzle_conditions.outputs.static_pressure
    #turboprop_conditions.core_nozzle_area_ratio                   = core_nozzle_conditions.outputs.area_ratio 
    #turboprop_conditions.core_nozzle_static_pressure              = core_nozzle_conditions.outputs.static_pressure
    #turboprop_conditions.core_nozzle_exit_velocity                = core_nozzle_conditions.outputs.velocity 
    #turboprop_conditions.fuel_to_air_ratio                        = combustor_conditions.outputs.fuel_to_air_ratio 
    #turboprop_conditions.total_temperature_reference              = lpc_conditions.outputs.stagnation_temperature
    #turboprop_conditions.total_pressure_reference                 = lpc_conditions.outputs.stagnation_pressure   

    turboprop_conditions.Tt4                = hpt_conditions.intputs.stagnation_temperature  

    # Step 25: Size the core of the turboprop  
    size_core(turboprop,turboprop_conditions,conditions)
    
    # Step 26: Static Sea Level Thrust 
    compute_static_sea_level_performance(turboprop)
     
    return 
## @ingroup Methods-Energy-Propulsors-Turboprop_Propulsor
# RCAIDE/Methods/Energy/Propulsors/Turboprop_Propulsor/compute_thrust.py
# 
# 
# Created:  Jul 2023, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 
 # RCAIDE imports  
from RCAIDE.Framework.Core      import Units 

# Python package imports
import numpy as np
 
# ----------------------------------------------------------------------------------------------------------------------
#  compute_thrust
# ----------------------------------------------------------------------------------------------------------------------
def compute_thrust(turboprop,turboprop_conditions,conditions):
    """Computes thrust and other properties of the turboprop listed below: 
    turboprop.  
      .outputs.thrust                           (numpy.ndarray): thrust                     [N] 
      .outputs.thrust_specific_fuel_consumption (numpy.ndarray): TSFC                       [N/N-s] 
      .outputs.non_dimensional_thrust           (numpy.ndarray): non-dim thurst             [unitless] 
      .outputs.core_mass_flow_rate              (numpy.ndarray): core nozzle mass flow rate [kg/s] 
      .outputs.fuel_flow_rate                   (numpy.ndarray): fuel flow rate             [kg/s] 
      .outputs.power                            (numpy.ndarray): power                      [W] 
      
    Assumptions:
        Perfect gas

    Source:
        Stanford AA 283 Course Notes: https://web.stanford.edu/~cantwell/AA283_Course_Material/AA283_Course_Notes/


    Args: 
        conditions. 
           freestream.isentropic_expansion_factor                (float): isentropic expansion factor   [unitless]  
           freestream.specific_heat_at_constant_pressure         (float): speific heat                  [J/(kg K)] 
           freestream.velocity                           (numpy.ndarray): freestream velocity           [m/s] 
           freestream.speed_of_sound                     (numpy.ndarray): freestream speed_of_sound     [m/s] 
           freestream.mach_number                        (numpy.ndarray): freestream mach_number        [unitless] 
           freestream.pressure                           (numpy.ndarray): freestream pressure           [Pa] 
           freestream.gravity                            (numpy.ndarray): freestream gravity            [m/s^2] 
           propulsion.throttle                           (numpy.ndarray): throttle                      [unitless] 
        turboprop 
           ..fuel_to_air_ratio                          (float): fuel_to_air_ratio                    [unitless] 
           ..total_temperature_reference                (float): total_temperature_reference          [K] 
           ..total_pressure_reference                   (float): total_pressure_reference             [Pa]    
           .core_nozzle.velocity                      (numpy.ndarray): turboprop core nozzle velocity        [m/s] 
           .core_nozzle.static_pressure               (numpy.ndarray): turboprop core nozzle static pressure [Pa] 
           .core_nozzle.area_ratio                            (float): turboprop core nozzle area ratio      [unitless] 
           .fan_nozzle.velocity                       (numpy.ndarray): turboprop fan nozzle velocity         [m/s] 
           .fan_nozzle.static_pressure                (numpy.ndarray): turboprop fan nozzle static pressure  [Pa] 
           .fan_nozzle.area_ratio                             (float): turboprop fan nozzle area ratio       [unitless]   
           .reference_temperature                             (float): reference_temperature                [K] 
           .reference_pressure                                (float): reference_pressure                   [Pa] 
           .compressor_nondimensional_massflow                (float): non-dim mass flow rate               [unitless]
      
    Returns:
        None
         
    """      
    # Unpack flight conditions 
    gamma                       = conditions.freestream.isentropic_expansion_factor 
    cp                          = conditions.freestream.Cp
    M0                          = conditions.freestream.mach_number
    T0                          = conditions.freestream.temperature                
    h_PR                        = 42800                                             # [kJ/kg] thermal energy released by the fuel during combustion
    
    
    #u0                          = conditions.freestream.velocity
    #a0                          = conditions.freestream.speed_of_sound
    #p0                          = conditions.freestream.pressure  
    #g                           = conditions.freestream.gravity        

    ## Unpack turboprop operating conditions and properties 
    #Tref                        = turboprop.reference_temperature
    #Pref                        = turboprop.reference_pressure
    #mdhc                        = turboprop.compressor_nondimensional_massflow
    #SFC_adjustment              = turboprop.SFC_adjustment 
    #f                           = turboprop_conditions.fuel_to_air_ratio
    #total_temperature_reference = turboprop_conditions.total_temperature_reference
    #total_pressure_reference    = turboprop_conditions.total_pressure_reference 
    #flow_through_core           = turboprop_conditions.flow_through_core 
    #flow_through_fan            = turboprop_conditions.flow_through_fan  
    #V_fan_nozzle                = turboprop_conditions.fan_nozzle_exit_velocity
    #fan_area_ratio              = turboprop_conditions.fan_nozzle_area_ratio
    #P_fan_nozzle                = turboprop_conditions.fan_nozzle_static_pressure
    #P_core_nozzle               = turboprop_conditions.core_nozzle_static_pressure
    #V_core_nozzle               = turboprop_conditions.core_nozzle_exit_velocity
    #core_area_ratio             = turboprop_conditions.core_nozzle_area_ratio                   
    #bypass_ratio                = turboprop_conditions.bypass_ratio  

    ## Compute  non dimensional thrust
    #fan_thrust_nondim   = flow_through_fan*(gamma*M0*M0*(V_fan_nozzle/u0-1.) + fan_area_ratio*(P_fan_nozzle/p0-1.))
    #core_thrust_nondim  = flow_through_core*(gamma*M0*M0*(V_core_nozzle/u0-1.) + core_area_ratio*(P_core_nozzle/p0-1.))

    #thrust_nondim       = core_thrust_nondim + fan_thrust_nondim

    ## Computing Specifc Thrust
    #Fsp   = 1./(gamma*M0)*thrust_nondim

    ## Compute specific impulse
    #Isp   = Fsp*a0*(1.+bypass_ratio)/(f*g)

    ## Compute TSFC
    #TSFC  = f*g/(Fsp*a0*(1.+bypass_ratio))*(1.-SFC_adjustment) * Units.hour # 1/s is converted to 1/hr here
 
    ## Compute core mass flow
    #mdot_core  = mdhc*np.sqrt(Tref/total_temperature_reference)*(total_pressure_reference/Pref)

    ## Compute dimensional thrust
    #FD2  = Fsp*a0*(1.+bypass_ratio)*mdot_core*turboprop_conditions.throttle

    ## Compute power 
    #power   = FD2*u0    

    ## Compute fuel flow rate 
    #fuel_flow_rate   = np.fmax(FD2*TSFC/g,np.array([0.]))*1./Units.hour

    ## Pack turboprop outouts  
    #turboprop_conditions.thrust                            = FD2 
    #turboprop_conditions.thrust_specific_fuel_consumption  = TSFC
    #turboprop_conditions.non_dimensional_thrust            = Fsp  
    #turboprop_conditions.power                             = power  
    #turboprop_conditions.specific_impulse                  = Isp
    #turboprop_conditions.core_mass_flow_rate               = mdot_core
    #turboprop_conditions.fuel_flow_rate                    = fuel_flow_rate   
    
    return  
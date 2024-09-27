## @ingroup Methods-Energy-Propulsors-Turboprop_Propulsor
# RCAIDE/Methods/Energy/Propulsors/Turboprop_Propulsor/size_core.py
# 
# 
# Created:  Jul 2023, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 
from RCAIDE.Library.Methods.Propulsors.Turboprop_Propulsor            import compute_thrust

# Python package imports
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
#  size_core
# ----------------------------------------------------------------------------------------------------------------------
## @ingroup Methods-Energy-Propulsors-Turboprop_Propulsor 
def size_core(turboprop,turboprop_conditions,conditions):
    """Sizes the core flow for the design condition by computing the
    non-dimensional thrust 

    Assumptions:
        Working fluid is a perfect gas

    Source:
        https://web.stanford.edu/~cantwell/AA283_Course_Material/AA283_Course_Notes/

    Args:
        conditions.freestream.speed_of_sound  (numpy.ndarray): [m/s]  
        turboprop
          .bypass_ratio                (float): bypass_ratio                [-]
          .total_temperature_reference (float): total temperature reference [K]
          .total_pressure_reference    (float): total pressure reference    [Pa]  
          .reference_temperature              (float): reference temperature       [K]
          .reference_pressure                 (float): reference pressure          [Pa]
          .design_thrust                      (float): design thrust               [N]  

    Returns:
        None 
    """             
    # Unpack flight conditions 
    a0                                            = conditions.freestream.speed_of_sound

    # Unpack turboprop flight conditions 
    #bypass_ratio   = turboprop_conditions.bypass_ratio
    Tref                                          = turboprop.reference_temperature
    Pref                                          = turboprop.reference_pressure 
    Tt_ref                                        = turboprop_conditions.total_temperature_reference  
    Pt_ref                                        = turboprop_conditions.total_pressure_reference  
    
    # Compute nondimensional thrust
    turboprop_conditions.throttle                 = 1.0
    compute_thrust(turboprop,turboprop_conditions,conditions) 

    # Compute dimensional mass flow rates
    Fsp                                           = turboprop_conditions.non_dimensional_thrust
    mdot_core                                     = turboprop.design_thrust/(Fsp*a0*turboprop_conditions.throttle)  
    mdhc                                          = mdot_core/ (np.sqrt(Tref/Tt_ref)*(Pt_ref/Pref))

    # Store results on turboprop data structure 
    turboprop.mass_flow_rate_design               = mdot_core
    turboprop.compressor_nondimensional_massflow  = mdhc

    return  

# RCAIDE/Methods/Aerodynamics/Common/cooling_drag.py
# 
# 
# Created:  May 2024, S S. Shekar 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------   
from RCAIDE.Framework.Core import Data

# python
import numpy as np 

# ----------------------------------------------------------------------------------------------------------------------
#  cooling_drag
# ----------------------------------------------------------------------------------------------------------------------  
## @ingroup Methods-Aerodynamics-Common-Drag
def cooling_drag(state,heat_exchanger,coolant_line,t_idx,fan_operation):
    """
            Assumptions:
            The density across the duct is equal to the freestream density of air. 
            Inlet area is varied based of required inflow required

            Source:
            Brelje, Benjamin & Jasa, John & Martins, Joaquim & Gray, Justin. (2019).
            Development of a conceptual-level thermal management system design capability in OpenConcept. 

            Inputs:
            Heat Exchanger Design and Operational Properties. 

            Outputs:Cooling Drag 
            None

            Properties Used:
            None

    """
    
    # Unpack Inputs 
    conditions                 = state.conditions
    density                    = conditions.freestream.density[t_idx+1]
    velocity                   = conditions.freestream.velocity[t_idx+1]
    pressure                   = conditions.freestream.pressure[t_idx+1]
   #reference_area             = state.analyses.aerodynamics.geometry.reference_area
    
 
    cd_cooling  = np.zeros_like(density)    
    if fan_operation:
        pass
    else:
    # unpack
        HEX_results               = conditions.energy[coolant_line.tag][heat_exchanger.tag]
        mass_flow_hex              = HEX_results.air_mass_flow_rate[t_idx+1] 
        hex_pressure_diff          = HEX_results.pressure_diff_air[t_idx+1]
        
        # Compute the Inlet area of the Ram
        inlet_area          = mass_flow_hex/(density*velocity)
        outlet_area         = inlet_area*heat_exchanger.atmospheric_air_inlet_to_outlet_area_ratio
        eta_e               = 0.5*(1-outlet_area/inlet_area)
        
        # Compute Exit Parameters
        exit_velocity       = mass_flow_hex/(density*outlet_area)
        exit_pressure       = 0.5*density*((1+eta_e)*exit_velocity**2-velocity)+pressure-hex_pressure_diff
        
        # Compute Drag due to cooling. 
        F_cooling_drag     = mass_flow_hex*(exit_velocity*heat_exchanger.duct_losses -velocity) + outlet_area*heat_exchanger.duct_losses *(exit_pressure-pressure) 
        cd_cooling         = F_cooling_drag/(0.5 * density * (velocity**2) )
                     
    
    # dump to results
    conditions.aerodynamics.coefficients.drag.cooling = Data(total = cd_cooling )

    return 
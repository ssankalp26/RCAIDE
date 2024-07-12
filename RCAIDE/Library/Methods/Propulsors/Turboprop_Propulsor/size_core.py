## @ingroup Methods-Energy-Propulsors-Turboshaft_Propulsor
# RCAIDE/Methods/Energy/Propulsors/Turboshaft_Propulsor/size_core.py
# 
# 
# Created:  Jul 2023, M. Clarke
# Modified: Jun 2024, M. Guidotti

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 
from RCAIDE.Library.Methods.Propulsors.Turboshaft_Propulsor import compute_power

# Python package imports
import numpy                                                       as np

# ----------------------------------------------------------------------------------------------------------------------
#  size_core
# ----------------------------------------------------------------------------------------------------------------------
## @ingroup Methods-Energy-Propulsors-Turboshaft_Propulsor 
def size_core(turboprop,conditions):
    """Sizes the core flow for the design condition.

    Assumptions:
    Perfect gas
    Turboshaft engine with free power turbine

    Sources:
    [1] https://soaneemrana.org/onewebmedia/ELEMENTS%20OF%20GAS%20TURBINE%20PROPULTION2.pdf - Page 332 - 336
    [2] https://www.colorado.edu/faculty/kantha/sites/default/files/attached-files/70652-116619_-_luke_stuyvenberg_-_dec_17_2015_1258_pm_-_stuyvenberg_helicopterturboprops.pdf

    Inputs:
    conditions.freestream.speed_of_sound [m/s] (conditions is also passed to turboprop.compute(..))
    turboprop.inputs.
      bypass_ratio                            [-]
      total_temperature_reference             [K]
      total_pressure_reference                [Pa]
      number_of_engines                       [-]

    Outputs:
    turboprop.outputs.non_dimensional_power  [-]

    Properties Used:
    turboprop.
      reference_temperature                   [K]
      reference_pressure                      [Pa]
      total_design                            [W] - Design power
    """             
    
    #unpack from turboprop
    Tref                                           = turboprop.reference_temperature
    Pref                                           = turboprop.reference_pressure 
    total_temperature_reference                    = turboprop.inputs.total_temperature_reference  
    total_pressure_reference                       = turboprop.inputs.total_pressure_reference 

    #compute nondimensional power
    compute_power(turboprop,conditions)

    #unpack results 
    Psp                                            = turboprop.outputs.non_dimensional_power
    
    #compute dimensional mass flow rates
    mdot_air                                       = turboprop.design_power/Psp
    mdot_compressor                                = mdot_air/ (np.sqrt(Tref/total_temperature_reference)*(total_pressure_reference/Pref))

    #pack outputs
    turboprop.mass_flow_rate_design               = mdot_air
    turboprop.compressor.mass_flow_rate           = mdot_compressor

    return    

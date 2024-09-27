# RCAIDE/Library/Components/Propulsors/Converters/Turboprop.py
# (c) Copyright 2023 Aerospace Research Community LLC
#  
# Created:  Sep 2024, M. Guidotti

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 
 
from RCAIDE.Framework.Core                                                                 import Container
from .                                                                                     import Propulsor
from RCAIDE.Library.Methods.Propulsors.Turboprop_Propulsor.append_turboprop_conditions     import append_turboprop_conditions 
from RCAIDE.Library.Methods.Propulsors.Turboprop_Propulsor.compute_turboprop_performance   import compute_turboprop_performance, reuse_stored_turboprop_data
 
# ---------------------------------------------------------------------------------------------------------------------- 
#  Fan Component
# ---------------------------------------------------------------------------------------------------------------------- 

class Turboprop(Propulsor):
    """This is a turboprop propulsor.
    
    Assumptions:
    None

    Source:
    None
    """ 
    def __defaults__(self):    
        # setting the default values
        self.tag                                      = 'Turboprop'  
        self.propeller                                = Container
        self.ram                                      = None 
        self.high_pressure_compressor                 = None 
        self.low_pressure_turbine                     = None 
        self.high_pressure_turbine                    = None 
        self.combustor                                = None 
        self.core_nozzle                              = None 
        self.active_fuel_tanks                        = None         
        self.engine_length                            = 0.0
        self.engine_height                            = 0.5     # Engine centerline heigh above the ground plane
        self.plug_diameter                            = 0.1     # dimater of the engine plug
        self.geometry_xe                              = 1.      # Geometry information for the installation effects function
        self.geometry_ye                              = 1.      # Geometry information for the installation effects function
        self.geometry_Ce                              = 2.      # Geometry information for the installation effects function
        self.design_isa_deviation                     = 0.0
        self.design_altitude                          = 0.0
        self.SFC_adjustment                           = 0.0 # Less than 1 is a reduction
        self.compressor_nondimensional_massflow       = 0.0
        self.reference_temperature                    = 288.15
        self.reference_pressure                       = 1.01325*10**5 
        self.design_thrust                            = 0.0
        self.mass_flow_rate_design                    = 0.0
    
    def append_operating_conditions(self,segment,fuel_line,add_additional_network_equation = False):
        append_turboprop_conditions(self,segment,fuel_line,add_additional_network_equation)
        return

    def unpack_propulsor_unknowns(self,segment,fuel_line,add_additional_network_equation = False):   
        return 

    def pack_propulsor_residuals(self,segment,fuel_line,add_additional_network_equation = False): 
        return
    
    def compute_performance(self,state,fuel_line,center_of_gravity = [[0, 0, 0]]):
        thrust,moment,power,stored_results_flag,stored_propulsor_tag = compute_turboprop_performance(self,state,fuel_line,center_of_gravity)
        return thrust,moment,power,stored_results_flag,stored_propulsor_tag
    
    def reuse_stored_data(turboprop,state,fuel_line,stored_propulsor_tag,center_of_gravity = [[0, 0, 0]]):
        thrust,moment,power = reuse_stored_turboprop_data(turboprop,state,fuel_line,stored_propulsor_tag,center_of_gravity)
        return thrust,moment,power 
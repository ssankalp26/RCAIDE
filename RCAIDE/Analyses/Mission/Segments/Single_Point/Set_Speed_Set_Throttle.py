## @ingroup Analyses-Mission-Segments-Single_Point
# RCAIDE/Analyses/Mission/Segments/Single_Point/Set_Speed_Set_Throttle.py
# 
# 
# Created:  Jul 2023, M. Clarke
 
# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# RCAIDE imports   
from RCAIDE.Methods.skip                             import skip 
from RCAIDE.Core                                     import Units 
from RCAIDE.Analyses.Mission.Segments.Evaluate       import Evaluate
from RCAIDE.Methods.Mission                          import Common,Segments

# package imports 
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
#  Set_Speed_Set_Throttle
# ----------------------------------------------------------------------------------------------------------------------

## @ingroup Analyses-Mission-Segments-Single_Point
class Set_Speed_Set_Throttle(Evaluate):
    """ This is a segment that is solved using a single point. A snapshot in time.
        We fix the speed and throttle. Acceleration is solved from those.
    
        Assumptions:
        None
        
        Source:
        None
    """       
    
    def __defaults__(self):
        """ This sets the default solver flow. Anything in here can be modified after initializing a segment.
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            None
    
            Outputs:
            None
    
            Properties Used:
            None
        """              
        
        # --------------------------------------------------------------------------------------------------------------
        #   User Inputs
        # --------------------------------------------------------------------------------------------------------------
        self.altitude                                = None
        self.air_speed                               = 10. * Units['km/hr']
        self.throttle                                = 1.
        self.z_accel                                 = 0. # note that down is positive
        self.state.numerics.number_of_control_points = 1
        
        # -------------------------------------------------------------------------------------------------------------- 
        #  Mission Specific Unknowns and Residuals 
        # --------------------------------------------------------------------------------------------------------------  
        self.state.unknowns.x_accel    = np.array([[0.0]])
        self.state.unknowns.body_angle = np.array([[0.5]])
        self.state.residuals.forces    = np.array([[0.0,0.0]])

        # -------------------------------------------------------------------------------------------------------------- 
        #  Mission specific processes 
        # --------------------------------------------------------------------------------------------------------------             
        initialize                         = self.process.initialize 
        initialize.expand_state            = skip
        initialize.differentials           = skip
        initialize.conditions              = Segments.Single_Point.Set_Speed_Set_Throttle.initialize_conditions 
        iterate                            = self.process.iterate 
        iterate.initials.energy            = skip    
        iterate.unknowns.mission           = Segments.Single_Point.Set_Speed_Set_Throttle.unpack_unknowns # Common.Unpack_Unknowns.level_flight
        iterate.conditions.differentials   = skip   
        iterate.conditions.planet_position = skip    
        iterate.conditions.acceleration    = skip
        iterate.conditions.weights         = skip 
        iterate.residuals.total_forces     = Common.Residuals.climb_descent_forces 
        post_process                       = self.process.post_process 
        post_process.inertial_position     = skip    
                
        return


## @ingroup Methods-Missions-Segments-Climb
# RCAIDE/Methods/Missions/Segments/Climb/Constant_Mach_Constant_Angle.py
# 
# 
# Created:  Jul 2023, M. Clarke 

# ----------------------------------------------------------------------------------------------------------------------  
#  IMPORT 
# ----------------------------------------------------------------------------------------------------------------------  
# import RCAIDE 
from RCAIDE.Methods.Mission.Common.Update.atmosphere import atmosphere

# package imports 
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------  
#  Initialize Conditions
# ----------------------------------------------------------------------------------------------------------------------  
## @ingroup Methods-Missions-Segments-Climb
def initialize_conditions(segment):
    """Sets the specified conditions which are given for the segment type.
    
    Assumptions:
    Constant Mach number, with a constant angle of climb

    Source:
    N/A

    Inputs:
    segment.climb_angle                                 [radians]
    segment.mach_number                                 [Unitless]
    segment.altitude_start                              [meters]
    segment.altitude_end                                [meters]
    segment.state.numerics.dimensionless.control_points [Unitless]
    conditions.freestream.density                       [kilograms/meter^3]

    Outputs:
    conditions.frames.inertial.velocity_vector  [meters/second]
    conditions.frames.inertial.position_vector  [meters]
    conditions.freestream.altitude              [meters]

    Properties Used:
    N/A
    """       
    # unpack User Inputs
    climb_angle = segment.climb_angle
    mach_number = segment.mach_number
    alt0        = segment.altitude_start  
    conditions  = segment.state.conditions  
        
    # unpack unknowns  
    alts     = -conditions.frames.inertial.position_vector[:,2]
    
    # check for initial altitude
    if alt0 is None:
        if not segment.state.initials: raise AttributeError('initial altitude not set')
        alt0 = -1.0 * segment.state.initials.conditions.frames.inertial.position_vector[-1,2]
    
    # pack conditions   
    conditions.freestream.altitude[:,0]             =  alts[:,0]  

    # check for initial velocity
    if mach_number is None: 
        if not segment.state.initials: raise AttributeError('mach not set')
        v_mag  = np.linalg.norm(segment.state.initials.conditions.frames.inertial.velocity_vector[-1])*segment.state.ones_row(1)   
    else: 
        # Update freestream to get speed of sound
        atmosphere(segment)
        a = conditions.freestream.speed_of_sound    
        
        # process velocity vector
        v_mag = mach_number * a
    v_x   = v_mag * np.cos(climb_angle)
    v_z   = -v_mag * np.sin(climb_angle)
    
    # pack conditions    
    conditions.frames.inertial.velocity_vector[:,0]              = v_x[:,0]
    conditions.frames.inertial.velocity_vector[:,2]              = v_z[:,0]   
    
# ----------------------------------------------------------------------------------------------------------------------  
#  Residual Total Forces
# ----------------------------------------------------------------------------------------------------------------------  
## @ingroup Methods-Missions-Segments-Climb
def residual_total_forces(segment):
    
    # Unpack results
    FT = segment.state.conditions.frames.inertial.total_force_vector
    a  = segment.state.conditions.frames.inertial.acceleration_vector
    m  = segment.state.conditions.weights.total_mass    
    alt_in  = segment.state.unknowns.altitudes[:,0] 
    alt_out = segment.state.conditions.freestream.altitude[:,0] 
    
    # Residual in X and Z, as well as a residual on the guess altitude
    segment.state.residuals.forces[:,0]   = FT[:,0]/m[:,0] - a[:,0]
    segment.state.residuals.forces[:,1]   = FT[:,2]/m[:,0] - a[:,2]
    segment.state.residuals.altitude[:,0] = (alt_in - alt_out)/alt_out[-1]

    return    
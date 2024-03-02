## @ingroup Networks
# RCAIDE/Energy/Networks/Turbojet_Engine_Network.py
# 
#
# Created:  Oct 2023, M. Clarke
# Modified: 

# ----------------------------------------------------------------------------------------------------------------------
#  Imports
# ---------------------------------------------------------------------------------------------------------------------
# RCAIDE Imports  
import RCAIDE 
from RCAIDE.Core                                                                      import Data 
from RCAIDE.Analyses.Mission.Common                                                   import Residuals    
from RCAIDE.Methods.Energy.Propulsors.Turbojet_Propulsor.compute_turbojet_performance import compute_turbojet_performance
from .Network                                                                         import Network  

# ----------------------------------------------------------------------------------------------------------------------
#  Turbojet
# ---------------------------------------------------------------------------------------------------------------------- 
## @ingroup Energy-Networks
class Turbojet_Engine_Network(Network):
    """ This is a turbojet. 
    
        Assumptions:
        None
        
        Source:
        Most of the componentes come from this book:
        https://web.stanford.edu/~cantwell/AA283_Course_Material/AA283_Course_Notes/
    """      
    
    def __defaults__(self):
        """ This sets the default values for the network to function.
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            None
    
            Outputs:
            None
    
            Properties Used:
            N/A
        """           

        self.tag                          = 'turbojet_engine'  
        self.system_voltage               = None   
        
    # linking the different network components
    def evaluate_thrust(self,state):
        """ Calculate thrust given the current state of the vehicle
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            state [state()]
    
            Outputs:
            results.thrust_force_vector [newtons]
            results.vehicle_mass_rate   [kg/s]
            conditions.noise.sources.turbojet:
                core:
                    exit_static_temperature      
                    exit_static_pressure       
                    exit_stagnation_temperature 
                    exit_stagnation_pressure
                    exit_velocity 
                fan:
                    exit_static_temperature      
                    exit_static_pressure       
                    exit_stagnation_temperature 
                    exit_stagnation_pressure
                    exit_velocity 
    
            Properties Used:
            Defaulted values
        """           

        # Step 1: Unpack
        conditions  = state.conditions  
        fuel_lines  = self.fuel_lines 
         
        total_thrust  = 0. * state.ones_row(3) 
        total_power   = 0. * state.ones_row(1) 
        total_mdot    = 0. * state.ones_row(1)   
        
        # Step 2: loop through compoments of network and determine performance
        for fuel_line in fuel_lines:
            if fuel_line.active:   
                
                # Step 2.1: Compute and store perfomrance of all propulsors 
                fuel_line_T,fuel_line_P = compute_turbojet_performance(fuel_line,state)  
                total_thrust += fuel_line_T   
                total_power  += fuel_line_P  
                
                # Step 2.2: Link each turbojet the its respective fuel tank(s)
                for fuel_tank in fuel_line.fuel_tanks:
                    mdot = 0. * state.ones_row(1)   
                    for turbojet in fuel_line.propulsors:
                        for source in (turbojet.active_fuel_tanks):
                            if fuel_tank.tag == source: 
                                mdot += conditions.energy[fuel_line.tag][turbojet.tag].fuel_flow_rate 
                        
                    # Step 2.3 : Determine cumulative fuel flow from fuel tank 
                    fuel_tank_mdot = fuel_tank.fuel_selector_ratio*mdot + fuel_tank.secondary_fuel_flow 
                    
                    # Step 2.4: Store mass flow results 
                    conditions.energy[fuel_line.tag][fuel_tank.tag].mass_flow_rate  = fuel_tank_mdot  
                    total_mdot += fuel_tank_mdot                    
                            
        # Step 3: Pack results 
        conditions.energy.thrust_force_vector  = total_thrust
        conditions.energy.power                = total_power 
        conditions.energy.vehicle_mass_rate    = total_mdot     
          
        # A PATCH TO BE DELETED IN RCAIDE
        results = Data()
        results.thrust_force_vector       = total_thrust
        results.power                     = total_power
        results.vehicle_mass_rate         = total_mdot     
        # -------------------------------------------------- 
        
        return results 
     
    
    def size(self,state):  
        """ Size the turbojet
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            State [state()]
    
            Outputs:
            None
    
            Properties Used:
            N/A
        """             
        
        #Unpack components
        conditions = state.conditions
        thrust     = self.thrust
        thrust.size(conditions) 
    
    def unpack_unknowns(self,segment):
        """Unpacks the unknowns set in the mission to be available for the mission.

        Assumptions:
        N/A
        
        Source:
        N/A
        
        Inputs:
        state.unknowns.rpm                   [rpm] 
        state.unknowns.throttle              [-] 
        
        Outputs:
        state.conditions.energy.rotor.rpm    [rpm] 
        state.conditions.energy.throttle     [-] 

        
        Properties Used:
        N/A
        """            
        
        fuel_lines = segment.analyses.energy.networks.turbojet_engine.fuel_lines
        RCAIDE.Methods.Mission.Common.Unpack_Unknowns.energy.fuel_line_unknowns(segment,fuel_lines) 
        
        return    
     
    def add_unknowns_and_residuals_to_segment(self, segment ):
        """ This function sets up the information that the mission needs to run a mission segment using this network 
         
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            segment
            eestimated_throttles           [-]
            estimated_propulsor_group_rpms [-]  
            
            Outputs:
            segment
    
            Properties Used:
            N/A
        """                  
        fuel_lines  = segment.analyses.energy.networks.turbojet_engine.fuel_lines
        ones_row    = segment.state.ones_row 
        segment.state.residuals.network = Residuals()  
         
        for fuel_line_i, fuel_line in enumerate(fuel_lines):    
            # ------------------------------------------------------------------------------------------------------            
            # Create fuel_line results data structure  
            # ------------------------------------------------------------------------------------------------------
            segment.state.conditions.energy[fuel_line.tag]       = RCAIDE.Analyses.Mission.Common.Conditions()       
            fuel_line_results                                    = segment.state.conditions.energy[fuel_line.tag]   
            fuel_line_results.throttle                           = 0. * ones_row(1) 
            segment.state.conditions.noise[fuel_line.tag]        = RCAIDE.Analyses.Mission.Common.Conditions()  
            noise_results                                        = segment.state.conditions.noise[fuel_line.tag]  
     
            for fuel_tank in fuel_line.fuel_tanks:               
                fuel_line_results[fuel_tank.tag]                 = RCAIDE.Analyses.Mission.Common.Conditions()  
                fuel_line_results[fuel_tank.tag].mass_flow_rate  = ones_row(1)  
                fuel_line_results[fuel_tank.tag].mass            = ones_row(1)  
                
            # ------------------------------------------------------------------------------------------------------
            # Assign network-specific  residuals, unknowns and results data structures
            # ------------------------------------------------------------------------------------------------------
            for turbojet in fuel_line.propulsors:               
                fuel_line_results[turbojet.tag]                         = RCAIDE.Analyses.Mission.Common.Conditions() 
                fuel_line_results[turbojet.tag].throttle                = 0. * ones_row(1)    
                fuel_line_results[turbojet.tag].y_axis_rotation         = 0. * ones_row(1)   # NEED TO REMOVE
                fuel_line_results[turbojet.tag].thrust                  = 0. * ones_row(1) 
                fuel_line_results[turbojet.tag].power                   = 0. * ones_row(1) 
                noise_results[turbojet.tag]                             = RCAIDE.Analyses.Mission.Common.Conditions() 
                noise_results[turbojet.tag].turbojet                    = RCAIDE.Analyses.Mission.Common.Conditions() 
        
        segment.process.iterate.unknowns.network                  = self.unpack_unknowns                   
        return segment    
        
    __call__ = evaluate_thrust

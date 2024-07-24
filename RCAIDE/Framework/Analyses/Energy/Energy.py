## @ingroup Analyses-Energy
# RCAIDE/Framework/Analyses/Energy/Energy.py
# 
# 
# Created:  Jul 2023, M. Clarke 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------  
# RCAIDE imports   
from RCAIDE.Framework.Analyses import Analysis 

# ----------------------------------------------------------------------------------------------------------------------
#  ANALYSIS
# ----------------------------------------------------------------------------------------------------------------------  
## @ingroup Analyses-Energy
class Energy(Analysis):
    """ RCAIDE.Framework.Analyses.Energy.Energy()
    """
    def __defaults__(self):
        """This sets the default values and methods for the analysis.
            
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
        self.tag      = 'energy'
        self.vehicle  = None
        
    def evaluate_thrust(self,state):
        
        """Evaluate the thrust produced by the energy network.
    
                Assumptions:
                Network has an "evaluate_thrust" method.
    
                Source:
                N/A
    
                Inputs:
                State data container
    
                Outputs:
                Results of the thrust evaluation method.
    
                Properties Used:
                N/A                
            """
                
            
        networks = self.vehicle.networks
        cg       = self.vehicle.mass_properties.center_of_gravity
        results  = networks.evaluate_thrust(state, cg) 
        
        return results
    
    def evaluate_power(self,state):
        
        """Evaluate the power produced by the energy network.
    
                Assumptions:
                Network has an "evaluate_power" method.
    
                Source:
                N/A
    
                Inputs:
                State data container
    
                Outputs:
                Results of the power evaluation method.
    
                Properties Used:
                N/A                
            """
                
            
        networks = self.vehicle.networks
        cg       = self.vehicle.mass_properties.center_of_gravity
        results  = networks.evaluate_power(state, cg) 
        
        return results    
    
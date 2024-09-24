## @ingroup Analyses-Emissions
# RCAIDE/Framework/Analyses/Emissions/Emission_Index_Correlation_Method.py
# 
# 
# Created:  Jul 2024, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------  
from RCAIDE.Framework.Analyses    import Process 
from RCAIDE.Library.Methods.Emissions.Emission_Index_Empirical_Method import *  
from .Emissions            import Emissions 
  

# ----------------------------------------------------------------------------------------------------------------------
#  Correlation_Buildup
# ----------------------------------------------------------------------------------------------------------------------
## @ingroup Analyses-Emissions
class Emission_Index_Correlation_Method(Emissions): 
    """ Emissions Index Correlation Method
    """    
    
    def __defaults__(self): 
        """This sets the default values and methods for the analysis.
    
            Assumptions:
            None
    
            Source:
            None 
            """ 

        # build the evaluation process
        compute                         = Process()  
        compute.emissions               = None  
        self.process.compute            = compute        
                
        return
            
    def initialize(self):   
        compute.emissions  = evaluate_correlation_emissions_indices
        return 


    def evaluate(self,state):
        """The default evaluate function.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        results   <RCAIDE data class>

        Properties Used:
        self.settings
        self.geometry
        """          
        settings = self.settings
        geometry = self.geometry 
        results  = self.process.compute(state,settings,geometry)

        return results             
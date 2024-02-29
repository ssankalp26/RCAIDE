## @ingroup Energy-Sources-Batteries
# RCAIDE/Energy/Sources/Batteries/Lithium_Ion_LiFePO4_18650.py
# 
# 
# Created:  Jul 2023, M. Clarke 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ---------------------------------------------------------------------------------------------------------------------- 

# RCAIDE imports 
from RCAIDE.Core          import Units  
from .Lithium_Ion_Generic import Lithium_Ion_Generic 
from RCAIDE.Methods.Energy.Sources.Battery.Lithium_Ion_LFP  import compute_lfp_cell_performance 

# package imports 
import numpy as np  

# ----------------------------------------------------------------------------------------------------------------------
#  Lithium_Ion_LFP
# ---------------------------------------------------------------------------------------------------------------------- 
## @ingroup Energy-Sources-Batteries 
class Lithium_Ion_LFP(Lithium_Ion_Generic):
    """ Specifies discharge/specific energy characteristics specific 
        18650 lithium-iron-phosphate-oxide battery cells.     
        
        Assumptions: 
        N/A 
        
        Source:
        # Cell Information 
        Saw, L. H., Yonghuang Ye, and A. A. O. Tay. "Electrochemical–thermal analysis of 
        18650 Lithium Iron Phosphate cell." Energy Conversion and Management 75 (2013): 
        162-174.
        
        # Electrode Area
        Muenzel, Valentin, et al. "A comparative testing study of commercial
        18650-format lithium-ion battery cells." Journal of The Electrochemical
        Society 162.8 (2015): A1592.
        
        # Cell Thermal Conductivities 
        (radial)
        Murashko, Kirill A., Juha Pyrhönen, and Jorma Jokiniemi. "Determination of the 
        through-plane thermal conductivity and specific heat capacity of a Li-ion cylindrical 
        cell." International Journal of Heat and Mass Transfer 162 (2020): 120330.
        
        (axial)
        Saw, L. H., Yonghuang Ye, and A. A. O. Tay. "Electrochemical–thermal analysis of 
        18650 Lithium Iron Phosphate cell." Energy Conversion and Management 75 (2013): 
        162-174.
        
        Inputs:
        None
        
        Outputs:
        None
        
        Properties Used:
        N/A
        """ 
    def __defaults__(self):
        self.tag                              = 'lithium_ion_lfp' 
         
        self.cell.diameter                    = 0.0185                                                   # [m]
        self.cell.height                      = 0.0653                                                   # [m]
        self.cell.mass                        = 0.03  * Units.kg                                         # [kg]
        self.cell.surface_area                = (np.pi*self.cell.height*self.cell.diameter) + (0.5*np.pi*self.cell.diameter**2)  # [m^2]
        self.cell.volume                      = np.pi*(0.5*self.cell.diameter)**2*self.cell.height       # [m^3] 
        self.cell.density                     = self.cell.mass/self.cell.volume                          # [kg/m^3]
        self.cell.electrode_area              = 0.0342                                                   # [m^2]  # estimated 
                                                        
        self.cell.maximum_voltage             = 3.6                                                      # [V]
        self.cell.nominal_capacity            = 1.5                                                      # [Amp-Hrs]
        self.cell.nominal_voltage             = 3.6                                                      # [V]
        self.cell.charging_voltage            = self.cell.nominal_voltage                                # [V]  
         
        self.watt_hour_rating                 = self.cell.nominal_capacity  * self.cell.nominal_voltage  # [Watt-hours]      
        self.specific_energy                  = self.watt_hour_rating*Units.Wh/self.cell.mass            # [J/kg]
        self.specific_power                   = self.specific_energy/self.cell.nominal_capacity          # [W/kg]   
        self.ragone.const_1                   = 88.818  * Units.kW/Units.kg
        self.ragone.const_2                   = -.01533 / (Units.Wh/Units.kg)
        self.ragone.lower_bound               = 60.     * Units.Wh/Units.kg
        self.ragone.upper_bound               = 225.    * Units.Wh/Units.kg         
        self.resistance                       = 0.022                                                    # [Ohms]
                                                        
        self.specific_heat_capacity           = 1115                                                     # [J/kgK] 
        self.cell.specific_heat_capacity      = 1115                                                     # [J/kgK] 
        self.cell.radial_thermal_conductivity = 0.475                                                    # [J/kgK]  
        self.cell.axial_thermal_conductivity  = 37.6                                                     # [J/kgK]   
        
        return
    

    def energy_calc(self,state,bus,battery_discharge_flag= True): 
        """This is an electric cycle model for 18650 lithium-iron_phosphate battery cells. It
           models losses based on an empirical correlation Based on method taken 
           from Datta and Johnson.
            
           Inputs: 
           
           Outputs:   
            
        """ 
        compute_lfp_cell_performance(self,state,bus,battery_discharge_flag) 
                        
        return     
    
    def compute_voltage(self,battery_conditions):
        """ Computes the voltage of a single LFP cell or a battery pack of LFP cells   
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:  
                state   - segment unknowns to define voltage [unitless]
            
            Outputs
                V_ul    - under-load voltage                 [volts]
             
            Properties Used:
            N/A
        """              

        return battery_conditions.pack.voltage_under_load 
    
    def update_battery_age(self,segment,increment_battery_age_by_one_day = False):   
        pass 
        return  
 
  
      
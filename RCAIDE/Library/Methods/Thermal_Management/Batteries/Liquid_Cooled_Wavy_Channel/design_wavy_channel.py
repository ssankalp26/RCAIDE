## @ingroup Library-Energy-Methods-Thermal_Management-Batteries
# RCAIDE/Library/Methods/Energy/Propulsors/design_wavy_channel.py


# Created:  Apr 2024, S. Shekar 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
# RCAIDE imports   
from RCAIDE.Framework.Core import Units , Data  
from RCAIDE.Library.Methods.Thermal_Management.Batteries.Liquid_Cooled_Wavy_Channel.wavy_channel_sizing_setup      import wavy_channel_sizing_setup
from RCAIDE.Library.Methods.Thermal_Management.Batteries.Liquid_Cooled_Wavy_Channel.wavy_channel_geometry_setup    import wavy_channel_geometry_setup
from RCAIDE.Framework.Optimization.Common             import Nexus
from RCAIDE.Framework.Optimization.Packages.scipy     import scipy_setup

# Python package imports  
import numpy as np  
import time 

# ----------------------------------------------------------------------
#  Wavy Channel Design
# ----------------------------------------------------------------------
def design_wavy_channel(HAS,battery,single_side_contact=True, dry_mass=True,
                        solver_name= 'SLSQP',iterations = 200,solver_sense_step = 1E-4,
                                       solver_tolerance = 1E-3,print_iterations = False):  
    
    """ Optimizes wavy channel geometric properties input parameters to minimize either design power and mass. 
        This scrip adopts RCAIDE's native optimization style where the objective function is expressed 
        as a sizing function, considering both power and mass.
          
          Inputs: 
          HAS.
              Maximum heat generated by the battery pack. 
              Wavy Channel width
              Wavy Channel thhickness
              Wavy  Channel contact angle
             
          Outputs:
                 Wavy Channel width
                 Wavy Channel thhickness
                 Wavy  Channel contact angle
                 Mass of Heat Acquisition System
                 Power Consumed by Heat Acquisition System 
                 
          Assumptions: 
             The wavy channel extracts from the battery pack considering it to be a lumped mass.  
        
          Source:
            Zhao, C., Clarke, M., Kellermann H., Verstraete D., “Design of a Liquid Cooling System for Lithium-Ion Battery Packs for eVTOL Aircraft" 
    """    
    
    if HAS.coolant_inlet_temperature == None:
        assert('specify coolant inlet temperature')
    elif HAS.design_battery_operating_temperature  == None:
        assert('specify design battery temperature')  
    elif HAS.design_heat_removed  == None: 
        assert('specify heat generated') 

    # start optimization 
    ti                   = time.time()   
    optimization_problem = wavy_channel_design_problem_setup(HAS,battery,print_iterations)
    output               = scipy_setup.SciPy_Solve(optimization_problem,solver=solver_name, iter = iterations , sense_step = solver_sense_step,tolerance = solver_tolerance)  

    tf                   = time.time()
    elapsed_time         = round((tf-ti)/60,2)
    print('Channel Cooling hex Optimization Simulation Time: ' + str(elapsed_time) + ' mins')   

    # print optimization results 
    print (output)   
    HAS_opt = optimization_problem.hrs_configurations.optimized.networks.all_electric.busses.bus.batteries.lithium_ion_nmc.thermal_management_system.heat_acquisition_system
    HAS.mass_properties.mass       = HAS_opt.mass_properties.mass      
    HAS.design_power_draw          = HAS_opt.design_power_draw         
    HAS.design_heat_removed        = HAS_opt.design_heat_removed       
    HAS.coolant_outlet_temperature = HAS_opt.coolant_outlet_temperature
    HAS.coolant_pressure_drop      = HAS_opt.coolant_pressure_drop
    HAS.channel_side_thickness     = HAS_opt.channel_side_thickness     
    HAS.channel_width              = HAS_opt.channel_width          
    HAS.coolant_flow_rate          = HAS_opt.coolant_flow_rate  # per module
    HAS.channel_contact_angle      = HAS_opt.channel_contact_angle  
    HAS.channel_area               = HAS_opt.surface_area_channel 
    
    # Update Battery Spacing based on Wavy Channel
    battery.module.geometrtic_configuration.parallel_spacing  = HAS_opt.battery_parllel_spacing 
    battery.module.geometrtic_configuration.normal_spacing    = HAS_opt.battery_series_spacing 

    return HAS

## @ingroup Methods-Thermal_Management-Batteries-Sizing
def wavy_channel_design_problem_setup(HAS,battery,print_iterations):  

    nexus                        = Nexus()
    problem                      = Data()
    nexus.optimization_problem   = problem 

    b_0        = HAS.channel_side_thickness                           
    d_0        = HAS.channel_width          
    m_dot_0    = HAS.coolant_flow_rate  
    theta_0    = HAS.channel_contact_angle       

    # ---------------------------------------------------------------------------------------------------------- 
    # Design Variables 
    # ----------------------------------------------------------------------------------------------------------       
    inputs = []   
    #               variable   initial      lower limit           upper limit       scaling       units 
    inputs.append([ 'm_dot' ,  m_dot_0     ,   0.05         ,  2.5                 , 1E-1       ,  1*Units.less])   
    inputs.append([ 'd'     ,  d_0         ,   0.001        ,  0.01              , 1E-3       ,  1*Units.less])  
    inputs.append([ 'b'     ,  b_0         ,   0.001        ,  0.002              , 1E-3       ,  1*Units.less]) 
    inputs.append([ 'theta' ,  theta_0     ,48*Units.degrees, 70*Units.degrees   , 1.0        ,  1*Units.less])         
    problem.inputs = np.array(inputs,dtype=object)    

    # ----------------------------------------------------------------------------------------------------------
    # Objective
    # ---------------------------------------------------------------------------------------------------------- 
    problem.objective = np.array([  
        [  'Obj'  ,  10   ,    1*Units.less] ],dtype=object)


    # ----------------------------------------------------------------------------------------------------------
    # Constraints
    # ----------------------------------------------------------------------------------------------------------  
    constraints = []    
    constraints.append([ 'Q_con'         ,  '>'  ,  0.0 ,   1.0   , 1*Units.less]) 
    constraints.append([ 'thick_con'     ,  '>'  ,  0.0 ,   1.0   , 1*Units.less]) 
    
    problem.constraints =  np.array(constraints,dtype=object)                

    # ----------------------------------------------------------------------------------------------------------
    #  Aliases
    # ---------------------------------------------------------------------------------------------------------- 
    aliases = [] 
    btms = 'hrs_configurations.optimized.networks.all_electric.busses.bus.batteries.lithium_ion_nmc.thermal_management_system.heat_acquisition_system'  
    aliases.append([ 'm_dot'       , btms + '.coolant_flow_rate'])    
    aliases.append([ 'b'           , btms + '.channel_side_thickness']) 
    aliases.append([ 'd'           , btms + '.channel_width']) 
    aliases.append([ 'theta'       , btms + '.channel_contact_angle']) 
    aliases.append([ 'Obj'         , 'summary.mass_power_objective' ])  
    aliases.append([ 'Q_con'       , 'summary.heat_energy_constraint'])  
    aliases.append([ 'thick_con'   , 'summary.thickness_constraint'])
    problem.aliases = aliases

    # -------------------------------------------------------------------
    #  Vehicles
    # ------------------------------------------------------------------- 
    nexus.hrs_configurations = wavy_channel_geometry_setup(HAS,battery)

    # -------------------------------------------------------------------
    #  Analyses
    # -------------------------------------------------------------------
    nexus.analyses = None 

    # -------------------------------------------------------------------
    #  Missions
    # -------------------------------------------------------------------
    nexus.missions = None

    # -------------------------------------------------------------------
    #  Procedure
    # -------------------------------------------------------------------    
    #nexus.print_iterations  = print_iterations 
    nexus.procedure         = wavy_channel_sizing_setup()

    # -------------------------------------------------------------------
    #  Summary
    # -------------------------------------------------------------------    
    nexus.summary         = Data()     

    return nexus
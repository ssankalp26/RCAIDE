## @ingroup Components-Energy-Networks
# Lift_Cruise.py
# 
# Created:  Jan 2016, E. Botero
# Modified: Mar 2020, M. Clarke
#           Apr 2021, M. Clarke

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
import SUAVE

# package imports
import numpy as np
from SUAVE.Core import Units, Data
from SUAVE.Components.Propulsors.Propulsor import Propulsor
from SUAVE.Components.Physical_Component import Container

# ----------------------------------------------------------------------
#  Lift_Forward
# ----------------------------------------------------------------------

## @ingroup Components-Energy-Networks
class Lift_Cruise(Propulsor):
    """ This is a complex version of battery_propeller with a battery powering propellers through
        electric motors. In this case we have 2 sets of motors at different motors that can be controlled seperately
        
        This network adds 2 extra unknowns to the mission. The first is
        a voltage, to calculate the thevenin voltage drop in the pack.
        The second is torque matching between motor and propeller.
        
        We have two inputs, the forward throttle and the lift throttle setting
        Since this is an airplane first and foremost, the "throttle" will be for forward thrust
        The new unknown will be for lift throttle, because of the assumption on throttle something needs to be done...
        Want only 1 residual on voltage
    
        Assumptions:
        For any segment using this, body angle can't be an unknown.
        
        Source:
        None
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
        self.rotor_motors                = Container()
        self.propeller_motors            = Container()
        self.rotors                      = Container()
        self.propellers                  = Container()
        self.rotor_esc                   = None
        self.propeller_esc               = None
        self.avionics                    = None
        self.payload                     = None
        self.battery                     = None
        self.rotor_nacelle_diameter      = None
        self.propeller_nacelle_diameter  = None
        self.rotor_engine_length         = None
        self.propeller_engine_length     = None
        self.number_of_rotor_engines     = None
        self.number_of_propeller_engines = None
        self.voltage                     = None
        self.propeller_pitch_command     = 0.0 
        self.rotor_pitch_command         = 0.0     
        self.tag                         = 'Lift_Cruise'
        self.generative_design_minimum   = 0
        self.identical_propellers        = True
        self.identical_rotors            = True
        pass
        
    def evaluate_thrust(self,state):
        """ Calculate thrust given the current state of the vehicle
    
            Assumptions:
            Caps the throttle at 110% and linearly interpolates thrust off that
    
            Source:
            N/A
    
            Inputs:
            state [state()]
    
            Outputs:
            results.thrust_force_vector [Newtons]
            results.vehicle_mass_rate   [kg/s]
            conditions.propulsion:
                rotor_rpm                [radians/sec]
                rpm _forward             [radians/sec]
                rotor_current_draw       [amps]
                propeller_current_draw   [amps]
                battery_draw             [watts]
                battery_energy           [joules]
                voltage_open_circuit     [volts]
                voltage_under_load       [volts]
                rotor_motor_torque        [N-M]
                propeller_motor_torque     [N-M]
                rotor_torque    [N-M]
                propeller_torque [N-M]
    
            Properties Used:
            Defaulted values
        """          
        
        # unpack
        conditions       = state.conditions
        numerics         = state.numerics
        rotor_motors     = self.rotor_motors
        propeller_motors = self.propeller_motors
        rotors           = self.rotors
        propellers       = self.propellers
        rotor_esc        = self.rotor_esc
        propeller_esc    = self.propeller_esc        
        avionics         = self.avionics
        payload          = self.payload
        battery          = self.battery
        num_lift         = self.number_of_rotor_engines
        num_forward      = self.number_of_propeller_engines
        
        # Unpack conditions
        a = conditions.freestream.speed_of_sound        
        
        #-----------------------------------------------------------------
        # SETUP BATTERIES AND ESC's
        #-----------------------------------------------------------------
        
        # Set battery energy
        battery.current_energy = conditions.propulsion.battery_energy    
        
        volts = state.unknowns.battery_voltage_under_load * 1. 
        volts[volts>self.voltage] = self.voltage 
        
        # ESC Voltage
        rotor_esc.inputs.voltagein     = volts      
        propeller_esc.inputs.voltagein = volts 
        
        #---------------------------------------------------------------
        # EVALUATE THRUST FROM FORWARD PROPULSORS 
        #---------------------------------------------------------------
        # Throttle the voltage
        propeller_esc.voltageout(conditions) 
        
        # How many evaluations to do
        if self.identical_propellers:
            n_evals = 1
            factor  = num_forward*1
        else:
            n_evals = int(num_forward)
            factor  = 1.
        
        # Setup numbers for iteration
        total_prop_motor_current = 0.
        total_prop_thrust        = 0. * state.ones_row(3)
        total_prop_power         = 0.
        
        # Iterate over motor/props
        for ii in range(n_evals):    
            
            # Unpack the motor and props
            motor_key = list(propeller_motors.keys())[ii]
            prop_key  = list(propellers.keys())[ii]
            motor     = self.propeller_motors[motor_key]
            prop      = self.propellers[prop_key]            
        
            # link
            motor.inputs.voltage = propeller_esc.outputs.voltageout
            motor.inputs.propeller_CP = np.atleast_2d(conditions.propulsion.propeller_power_coefficient[:,ii]).T
            
            # Run the motor
            motor.omega(conditions)
            
            # link
            prop.inputs.omega  = motor.outputs.omega
            prop.pitch_command = self.propeller_pitch_command 
            
            # Run the propeller
            F_forward, Q_forward, P_forward, Cp_forward, outputs_forward, etap_forward = prop.spin(conditions)
                
            # Check to see if magic thrust is needed, the ESC caps throttle at 1.1 already
            eta                       = conditions.propulsion.throttle[:,0,None]
            P_forward[eta>1.0]        = P_forward[eta>1.0]*eta[eta>1.0]
            F_forward[eta[:,0]>1.0,:] = F_forward[eta[:,0]>1.0,:]*eta[eta[:,0]>1.0,:]  
            
            # Run the motor for current
            motor.current(conditions)
            
            # Conditions specific to this instantation of motor and propellers
            R                        = prop.tip_radius
            rpm                      = motor.outputs.omega / Units.rpm
            F_mag                    = np.atleast_2d(np.linalg.norm(F_forward, axis=1)).T
            total_prop_thrust        = total_prop_thrust + F_forward * factor
            total_prop_power         = total_prop_power  + P_forward * factor
            total_prop_motor_current = total_prop_motor_current + factor*motor.outputs.current

            # Pack specific outputs
            conditions.propulsion.propeller_motor_torque[:,ii] = motor.outputs.torque[:,0]
            conditions.propulsion.propeller_torque[:,ii]       = Q_forward[:,0]
            conditions.propulsion.propeller_rpm[:,ii]          = rpm[:,0]
            conditions.propulsion.propeller_tip_mach[:,ii]     = (R*rpm[:,0]*Units.rpm)/a[:,0]
            conditions.propulsion.propeller_disc_loading[:,ii] = (F_mag[:,0])/(np.pi*(R**2))    # N/m^2                  
            conditions.propulsion.power_loading[:,ii]          = (F_mag[:,0])/(P_forward[:,0])  # N/W               
            conditions.noise.sources.propellers[prop.tag]      = outputs_forward            
            
        
        # link
        propeller_esc.inputs.currentout = total_prop_motor_current
        
        # Run the esc
        propeller_esc.currentin(conditions)        
       
        #-------------------------------------------------------------------
        # EVALUATE THRUST FROM LIFT PROPULSORS 
        #-------------------------------------------------------------------
        
        # Make a new set of konditions, since there are differences for the esc and motor
        konditions                                        = Data()
        konditions.propulsion                             = Data()
        konditions.freestream                             = Data()
        konditions.frames                                 = Data()
        konditions.frames.inertial                        = Data()
        konditions.frames.body                            = Data()
        konditions.propulsion.throttle                    = conditions.propulsion.throttle_lift* 1.
        konditions.propulsion.propeller_power_coefficient = conditions.propulsion.rotor_power_coefficient * 1.
        konditions.freestream.density                     = conditions.freestream.density * 1.
        konditions.freestream.velocity                    = conditions.freestream.velocity * 1.
        konditions.freestream.dynamic_viscosity           = conditions.freestream.dynamic_viscosity * 1.
        konditions.freestream.speed_of_sound              = conditions.freestream.speed_of_sound *1.
        konditions.freestream.temperature                 = conditions.freestream.temperature * 1.
        konditions.freestream.altitude                    = conditions.freestream.altitude * 1.
        konditions.frames.inertial.velocity_vector        = conditions.frames.inertial.velocity_vector *1.
        konditions.frames.body.transform_to_inertial      = conditions.frames.body.transform_to_inertial

        # Throttle the voltage
        rotor_esc.voltageout(konditions)       
        # link
        rotor_motor.inputs.voltage = rotor_esc.outputs.voltageout
        
        # Run the motor
        rotor_motor.omega(konditions)
        
        # link
        rotor.inputs.omega  = rotor_motor.outputs.omega
        rotor.thrust_angle  = self.rotor_thrust_angle
        rotor.pitch_command = self.rotor_pitch_command 
        rotor.VTOL_flag     = state.VTOL_flag   
        
        # Run the propeller
        F_lift, Q_lift, P_lift, Cp_lift, outputs_lift, etap_lift = rotor.spin(konditions)
        rotor.outputs = outputs_lift
        
        # Link
        rotor.outputs = outputs_lift

        # Check to see if magic thrust is needed, the ESC caps throttle at 1.1 already
        eta = state.conditions.propulsion.throttle_lift
        P_lift[eta>1.0] = P_lift[eta>1.0]*eta[eta>1.0]
        F_lift[eta>1.0] = F_lift[eta>1.0]*eta[eta>1.0]        
        
        # Run the motor for current
        i, etam_lift = rotor_motor.current(konditions)  
        
        # Fix the current for the throttle cap
        rotor_motor.outputs.current[eta>1.0] = rotor_motor.outputs.current[eta>1.0]*eta[eta>1.0]
        
        # link
        rotor_esc.inputs.currentout =  rotor_motor.outputs.current     
        
        # Run the esc
        rotor_esc.currentin(konditions)          
        
        ##
        # COMBINE THRUST AND POWER
        ##
        
        # Run the avionics
        avionics.power()
    
        # Run the payload
        payload.power()
        
        # Calculate avionics and payload power
        avionics_payload_power = avionics.outputs.power + payload.outputs.power
    
        # Calculate avionics and payload current
        i_avionics_payload = avionics_payload_power/volts   
        
        # Add up the power usages
        i_lift    = rotor_esc.outputs.currentin
        i_forward = propeller_esc.outputs.currentin
        
        current_total = i_lift + i_forward + i_avionics_payload
        power_total   = current_total * volts   
        
        battery.inputs.current  = current_total
        battery.inputs.power_in = - power_total
        
        # Run the battery
        battery.energy_calc(numerics)   
        
        ## Calculate the thrust and mdot
        #F_lift_total    = F_lift*num_lift * [np.cos(self.rotor_thrust_angle),0,-np.sin(self.rotor_thrust_angle)]    
        #F_forward_total = F_forward*num_forward * [np.cos(self.propeller_thrust_angle),0,-np.sin(self.propeller_thrust_angle)] 
 
        #F_lift_mag    = np.atleast_2d(np.linalg.norm(F_lift_total, axis=1))
        #F_forward_mag = np.atleast_2d(np.linalg.norm(F_forward_total, axis=1))
        
        # Store network performance  
        battery_draw = battery.inputs.power_in 
        conditions.propulsion.battery_draw                      = battery.inputs.power_in 
        conditions.propulsion.battery_energy                    = battery.current_energy 
        conditions.propulsion.battery_voltage_open_circuit      = battery.voltage_open_circuit
        conditions.propulsion.battery_voltage_under_load        = vbattery.voltage_under_load 
        conditions.propulsion.battery_efficiency                = (battery_draw+battery.resistive_losses)/battery_draw
        conditions.propulsion.payload_efficiency                = (battery_draw+(avionics.outputs.power + payload.outputs.power))/battery_draw            
        conditions.propulsion.battery_specfic_power             = -battery_draw/battery.mass_properties.mass    # kWh/kg
        conditions.propulsion.state_of_charge                   = battery.state_of_charge      
        conditions.propulsion.battery_current                   = i_lift + i_forward
        conditions.propulsion.electronics_efficiency            = -(P_forward + P_lift)/battery_draw  
        conditions.propulsion.battery_current                   = current_total

        # noise
        outputs_forward.number_of_engines    = num_forward
        outputs_lift.number_of_engines       = num_lift
        conditions.noise.sources.propeller   = outputs_forward
        conditions.noise.sources.rotor       = outputs_lift

        F_total = F_lift_total + F_forward_total

        results = Data()
        results.thrust_force_vector = F_total
        results.vehicle_mass_rate   = state.ones_row(1)*0.0 
        
        return results
    
    def unpack_unknowns_transition(self,segment):
        """ This is an extra set of unknowns which are unpacked from the mission solver and send to the network.
            This uses all the motors.
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            state.unknowns.rotor_power_coefficient[None]
            state.unknowns.propeller_power_coefficient [None]
            state.unknowns.battery_voltage_under_load  [volts]
            state.unknowns.throttle_lift               [0-1]
            state.unknowns.throttle                    [0-1]
    
            Outputs:
            state.conditions.propulsion.rotor_power_coefficient [None]
            state.conditions.propulsion.propeller_power_coefficient [None]
            state.conditions.propulsion.battery_voltage_under_load  [volts]
            state.conditions.propulsion.throttle_lift              [0-1]
            state.conditions.propulsion.throttle                    [0-1]
    
            Properties Used:
            N/A
        """          
        
        # Here we are going to unpack the unknowns (Cps,throttle,voltage) provided for this network
        segment.state.conditions.propulsion.battery_voltage_under_load  = segment.state.unknowns.battery_voltage_under_load
        segment.state.conditions.propulsion.rotor_power_coefficient     = segment.state.unknowns.rotor_power_coefficient
        segment.state.conditions.propulsion.propeller_power_coefficient = segment.state.unknowns.propeller_power_coefficient   
        segment.state.conditions.propulsion.throttle_lift               = segment.state.unknowns.throttle_lift        
        segment.state.conditions.propulsion.throttle                    = segment.state.unknowns.throttle
        
        return
    
    
    def unpack_unknowns_cruise(self,segment):
        """ This is an extra set of unknowns which are unpacked from the mission solver and send to the network.
            This uses only the forward motors and turns the rest off.
    
            Assumptions:
            Only the forward motors and turns the rest off.
    
            Source:
            N/A
    
            Inputs:
            state.unknowns.propeller_power_coefficient [None]
            state.unknowns.battery_voltage_under_load  [volts]
            state.unknowns.throttle_lift              [0-1]
            state.unknowns.throttle                    [0-1]
    
            Outputs:
            state.conditions.propulsion.propeller_power_coefficient [None]
            state.conditions.propulsion.battery_voltage_under_load  [volts]
            state.conditions.propulsion.throttle_lift              [0-1]
            state.conditions.propulsion.throttle                    [0-1]
    
            Properties Used:
            N/A
        """             
        
        ones = segment.state.ones_row
        
        # Here we are going to unpack the unknowns (Cps,throttle,voltage) provided for this network
        segment.state.conditions.propulsion.throttle_lift                       = 0.0 * ones(1)
        segment.state.conditions.propulsion.rotor_power_coefficient             = 0.0 * ones(1)
        segment.state.conditions.propulsion.battery_voltage_under_load          = segment.state.unknowns.battery_voltage_under_load
        segment.state.conditions.propulsion.propeller_power_coefficient         = segment.state.unknowns.propeller_power_coefficient
        segment.state.conditions.propulsion.throttle                            = segment.state.unknowns.throttle
        
        return    
    
    def unpack_unknowns_lift(self,segment):
        """ This is an extra set of unknowns which are unpacked from the mission solver and send to the network.
            This uses only the lift motors.
    
            Assumptions:
            Only the lift motors.
    
            Source:
            N/A
    
            Inputs:
            state.unknowns.propeller_power_coefficient [None]
            state.unknowns.battery_voltage_under_load  [volts]
            state.unknowns.throttle_lift               [0-1]
            state.unknowns.throttle                    [0-1]
    
            Outputs:
            state.conditions.propulsion.propeller_power_coefficient [None]
            state.conditions.propulsion.battery_voltage_under_load  [volts]
            state.conditions.propulsion.throttle_lift               [0-1]
            state.conditions.propulsion.throttle                    [0-1]
    
            Properties Used:
            N/A
        """             
        
        ones = segment.state.ones_row
        
        # Here we are going to unpack the unknowns (Cps,throttle,voltage) provided for this network
        segment.state.conditions.propulsion.throttle_lift               = segment.state.unknowns.throttle_lift
        segment.state.conditions.propulsion.battery_voltage_under_load  = segment.state.unknowns.battery_voltage_under_load
        segment.state.conditions.propulsion.rotor_power_coefficient     = segment.state.unknowns.rotor_power_coefficient
        segment.state.conditions.propulsion.propeller_power_coefficient = 0.0 * ones(1)
        segment.state.conditions.propulsion.throttle                    = 0.0 * ones(1)
        
        return    
    
    def residuals_transition(self,segment):
        """ This packs the residuals to be send to the mission solver.
            Use this if all motors are operational
    
            Assumptions:
            All motors are operational
    
            Source:
            N/A
    
            Inputs:
            state.conditions.propulsion:
                propeller_motor_torque                [N-m]
                rotor_motor_torque                    [N-m]
                propeller_torque                      [N-m]
                rotor_torque                          [N-m]
                voltage_under_load                    [volts]
            state.unknowns.battery_voltage_under_load [volts]
    
            Outputs:
            None
    
            Properties Used:
            self.voltage                              [volts]
        """            
        
        # Here we are going to pack the residuals (torque,voltage) from the network
        q_propeller_motor = segment.state.conditions.propulsion.propeller_motor_torque
        q_prop_forward    = segment.state.conditions.propulsion.propeller_torque
        q_rotor_motor     = segment.state.conditions.propulsion.rotor_motor_torque
        q_prop_lift       = segment.state.conditions.propulsion.rotor_torque        
        v_actual          = segment.state.conditions.propulsion.battery_voltage_under_load
        v_predict         = segment.state.unknowns.battery_voltage_under_load
        v_max             = self.voltage
        
        # Return the residuals
        segment.state.residuals.network.voltage    = (v_predict - v_actual)/v_max  
        segment.state.residuals.network.propellers = (q_propeller_motor - q_prop_forward)/q_propeller_motor
        segment.state.residuals.network.rotors     = (q_rotor_motor - q_prop_lift)/q_rotor_motor

        return
    
    
    def residuals_cruise(self,segment):
        """ This packs the residuals to be send to the mission solver.
            Use this if only the forward motors are operational
    
            Assumptions:
            Only the forward motors are operational
    
            Source:
            N/A
    
            Inputs:
            state.conditions.propulsion:
                propeller_motor_torque                [N-m]
                rotor_motor_torque                    [N-m]
                propeller_torque                      [N-m]
                rotor_torque                          [N-m]
                voltage_under_load                    [volts]
            state.unknowns.battery_voltage_under_load [volts]
            
            Outputs:
            None
    
            Properties Used:
            self.voltage                              [volts]
        """          
        
        # Here we are going to pack the residuals (torque,voltage) from the network
        q_propeller_motor = segment.state.conditions.propulsion.propeller_motor_torque
        q_prop_forward    = segment.state.conditions.propulsion.propeller_torque   
        v_actual          = segment.state.conditions.propulsion.battery_voltage_under_load
        v_predict         = segment.state.unknowns.battery_voltage_under_load
        v_max             = self.voltage        
        
        # Return the residuals
        segment.state.residuals.network.voltage   = (v_predict - v_actual)/v_max 
        segment.state.residuals.network.propeller = (q_propeller_motor - q_prop_forward)/q_propeller_motor

        return    
    
    def residuals_lift(self,segment):
        """ This packs the residuals to be send to the mission solver.
            Only the lift motors are operational
    
            Assumptions:
            The lift motors are operational
    
            Source:
            N/A
    
            Inputs:
            state.conditions.propulsion:
                propeller_motor_torque                [N-m]
                rotor_motor_torque                    [N-m]
                propeller_torque                      [N-m]
                rotor_torque                          [N-m]
                voltage_under_load                    [volts]
            state.unknowns.battery_voltage_under_load [volts]
    
            Outputs:
            None
    
            Properties Used:
            self.voltage                              [volts]
        """            
        
        # Here we are going to pack the residuals (torque,voltage) from the network
        q_rotor_motor   = segment.state.conditions.propulsion.rotor_motor_torque
        q_prop_lift     = segment.state.conditions.propulsion.rotor_torque        

        v_actual        = segment.state.conditions.propulsion.battery_voltage_under_load
        v_predict       = segment.state.unknowns.battery_voltage_under_load
        v_max           = self.voltage        
        
        # Return the residuals
        segment.state.residuals.network = (v_predict - v_actual)/v_max  
        segment.state.residuals.network = (q_rotor_motor - q_prop_lift)/q_rotor_motor

        return
    
    
    def add_transition_unknowns_and_residuals_to_segment(self, segment, initial_voltage = None, 
                                                         initial_prop_power_coefficient = 0.005,
                                                         initial_rotor_power_coefficient = 0.005,
                                                         initial_throttle_lift = 0.9):
        """ This function sets up the information that the mission needs to run a mission segment using this network
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            segment
            initial_voltage                   [v]
            initial_power_coefficient         [float]s
            
            Outputs:
            segment.state.unknowns.battery_voltage_under_load
            segment.state.unknowns.propeller_power_coefficient
            segment.state.conditions.propulsion.propeller_motor_torque
            segment.state.conditions.propulsion.propeller_torque   
    
            Properties Used:
            N/A
        """           
        
        # unpack the ones function
        ones_row = segment.state.ones_row
        
        # unpack the initial values if the user doesn't specify
        if initial_voltage==None:
            initial_voltage = self.battery.max_voltage
        
        # Count how many unknowns and residuals based on p
        n_props    = len(self.propellers)
        n_rotors   = len(self.rotors)
        n_motors_p = len(self.propeller_motors)
        n_motors_r = len(self.rotor_motors)
        n_eng_p    = self.number_of_propeller_engines
        n_eng_r    = self.number_of_rotor_engines

        
        if n_props!=n_motors_p!=n_eng_p:
            assert('The number of propellers is not the same as the number of motors')
            
        if n_rotors!=n_motors_r!=n_eng_r:
            assert('The number of rotors is not the same as the number of motors')
            
        # Now check if the props/rotors are all identical, in this case they have the same of residuals and unknowns
        if self.identical_propellers:
            n_props = 1
        else:
            self.number_of_propeller_engines = int(self.number_of_propeller_engines)
            
        if self.identical_rotors:
            n_rotors = 1
        else:
            self.number_of_rotor_engines = int(self.number_of_rotor_engines)
        
        # Setup the residuals
        segment.state.residuals.network            = Data()        
        segment.state.residuals.network.voltage    = 0. * ones_row(1)
        segment.state.residuals.network.propellers = 0. * ones_row(n_props)
        segment.state.residuals.network.rotors     = 0. * ones_row(n_rotors)
        
        # Setup the unknowns
        segment.state.unknowns.throttle_lift               = initial_throttle_lift           * ones_row(1)   
        segment.state.unknowns.battery_voltage_under_load  = initial_voltage                 * ones_row(1)
        segment.state.unknowns.propeller_power_coefficient = initial_prop_power_coefficient  * ones_row(n_props)
        segment.state.unknowns.rotor_power_coefficient     = initial_rotor_power_coefficient * ones_row(n_rotors)
        
        # Setup the conditions for the propellers
        segment.state.conditions.propulsion.propeller_motor_torque  = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_torque        = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_rpm           = 0. * ones_row(n_props)      
        segment.state.conditions.propulsion.propeller_disc_loading  = 0. * ones_row(n_props)                 
        segment.state.conditions.propulsion.propeller_power_loading = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_tip_mach      = 0. * ones_row(n_props)

        # Setup the conditions for the rotors
        segment.state.conditions.propulsion.rotor_motor_torque      = 0. * ones_row(n_rotors)
        segment.state.conditions.propulsion.rotor_torque            = 0. * ones_row(n_rotors)
        segment.state.conditions.propulsion.rotor_rpm               = 0. * ones_row(n_rotors)
        segment.state.conditions.propulsion.rotor_disc_loading      = 0. * ones_row(n_rotors)                 
        segment.state.conditions.propulsion.rotor_power_loading     = 0. * ones_row(n_rotors)        
        segment.state.conditions.propulsion.rotor_tip_mach          = 0. * ones_row(n_rotors)
        
        # Ensure the mission knows how to pack and unpack the unknowns and residuals
        segment.process.iterate.unknowns.network  = self.unpack_unknowns_transition
        segment.process.iterate.residuals.network = self.residuals_transition      

        return segment
    
    
    def add_cruise_unknowns_and_residuals_to_segment(self, segment, initial_voltage = None, 
                                                         initial_prop_power_coefficient = 0.005):
        """ This function sets up the information that the mission needs to run a mission segment using this network
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            segment
            initial_voltage                   [v]
            initial_power_coefficient         [float]s
            
            Outputs:
            segment.state.unknowns.battery_voltage_under_load
            segment.state.unknowns.propeller_power_coefficient
            segment.state.conditions.propulsion.propeller_motor_torque
            segment.state.conditions.propulsion.propeller_torque   
    
            Properties Used:
            N/A
        """           
        
        # unpack the ones function
        ones_row = segment.state.ones_row
        
        # unpack the initial values if the user doesn't specify
        if initial_voltage==None:
            initial_voltage = self.battery.max_voltage
        
        # Count how many unknowns and residuals based on p
        n_props    = len(self.propellers)
        n_motors_p = len(self.propeller_motors)
        n_eng_p    = self.number_of_propeller_engines
        
        if n_props!=n_motors_p!=n_eng_p:
            assert('The number of propellers is not the same as the number of motors')
            
        # Now check if the props/rotors are all identical, in this case they have the same of residuals and unknowns
        if self.identical_propellers:
            n_props = 1
        else:
            self.number_of_propeller_engines = int(self.number_of_propeller_engines)
            
        if self.identical_rotors:
            n_rotors = 1
        else:
            self.number_of_rotor_engines = int(self.number_of_rotor_engines)
        
        # Setup the residuals
        segment.state.residuals.network            = Data()
        segment.state.residuals.network.voltage    = 0. * ones_row(1)
        segment.state.residuals.network.propellers = 0. * ones_row(n_props)
        
        # Setup the unknowns
        segment.state.unknowns.battery_voltage_under_load  = initial_voltage * ones_row(1)
        segment.state.unknowns.propeller_power_coefficient = initial_prop_power_coefficient * ones_row(n_props)
        
        # Setup the conditions for the propellers
        segment.state.conditions.propulsion.propeller_motor_torque  = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_torque        = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_rpm           = 0. * ones_row(n_props)      
        segment.state.conditions.propulsion.propeller_disc_loading  = 0. * ones_row(n_props)                 
        segment.state.conditions.propulsion.propeller_power_loading = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_tip_mach      = 0. * ones_row(n_props)
        
        # Setup the conditions for the rotors
        segment.state.conditions.propulsion.rotor_motor_torque      = 0. * ones_row(n_rotors)
        segment.state.conditions.propulsion.rotor_torque            = 0. * ones_row(n_rotors)
        segment.state.conditions.propulsion.rotor_rpm               = 0. * ones_row(n_rotors)
        segment.state.conditions.propulsion.rotor_disc_loading      = 0. * ones_row(n_rotors)                 
        segment.state.conditions.propulsion.rotor_power_loading     = 0. * ones_row(n_rotors)        
        segment.state.conditions.propulsion.rotor_tip_mach          = 0. * ones_row(n_rotors)        

        # Ensure the mission knows how to pack and unpack the unknowns and residuals
        segment.process.iterate.unknowns.network  = self.unpack_unknowns_cruise
        segment.process.iterate.residuals.network = self.residuals_cruise     

        return segment
    
    
    def add_lift_unknowns_and_residuals_to_segment(self, segment, initial_voltage = None,
                                                         initial_rotor_power_coefficient = 0.005,
                                                         initial_throttle_lift = 0.9):
        """ This function sets up the information that the mission needs to run a mission segment using this network
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            segment
            initial_voltage                   [v]
            initial_power_coefficient         [float]s
            
            Outputs:
            segment.state.unknowns.battery_voltage_under_load
            segment.state.unknowns.propeller_power_coefficient
            segment.state.conditions.propulsion.propeller_motor_torque
            segment.state.conditions.propulsion.propeller_torque   
    
            Properties Used:
            N/A
        """           
        
        # unpack the ones function
        ones_row = segment.state.ones_row
        
        # unpack the initial values if the user doesn't specify
        if initial_voltage==None:
            initial_voltage = self.battery.max_voltage
        
        # Count how many unknowns and residuals based on p
        n_rotors   = len(self.rotors)
        n_motors_r = len(self.rotor_motors)
        n_eng_r    = self.number_of_rotor_engines

        if n_rotors!=n_motors_r!=n_eng_r:
            assert('The number of rotors is not the same as the number of motors')
            
        # Now check if the props/rotors are all identical, in this case they have the same of residuals and unknowns
        if self.identical_propellers:
            n_props = 1
        else:
            self.number_of_propeller_engines = int(self.number_of_propeller_engines)
            
        if self.identical_rotors:
            n_rotors = 1
        else:
            self.number_of_rotor_engines = int(self.number_of_rotor_engines)
        
        # Setup the residuals
        segment.state.residuals.network            = Data()        
        segment.state.residuals.network.voltage    = 0. * ones_row(1)
        segment.state.residuals.network.rotors     = 0. * ones_row(n_rotors)
        
        # Setup the unknowns
        segment.state.unknowns.__delitem__('throttle')
        segment.state.unknowns.throttle_lift               = initial_throttle_lift           * ones_row(1)
        segment.state.unknowns.battery_voltage_under_load  = initial_voltage                 * ones_row(1)
        segment.state.unknowns.rotor_power_coefficient     = initial_rotor_power_coefficient * ones_row(n_rotors)
        
        # Setup the conditions for the propellers
        segment.state.conditions.propulsion.propeller_motor_torque  = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_torque        = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_rpm           = 0. * ones_row(n_props)      
        segment.state.conditions.propulsion.propeller_disc_loading  = 0. * ones_row(n_props)                 
        segment.state.conditions.propulsion.propeller_power_loading = 0. * ones_row(n_props)
        segment.state.conditions.propulsion.propeller_tip_mach      = 0. * ones_row(n_props)        

        # Setup the conditions for the rotors
        segment.state.conditions.propulsion.rotor_motor_torque      = 0. * ones_row(n_rotors)
        segment.state.conditions.propulsion.rotor_torque            = 0. * ones_row(n_rotors)
        segment.state.conditions.propulsion.rotor_rpm               = 0. * ones_row(n_rotors)
        segment.state.conditions.propulsion.rotor_disc_loading      = 0. * ones_row(n_rotors)                 
        segment.state.conditions.propulsion.rotor_power_loading     = 0. * ones_row(n_rotors)        
        segment.state.conditions.propulsion.rotor_tip_mach          = 0. * ones_row(n_rotors)
        
        # Ensure the mission knows how to pack and unpack the unknowns and residuals
        segment.process.iterate.unknowns.network  = self.unpack_unknowns_lift
        segment.process.iterate.residuals.network = self.residuals_lift 

        return segment    
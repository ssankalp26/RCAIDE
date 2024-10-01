## @defgroup Library-Plots-Mission  
# RCAIDE/Library/Plots/Performance/Mission/plot_flight_conditions.py
# 
# 
# Created:  Jul 2023, M. Clarke 

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------  

from RCAIDE.Framework.Core import Units
from RCAIDE.Library.Plots.Common import set_axes, plot_style
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np 

# ----------------------------------------------------------------------------------------------------------------------
#  PLOTS
# ----------------------------------------------------------------------------------------------------------------------   
## @defgroup Library-Plots-Mission  
def plot_flight_conditions(results,
                           save_figure = False,
                           show_legend=True,
                           save_filename = "Flight Conditions",
                           file_type = ".png",
                           width = 8, height = 6): 

    """This plots the flights the conditions

    Assumptions:
    None

    Source:
    None

    Inputs:
    results.segments.conditions.
         frames
             body.inertial_rotations
             inertial.position_vector
         freestream.velocity
         aerodynamics.
             lift_coefficient
             drag_coefficient
             angle_of_attack

    Outputs:
    Plots

    Properties Used:
    N/A
    """
 

    # get plotting style 
    ps      = plot_style()  

    parameters = {'axes.labelsize': ps.axis_font_size,
                  'xtick.labelsize': ps.axis_font_size,
                  'ytick.labelsize': ps.axis_font_size,
                  'axes.titlesize': ps.title_font_size}
    plt.rcParams.update(parameters)
     
    # get line colors for plots 
    line_colors   = cm.inferno(np.linspace(0,0.9,len(results.segments)))     
     
    fig_1   = plt.figure(save_filename + "_Altitude")
    fig_2   = plt.figure(save_filename + "_Airspeed")
    fig_3   = plt.figure(save_filename + "_Range")
    fig_4   = plt.figure(save_filename + "_Pitch_Angle")
    
    fig_1.set_size_inches(width,height)
    fig_2.set_size_inches(width,height)
    fig_3.set_size_inches(width,height)
    fig_4.set_size_inches(width,height)
    for i in range(len(results.segments)): 
        time     = results.segments[i].conditions.frames.inertial.time[:,0] / Units.min
        airspeed = results.segments[i].conditions.freestream.velocity[:,0] /   Units['mph']
        theta    = results.segments[i].conditions.frames.body.inertial_rotations[:,1,None] / Units.deg
        Range    = results.segments[i].conditions.frames.inertial.aircraft_range[:,0]/ Units.nmi
        altitude = results.segments[i].conditions.freestream.altitude[:,0]/Units.feet
              
        segment_tag  =  results.segments[i].tag
        segment_name = segment_tag.replace('_', ' ')
        
        axis_1 = plt.subplot(1,1,1)
        axis_1.plot(time, altitude, color = line_colors[i], marker = ps.markers[0], linewidth = ps.line_width, label = segment_name, markersize = ps.marker_size)
        axis_1.set_ylabel(r'Altitude (ft)')
        set_axes(axis_1)    
        
        axis_2 = plt.subplot(1,1,1)
        axis_2.plot(time, airspeed, color = line_colors[i], marker = ps.markers[0], linewidth = ps.line_width, label = segment_name, markersize = ps.marker_size) 
        axis_2.set_ylabel(r'Airspeed (mph)')
        set_axes(axis_2) 
        
        axis_3 = plt.subplot(1,1,1)
        axis_3.plot(time, Range, color = line_colors[i], marker = ps.markers[0], linewidth = ps.line_width, label = segment_name, markersize = ps.marker_size)
        axis_3.set_xlabel('Time (mins)')
        axis_3.set_ylabel(r'Range (nmi)')
        set_axes(axis_3) 
         
        axis_4 = plt.subplot(1,1,1)
        axis_4.plot(time, theta, color = line_colors[i], marker = ps.markers[0], linewidth = ps.line_width, label = segment_name, markersize = ps.marker_size)
        axis_4.set_xlabel('Time (mins)')
        axis_4.set_ylabel(r'Pitch Angle (deg)')
        set_axes(axis_4) 
         
    
    if show_legend:        
        leg1 =  fig_1.legend(bbox_to_anchor=(0.5, 1.0), loc='upper center', ncol = 5)
        leg2 =  fig_2.legend(bbox_to_anchor=(0.5, 1.0), loc='upper center', ncol = 5)
        leg3 =  fig_3.legend(bbox_to_anchor=(0.5, 1.0), loc='upper center', ncol = 5)
        leg4 =  fig_4.legend(bbox_to_anchor=(0.5, 1.0), loc='upper center', ncol = 5)
        
        leg1.set_title('Flight Segment', prop={'size': ps.legend_font_size, 'weight': 'heavy'})
        leg2.set_title('Flight Segment', prop={'size': ps.legend_font_size, 'weight': 'heavy'})
        leg3.set_title('Flight Segment', prop={'size': ps.legend_font_size, 'weight': 'heavy'})
        leg4.set_title('Flight Segment', prop={'size': ps.legend_font_size, 'weight': 'heavy'}) 
    
    # Adjusting the sub-plots for legend 
    fig_1.subplots_adjust(top=0.8)
    fig_2.subplots_adjust(top=0.8)
    fig_3.subplots_adjust(top=0.8)
    fig_4.subplots_adjust(top=0.8) 

    fig_1.tight_layout()    
    fig_2.tight_layout()    
    fig_3.tight_layout()    
    fig_4.tight_layout()    
    if save_figure:
        fig_1.savefig(save_filename + "_Altitude"+ file_type)
        fig_2.savefig(save_filename + "_Airspeed"+ file_type)
        fig_3.savefig(save_filename + "_Range"+ file_type)
        fig_4.savefig(save_filename + "_Pitch_Angle"+ file_type)  
    return  fig_1, fig_2,  fig_3,  fig_4
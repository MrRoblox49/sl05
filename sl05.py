
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# 1. App Title and Description
st.set_page_config(page_title="Overtaking Sight Distance Simulator", layout="centered")
st.title("Overtaking sight distance simulator")
st.write("Adjust the parameters in the sidebar to see how they affect the situation.")

# 2. Sidebar Inputs for Parameters
st.sidebar.header("Simulation Parameters")
velocity_b = st.sidebar.slider("Velocity of blue car (km/hr)", min_value=50, max_value=130, value=70, step=1)
acceleration_r = st.sidebar.slider("Acceleration of red car (m/s^2)", min_value=0.40, max_value=1.20, value=1.10, step=0.01)
velocity_y = st.sidebar.slider("Velocity of yellow car (km/hr)", min_value=50, max_value=130, value=60, step=1)
reaction_time = st.sidebar.slider("Reaction time (s)", min_value=1.0, max_value=4.0, value=2.0, step=0.1)

# 3. Derived Physics Calculations
# velocity in hr
velocity_b = velocity_b/3.6
velocity_y = velocity_y/3.6
# s = 0.75vb + 6
s = 0.75 * velocity_b + 6
# T = sqrt(4s/a)
T = np.sqrt(4*s/acceleration_r)
# d_1 = vb*trec
d_1 = velocity_b*reaction_time
# d_2 = vb * T
d_2 = velocity_b*T
# d_3 = vc(T+trec)
d_3 = velocity_y*(T+reaction_time)
# osd = d_1+d_2+d_3+2s
osd = int(d_1+d_2+d_3+(2*s))
# time
t_1 = np.sqrt(2*s/acceleration_r)
# initial position
current_x_r = 0
current_y_r = 1
#sidebar for osd
overtaking_distance = st.sidebar.slider("Initial distance between red and yellow car (m)", min_value=osd-300, max_value=osd+300, value=osd, step=1)

# Display calculated metrics in columns
col1, col2 = st.columns(2)
col1.metric("minimum Overtaking Sight Distance (m)", f"{osd:.0f} m")
col2.metric("Period (T)", f"{T+reaction_time:.2f} s")

# 5. Live Animation Controls
st.subheader("Live Simulation")
start_button = st.button("▶ Run / Reset Animation")
# create space for the graph plotting
plot_spot = st.empty()
time_spot = st.empty()

# 6. Animation Loop
if start_button:
    start_time = time.time()

    # Run the animation loop for 10 seconds
    while time.time() - start_time < T+reaction_time+5:
        # Calculate elapsed simulation time based on speed
        # Calculate elapsed simulation time based on speed
        t = (time.time() - start_time)
        time_spot.markdown(f" **Elapsed Time:** `{t:.2f}` seconds")
        
        # คำนวณตำแหน่งรถน้ำเงิน (Blue) และรถเหลือง (Yellow) ตามเวลา t
        current_x_b = s + velocity_b * t
        current_x_y = overtaking_distance - (velocity_y * t)
        
        # กำหนดช่วงเวลา (Time Checkpoints) สำหรับรถสีแดง
        t_reaction = reaction_time                             
        t_lane_1 = t_reaction + 1.5                             
        t_overtake_end = t_reaction + T                         
        t_lane_2 = t_overtake_end + 1.5                         

        # คำนวณตำแหน่งรถแดง (Red) โดยขึ้นตรงกับเวลา t เท่านั้น
        
        # เฟส 1: ช่วง Reaction Time (วิ่งความเร็วเท่ารถน้ำเงิน อยู่เลนซ้าย y=1)
        if t < t_reaction:
            current_x_r = velocity_b * t
            current_y_r = 1.0
            
        # เฟส 2: กำลังเริ่มเร่ง และเบี่ยงขวาออกไปเลนสวน (y ดิ่งลงจาก 1 ไป -1)
        elif t_reaction <= t < t_lane_1:
            t_delta = t - t_reaction
            current_x_r = (velocity_b * t_reaction) + (velocity_b * t_delta) + (0.5 * acceleration_r * (t_delta**2))
            # คำนวณแกน y ให้ค่อยๆ ลาดลงตามเวลาจาก 1 ไป -1
            current_y_r = 1.0 - 2.0 * ((t - t_reaction) / (t_lane_1 - t_reaction))
            
        # เฟส 3: วิ่งเร่งแซงเต็มกำลังในเลนขวาสวนเลน (y คงที่ที่ -1)
        elif t_lane_1 <= t < t_overtake_end:
            t_delta = t - t_reaction
            current_x_r = (velocity_b * t_reaction) + (velocity_b * t_delta) + (0.5 * acceleration_r * (t_delta**2))
            current_y_r = -1.0
            
        # เฟส 4: แซงพ้นแล้ว กำลังเบี่ยงกลับเข้าเลนซ้าย (y ไต่ขึ้นจาก -1 ไป 1)
        elif t_overtake_end <= t < t_lane_2:
            t_delta = t - t_reaction
            current_x_r = (velocity_b * t_reaction) + (velocity_b * t_delta) + (0.5 * acceleration_r * (t_delta**2))
            # คำนวณแกน y ให้ค่อยๆ ไต่กลับขึ้นมาตามเวลาจาก -1 ไป 1
            current_y_r = -1.0 + 2.0 * ((t - t_overtake_end) / (t_lane_2 - t_overtake_end))
            
        # เฟส 5: แซงเสร็จสมบูรณ์ วิ่งความเร็วปลายต่อบนเลนซ้ายปกติ (y คงที่ที่ 1)
        else:
            t_delta = t - t_reaction
            current_x_r = (velocity_b * t_reaction) + (velocity_b * t_delta) + (0.5 * acceleration_r * (t_delta**2))
            current_y_r = 1.0

        # Create the Matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 2))

        # Draw the road
        ax.axhline(y=1, color='grey', linestyle='--', linewidth=1)
        ax.axhline(y=-1, color='grey', linestyle='--', linewidth=1)

        # Draw the mass 
        ax.plot(current_x_b, 1, marker='>', markersize=13, color='b')
        ax.plot(current_x_y, -1, marker='<', markersize=13, color='y')
        ax.plot(current_x_r, current_y_r, marker='>', markersize=13, color='r')

        # Graph styling
        ax.set_xlim(0, 1.25*overtaking_distance)
        ax.set_ylim(-3, 3)
        ax.set_ylabel("Lane")
        ax.set_xlabel("Displacement (m)")
        ax.grid(True, linestyle=':', alpha=0.6)

        # Render the plot inside the placeholder
        plot_spot.pyplot(fig)

        # Close the figure to free up memory
        plt.close(fig)

        # Short pause to control frame rate (~30 FPS)
        time.sleep(0.15)

    st.success("Simulation finished!")
else:
    st.info("Click the 'Run / Reset Animation' button to start the simulation.")
        

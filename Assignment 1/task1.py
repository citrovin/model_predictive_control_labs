import numpy as np

from astrobee_1d import Astrobee
from controller import Controller
from simulation import EmbeddedSimEnvironment

import casadi as ca

# Create pendulum and controller objects
abee = Astrobee(h=0.1)
ctl = Controller()

# Get the system discrete-time dynamics
A, B = abee.one_axis_ground_dynamics()
Cc = ca.DM.zeros(1, 2)
Dc = ca.DM.zeros(1, 1)
Cc[0,0] = 1

Cc = np.asarray(Cc)
Dc = np.asarray(Dc)
Cc = [1,0]
Dc = [0]

# TODO: Get the discrete time system with casadi_c2d
Ad, Bd, Cd, Dd = abee.casadi_c2d(A, B, Cc, Dc)
print("Ad =", Ad)
print("Bd =", Bd)
print("Cd = ", Cd)

abee.set_discrete_dynamics(Ad, Bd)

# Plot poles and zeros
sys = abee.poles_zeros(Ad, Bd, Cd, Dd)

# Get control gains
ctl.set_system(Ad, Bd, Cd, Dd)
K = ctl.get_closed_loop_gain()

# Set the desired reference based on the dock position and zero velocity on docked position
dock_target = np.array([[0.0, 0.0]]).T
ctl.set_reference(dock_target)

# Starting position
x0 = [1.0, 0.0]

# Initialize simulation environment
sim_env = EmbeddedSimEnvironment(model=abee,
                                 dynamics=abee.linearized_discrete_dynamics,
                                 controller=ctl.control_law,
                                 time=40.0)
t, y, u = sim_env.run(x0)
sim_env.visualize()

# Disturbance effect
abee.set_disturbance()
sim_env = EmbeddedSimEnvironment(model=abee,
                                 dynamics=abee.linearized_discrete_dynamics,
                                 controller=ctl.control_law,
                                 time=40.0)
t, y, u = sim_env.run(x0)
sim_env.visualize()

# Activate feed-forward gain
ctl.activate_integral_action(dt=0.1, ki=0.045)
t, y, u = sim_env.run(x0)
sim_env.visualize()

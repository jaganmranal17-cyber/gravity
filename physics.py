import numpy as np

def get_acceleration(pos, masses, G):
    """
    Vectorized acceleration calculation.
    pos: (N, 3) array of positions
    masses: (N,) array of masses
    """
    num_bodies = len(masses)
    acceleration = np.zeros((num_bodies, 3))
    
    for i in range(num_bodies):
        diff = pos - pos[i]
        dist_sq = np.sum(diff**2, axis=1)
        
        # Avoid division by zero for the body itself
        dist_sq[i] = np.inf
        
        # Acceleration: a = G * m_k * r_ik / |r_ik|^3
        dist = np.sqrt(dist_sq)
        # Use a small epsilon to avoid singularities
        mag = G * masses / (dist_sq * dist + 1e-10) 
        
        acceleration[i] = np.sum(diff * mag[:, np.newaxis], axis=0)
        
    return acceleration

def rk4_step(data, dt, G):
    """
    4th Order Runge-Kutta Integrator.
    data: list of [mass, [x, vx], [y, vy], [z, vz], trail, name, color]
    """
    masses = np.array([p[0] for p in data])
    pos = np.array([[p[1][0], p[2][0], p[3][0]] for p in data])
    vel = np.array([[p[1][1], p[2][1], p[3][1]] for p in data])
    
    # k1
    a1 = get_acceleration(pos, masses, G)
    v1 = vel
    
    # k2
    a2 = get_acceleration(pos + v1 * dt/2, masses, G)
    v2 = vel + a1 * dt/2
    
    # k3
    a3 = get_acceleration(pos + v2 * dt/2, masses, G)
    v3 = vel + a2 * dt/2
    
    # k4
    a4 = get_acceleration(pos + v3 * dt, masses, G)
    v4 = vel + a3 * dt
    
    # Combine (weighted average)
    new_pos = pos + (dt/6) * (v1 + 2*v2 + 2*v3 + v4)
    new_vel = vel + (dt/6) * (a1 + 2*a2 + 2*a3 + a4)
    
    # Update data structure
    for i in range(len(data)):
        data[i][1] = [float(new_pos[i, 0]), float(new_vel[i, 0])]
        data[i][2] = [float(new_pos[i, 1]), float(new_vel[i, 1])]
        data[i][3] = [float(new_pos[i, 2]), float(new_vel[i, 2])]
        
    return data

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
GLOBAL_SCALE = 0.6
np.random.seed(42)
def rotation_matrix_from_z_to(n):
    n = n / np.linalg.norm(n)
    z = np.array([0.0, 0.0, 1.0])
    v = np.cross(z, n)
    c = np.dot(z, n)
    s = np.linalg.norm(v)
    if s < 1e-6:
        if c > 0:
            return np.eye(3)
        else:
            return np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    R = np.eye(3) + vx + vx @ vx * ((1 - c) / (s * s))
    return R
# inward 参数控制向内卷 ---
def create_petal_mesh(u_start, u_end, num_points, scale, tip_strength, base_strength, openness, inward):
    u = np.linspace(u_start, u_end, 100)
    v = np.linspace(-np.pi/2, np.pi/2, 30)
    U, V = np.meshgrid(u, v)
    # X轴公式：加入向内卷曲项 inward * (U**2) * scale
    # 根部(U=0)不动，越靠近尖端(U=1)向内收缩得越厉害
    X = (U * 1.6 * scale + 0.03 - inward * (U ** 2) * scale) * GLOBAL_SCALE
    Y = np.sin(np.pi * U) ** 0.8 * 0.42 * np.sin(V) * scale * GLOBAL_SCALE
    base_curve = -np.sin(np.pi * U) * base_strength * np.cos(V)
    lateral_curl = np.sin(np.pi * U) * 0.2 * (np.abs(np.sin(V)) ** 3)
    tip_curl = (U ** 2) * tip_strength
    z_slope = openness * U * 1.6 * scale
    Z = (z_slope + base_curve + lateral_curl + tip_curl) * scale * GLOBAL_SCALE
    return X, Y, Z, U, V
fig = plt.figure(figsize=(5, 6), dpi=100, facecolor='black')
ax = fig.add_subplot(111, projection='3d', facecolor='black')
ax.set_xlim(-0.7, 0.7)
ax.set_ylim(-0.7, 0.7)
ax.set_zlim(-0.5, 1.3)
ax.set_axis_off()
ax.grid(False)
# --- 四层参数 inward 值 (外层0，内层最大) ---
layers = [
    {'petals': 6, 'scale': 1.0,  'tip': 0.2, 'base': 0.1, 'openness': 0.0, 'alpha': 0.15, 'tip_alpha': 0.65, 'inward': 0.0},  # 最外层不卷
    {'petals': 6, 'scale': 0.75, 'tip': 0.5, 'base': 0.2, 'openness': 0.4, 'alpha': 0.25, 'tip_alpha': 0.50, 'inward': 0.1},  # 次外层微卷
    {'petals': 5, 'scale': 0.55, 'tip': 0.9, 'base': 0.3, 'openness': 0.9, 'alpha': 0.35, 'tip_alpha': 0.40, 'inward': 0.2},  # 内层明显卷
    {'petals': 4, 'scale': 0.35, 'tip': 1.4, 'base': 0.4, 'openness': 1.4, 'alpha': 0.45, 'tip_alpha': 0.30, 'inward': 0.35}  # 最内层卷得最深
]
P_surf = np.array([0.0, 0.0, 0.0])
n = np.array([0.0, 0.0, 1.0])
R = rotation_matrix_from_z_to(n)
all_p_x, all_p_y, all_p_z = [], [], []
base_sizes, phases = [], []
for layer in layers:
    num_petals = layer['petals']
    scale = layer['scale']
    alpha = layer['alpha']
    tip_alpha = layer['tip_alpha']
    base_strength = layer['base']
    tip_strength = layer['tip']
    openness = layer['openness']
    inward = layer['inward']
    base_color = np.array([1.0, 0.75, 0.85, alpha])
    tip_color = np.array([0.85, 0.05, 0.1, tip_alpha])
    # 传入 inward 参数
    X_petal, Y_petal, Z_petal, U, V = create_petal_mesh(0, 1, 100, scale, tip_strength, base_strength, openness, inward)
    t = (U - 0.6) / 0.4
    t = np.clip(t, 0, 1)
    t = t ** 1.5
    face_colors = np.zeros(U.shape + (4,))
    for i in range(4):
        face_colors[:, :, i] = base_color[i] * (1 - t) + tip_color[i] * t
    for i in range(num_petals):
        angle = i * (2 * np.pi / num_petals)
        X_rot = X_petal * np.cos(angle) - Y_petal * np.sin(angle)
        Y_rot = X_petal * np.sin(angle) + Y_petal * np.cos(angle)
        Z_rot = Z_petal
        points = np.stack([X_rot, Y_rot, Z_rot], axis=-1).reshape(-1, 3)
        points_world = points @ R.T + P_surf
        X_final = points_world[:, 0].reshape(X_petal.shape)
        Y_final = points_world[:, 1].reshape(X_petal.shape)
        Z_final = points_world[:, 2].reshape(X_petal.shape)
        ax.plot_surface(X_final, Y_final, Z_final,
                        facecolors=face_colors,
                        rstride=2, cstride=2,
                        edgecolor=(1.0, 0.6, 0.8, 0.1),
                        linewidth=0.1,
                        antialiased=True, shade=False)
        v_indices = range(0, 30, 4)
        for v_idx in v_indices:
            x_line = X_final[v_idx, :]
            y_line = Y_final[v_idx, :]
            z_line = Z_final[v_idx, :]
            u_line = U[v_idx, :]
            ax.plot(x_line, y_line, z_line, color=(1.0, 0.7, 0.85, 0.9), linewidth=0.1)
            tip_mask = u_line > 0.7
            ax.plot(x_line[tip_mask], y_line[tip_mask], z_line[tip_mask],
                    color=(1.0, 0.2, 0.6, 0.6), linewidth=0.4)
            ax.plot(x_line[tip_mask], y_line[tip_mask], z_line[tip_mask],
                    color=(1.0, 0.9, 1.0, 0.9), linewidth=0.15)
        num_particles = 4
        u_p = np.random.uniform(0.6, 1.0, num_particles)
        v_p = np.random.uniform(-np.pi/2, np.pi/2, num_particles)
        # 匹配向内卷的X轴公式
        pX = (u_p * 1.6 * scale + 0.03 - inward * (u_p ** 2) * scale) * GLOBAL_SCALE
        pY = np.sin(np.pi * u_p) ** 0.8 * 0.42 * np.sin(v_p) * scale * GLOBAL_SCALE
        p_base_curve = -np.sin(np.pi * u_p) * base_strength * np.cos(v_p)
        p_lateral_curl = np.sin(np.pi * u_p) * 0.2 * (np.abs(np.sin(v_p)) ** 3)
        p_tip_curl = (u_p ** 2) * tip_strength
        p_z_slope = openness * u_p * 1.6 * scale
        pZ = (p_z_slope + p_base_curve + p_lateral_curl + p_tip_curl) * scale * GLOBAL_SCALE
        pX_rot = pX * np.cos(angle) - pY * np.sin(angle)
        pY_rot = pX * np.sin(angle) + pY * np.cos(angle)
        p_points = np.stack([pX_rot, pY_rot, pZ], axis=-1)
        p_world = p_points @ R.T + P_surf
        all_p_x.extend(p_world[:, 0])
        all_p_y.extend(p_world[:, 1])
        all_p_z.extend(p_world[:, 2])
        for _ in range(num_particles):
            base_sizes.append(np.random.uniform(0.05, 0.8))
            phases.append(np.random.uniform(0, 2 * np.pi))
all_p_x = np.array(all_p_x)
all_p_y = np.array(all_p_y)
all_p_z = np.array(all_p_z)
base_sizes = np.array(base_sizes)
phases = np.array(phases)
# 花瓣内微尘闪烁
scat = ax.scatter(all_p_x, all_p_y, all_p_z, s=base_sizes, c='white', alpha=0.8)
# --- 花蕊 ---
start_center_local = np.array([0.0, 0.0, 0.0])
end_center_local = np.array([0.0, 0.0, 0.35 * GLOBAL_SCALE])
start_center = start_center_local @ R.T + P_surf
end_center = end_center_local @ R.T + P_surf
ax.plot([start_center[0], end_center[0]],
        [start_center[1], end_center[1]],
        [start_center[2], end_center[2]],
        color='#FFD700', linewidth=1.5)
STAMEN_HEIGHT = 0.35 * GLOBAL_SCALE
BASE_RADIUS = 0.05 * GLOBAL_SCALE
num_stamens = 40
angles = np.linspace(0, 2 * np.pi, num_stamens, endpoint=False)
for j in range(num_stamens):
    theta = angles[j]
    extent = np.random.uniform(0.05, 0.15) * GLOBAL_SCALE
    t_points = np.linspace(0, 1, 50)
    x_local = (BASE_RADIUS + extent * t_points) * np.cos(theta)
    y_local = (BASE_RADIUS + extent * t_points) * np.sin(theta)
    z_local = STAMEN_HEIGHT * (t_points ** 2)
    pts_local = np.stack([x_local, y_local, z_local], axis=-1)
    pts_world = pts_local @ R.T + P_surf
    ax.plot(pts_world[:, 0], pts_world[:, 1], pts_world[:, 2], color='#FFD700', linewidth=1.0)
    ax.scatter(pts_world[-1, 0], pts_world[-1, 1], pts_world[-1, 2], color='#CC8800', s=2)
def update(frame):
    azim = 60 + frame * 4.0
    ax.view_init(elev=25, azim=azim)
    sizes = base_sizes * (1 + 0.5 * np.sin(frame * 0.2 + phases))
    scat.set_sizes(sizes)
    colors = np.zeros((len(sizes), 4))
    colors[:, 0] = 1.0
    colors[:, 1] = 0.7 + 0.3 * np.abs(np.sin(frame * 0.3 + phases))
    colors[:, 2] = 0.85
    colors[:, 3] = 1.0
    scat.set_facecolors(colors)
    return scat,
ani = FuncAnimation(fig, update, frames=200, interval=50, blit=False)
plt.show()

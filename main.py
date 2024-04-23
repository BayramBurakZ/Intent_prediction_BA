import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

path_right = r'trajectories\right_hand\right_1.csv'
#path_left = r'trajectories\left_hand\left_1.csv'
df_right=pd.read_csv(path_right)
#df_left = pd.read_csv(path_left)

p_g1 = (0.125, 0.149)
p_g2 = (0.189, 0.149)
p_n = (0.138, -0.020)
p_p = (0.123, -0.045)

#plot sample
x = [p_g1[0], p_g2[0], p_n[0], p_p[0]]
y = [p_g1[1], p_g2[1], p_n[1], p_p[1]]
def prediction_model(p_previous, p_g, ):
    a_0 = p_previous
    #a_1 = p_prime
    a_2 = 1.5*p_g - 1.5*p_previous # -1.5p_n1 prim
    a_3 = -0.5*p_g + 0.5*p_previous # + e0.5p_n1 prim

def plot(x, y):
    # Plotting the points
    plt.plot(x, y, 'ro')  # 'ro' for red circles
    plt.title('Sample Point Plot')
    plt.xlabel('x values')
    plt.ylabel('y values')

    # Show plot
    plt.show()

plot(x,y)
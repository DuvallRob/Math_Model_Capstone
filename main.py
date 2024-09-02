import pandas as pd
import numpy as np
import tensorflow as tf
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Load the fusion and fission datasets
fusion_data = pd.read_csv('fusion_data.csv')
fission_data = pd.read_csv('fission_data.csv')

# Use the 'DATA (B) 0.1' column as the neutron yield and cross-section data
fusion_neutron_yield = fusion_data['DATA (B) 0.1']
fission_cross_section = fission_data['DATA (B) 0.1']

# Prepare training data by selecting relevant columns (e.g., energy and projections)
# Ensure all columns contain valid numerical data
X_fusion = fusion_data[['EN-CM (EV) 1.1']].values  # Using energy columns
X_fission = fission_data[['EN-MIN (EV) 1.2']].values

y_fusion = fusion_neutron_yield.values
y_fission = fission_cross_section.values

# Define the model creation function
def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(1,)),  # Adjust input shape to match X data
        tf.keras.layers.Dense(10, activation='relu'),
        tf.keras.layers.Dense(10, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# Initialize models
fusion_model = create_model()
fission_model = create_model()

# Train models using fusion and fission data
fusion_model.fit(X_fusion, y_fusion, epochs=10, verbose=1)
fission_model.fit(X_fission, y_fission, epochs=10, verbose=1)

# Example of how you could integrate predictions into a solver for neutron population dynamics
def neutron_dynamics(t, N):
    N = np.array(N).reshape(-1, 1)  # Reshape N to fit the expected input dimensions for prediction
    inputs_fusion = np.array([[1.0e6]])  # Example input for fusion (energy)
    inputs_fission = np.array([[1.0e6]])  # Example input for fission (energy)

    # Use the trained models to predict neutron yields from fusion and fission
    N_fusion = fusion_model.predict(inputs_fusion)[0]
    N_fission = fission_model.predict(inputs_fission)[0]

    return [N_fusion + N_fission]

# Time span for the simulation
t_span = [0, 50]  # Time range for the simulation
t_eval = np.linspace(0, 50, 500)

# Solve the differential equation
sol = solve_ivp(neutron_dynamics, t_span, [1e10], method='RK45', t_eval=t_eval)

# Plot the results
plt.plot(sol.t, sol.y[0], label='Neutron Population Over Time')
plt.title('Neutron Population Dynamics in a Hybrid Reactor')
plt.xlabel('Time (s)')
plt.ylabel('Neutron Population')
plt.legend()
plt.show()

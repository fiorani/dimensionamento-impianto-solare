import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt

# Consumi
demand = 45  # Domanda energetica in kW che vale al giorno
grid_price_kw = 0.30  # Tariffe al kW dell'energia elettrica
grid_price_sell_kw = 0.10  # Tariffe al kW dell'energia elettrica venduta

# Sistema solare
solar_max_kwh  = 6  # Massima potenza in kW generabile dai pannelli solari
solar_degradation = 0.05  # Fattore di degrado annuale dei pannelli solari
solar_price_kw = 500  # Prezzo al kW del sistema solare

# Batteria
storage_max_kw  = 10  # Capacità in kW massima della batteria
storage_price_kw = 1000  # Prezzo al kW della batteria
storage_degradation = 0.10  # Fattore di degrado annuale dello stoccaggio dell'energia

# Durata
life = 10  # Anni di vita per la batteria e il sistema solare

# Curva impianto solare
hours = np.arange(0, 24)
solar_curve = solar_max_kwh  * np.sin(np.pi * (hours - 7) / 12)  # Funzione sinusoidale per rappresentare la generazione solare
solar_curve[solar_curve < 0] = 0  # Imposta a 0 la generazione solare quando è negativa

# Curva batteria
battery_energy = np.zeros_like(solar_curve)  # Inizializza l'array per l'energia accumulata nella batteria
for i in range(1, len(hours)):
    excess_energy = max(solar_curve[i] - demand / 24, 0)  # Energia in eccesso rispetto alla domanda
    deficit_energy = max(demand / 24 - solar_curve[i], 0)  # Energia mancante rispetto alla domanda
    battery_energy[i] = battery_energy[i-1] + excess_energy - deficit_energy
    battery_energy[i] = max(0, min(battery_energy[i], storage_max_kw ))

# Plot della curva solare, della curva della batteria e della domanda energetica
plt.figure(figsize=(10, 6))
plt.plot(hours, solar_curve, label="Energia prodotta")
plt.plot(hours, battery_energy, label="Batteria")
plt.plot(hours, np.full_like(hours, demand)/24, label="Consumo")
plt.xlabel("Ore del giorno")
plt.ylabel("Potenza (kW)")
plt.legend()
plt.grid(True)
plt.show()

#impianto solare
energy_generated = np.sum(solar_curve)*365* life
energy_used = np.sum(np.minimum(solar_curve, demand/24))*365* life
energy_sell= energy_generated-energy_used
energy_consu=demand *365* life
solar_lifetime_cost = grid_price_kw*energy_used +  grid_price_sell_kw*energy_sell -(solar_max_kwh*solar_price_kw)
grid_energy_cost = - grid_price_kw * energy_consu
print("Energia generata dall'impianto solare:", energy_generated)
print("Energia usata dall'impianto solare:", energy_used)
print("Energia venduta dall'impianto solare:", energy_sell)
print("risparmio dell'energia generata dall'impianto solare:", solar_lifetime_cost)
print("Costo dell'energia acquistata dalla rete elettrica:", grid_energy_cost)
if solar_lifetime_cost > grid_energy_cost:
    print("Conviene l'installazione dell'impianto solare.")
else:
    print("Non conviene l'installazione dell'impianto solare.")
    
    
#impianto solare con accumolo
storage_energy_used = np.sum(np.minimum(solar_curve+battery_energy, demand/24))*365* life
storage_energy_sell= energy_generated-storage_energy_used
storage_solar_lifetime_cost = grid_price_kw*storage_energy_used +  grid_price_sell_kw*storage_energy_sell -(storage_max_kw*storage_price_kw)-(solar_max_kwh*solar_price_kw)
print("Energia usata dall'impianto solare:", storage_energy_used)
print("Energia venduta dall'impianto solare:", storage_energy_sell)
print("risparmio dell'energia generata dall'impianto solare con accumolo:", storage_solar_lifetime_cost)
if storage_solar_lifetime_cost > grid_energy_cost:
    print("Conviene l'installazione dell'impianto solare con accumolo.")
else:
    print("Non conviene l'installazione dell'impianto solare con accumolo.")

# Definizione della funzione obiettivo per la programmazione lineare
def objective(x):
    solar_cost = x[0] * solar_price_kw
    storage_cost = x[1] * storage_price_kw
    grid_cost = x[2] * grid_price_kw
    return solar_cost + storage_cost + grid_cost

# Definizione dei vincoli per la programmazione lineare
def constraint(x):
    solar_cost = x[0] * solar_price_kw
    storage_cost = x[1] * storage_price_kw
    grid_cost = x[2] * grid_price_kw
    energy_generated = x[0] * solar_max_kwh * 365 * life
    energy_used = x[0] * np.sum(np.minimum(solar_curve, demand/24)) * 365 * life
    energy_sell = energy_generated - energy_used
    return [energy_generated, energy_used, energy_sell, solar_cost, storage_cost, grid_cost]

# Risoluzione del problema di programmazione lineare
res = linprog(c=[solar_price_kw, storage_price_kw, grid_price_kw], A_ub=[[-1, 0, 0], [0, -1, 0], [0, 0, -1]], b_ub=[0, 0, 0], A_eq=[[solar_max_kwh * 365 * life, 0, 0], [1, 1, 1], [1, 1, 1], [0, 1, 0]], b_eq=[demand * 365 * life, solar_max_kwh * 365 * life, storage_max_kw * 365 * life, 0], bounds=[(0, solar_max_kwh), (0, storage_max_kw), (0, np.inf)])    
# Estrazione dei risultati
solar_installation = res.x[0]
battery_installation = res.x[1]
total_cost = res.fun

# Stampa dei risultati
print("Impianto solare installato:", solar_installation)
print("Batteria installata:", battery_installation)
print("Costo totale:", total_cost)
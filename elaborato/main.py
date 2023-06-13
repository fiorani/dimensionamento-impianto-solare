import numpy as np
from scipy.optimize import linprog
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Consumi
demand = 45  # Domanda energetica in kW che vale al giorno
grid_price_kw = 0.30  # Tariffe al kW dell'energia elettrica
grid_price_sell_kw = 0.05  # Tariffe al kW dell'energia elettrica venduta

# Sistema solare
solar_max_kwh  = 6  # Massima potenza in kW generabile dai pannelli solari
solar_degradation = 0.05  # Fattore di degrado annuale dei pannelli solari
solar_price_kw = 50  # Prezzo al kW del sistema solare

# Batteria
storage_max_kw  = 10  # Capacità in kW massima della batteria
storage_price_kw = 10  # Prezzo al kW della batteria
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    

C_impianto = 1000  # Costo dell'impianto solare in euro/kW
C_batteria = 500   # Costo della batteria di accumulo in euro/kW
C_elettrica = 0.3  # Costo dell'energia elettrica dalla rete in euro/kWh
E_consumo = 20    # Consumo energetico giornaliero dell'abitazione in kWh
p_max_impianto = 6  # Potenza massima dell'impianto solare in kW
p_max_batteria = 10  # Capacità massima della batteria di accumulo in kW

def objective(x, C_impianto, C_batteria, C_elettrica, E_consumo):
    P_impianto, P_batteria = x
    
    hours = np.arange(0, 24)
    solar_curve = P_impianto * np.sin(np.pi * (hours - 7) / 12)  # Funzione sinusoidale per rappresentare la generazione solare
    solar_curve = np.maximum(solar_curve, 0)  # Imposta a 0 la generazione solare quando è negativa
    battery_energy = np.zeros_like(solar_curve)  # Inizializza l'array per l'energia accumulata nella batteria
    for i in range(1, len(hours)):
        excess_energy = max(solar_curve[i] - E_consumo / 24, 0)  # Energia in eccesso rispetto alla domanda
        deficit_energy = max(E_consumo / 24 - solar_curve[i], 0)  # Energia mancante rispetto alla domanda
        battery_energy[i] = battery_energy[i-1] + excess_energy - deficit_energy
        battery_energy[i] = max(0, min(battery_energy[i], P_batteria))
    E_impianto_generata = np.sum(solar_curve)  # Energia generata durante il giorno
    E_impianto_usata = np.sum(np.minimum(solar_curve, E_consumo / 24))  # Energia usata dall'impianto durante il giorno
    E_impianto_venduta = E_impianto_generata - E_impianto_usata  # Energia venduta dall'impianto durante il giorno
    E_batteria_usata = np.sum(np.minimum(solar_curve + battery_energy, E_consumo / 24))  # Energia usata dalla batteria durante il giorno
    
    plt.figure(figsize=(10, 6))
    plt.plot(hours, solar_curve, label="Energia prodotta")
    plt.plot(hours, battery_energy, label="Batteria")
    plt.plot(hours, np.full_like(hours, E_consumo)/24, label="Consumo")
    plt.xlabel("Ore del giorno")
    plt.ylabel("Potenza (kW)")
    plt.legend()
    plt.grid(True)
    plt.show()
    costo_totale = C_impianto * P_impianto + C_batteria * P_batteria + (E_consumo - E_impianto_usata + E_batteria_usata + E_impianto_venduta) * C_elettrica
    print("Costo totale iterazione:", costo_totale, "euro potenza impianto",P_impianto,"potenza batteria",P_batteria)
    return costo_totale

# Vincoli
def constraint1(x):
    P_impianto, _ = x
    return P_impianto - p_max_impianto

def constraint2(x):
    P_impianto, P_batteria = x
    return P_batteria - p_max_batteria

def constraint3(x):
    P_impianto, P_batteria = x
    return [P_impianto, P_batteria]

# Vincoli
cons = [{'type': 'ineq', 'fun': constraint1},
        {'type': 'ineq', 'fun': constraint2},
        {'type': 'ineq', 'fun': constraint3}]

# Valori iniziali delle variabili decisionali
x0 = [0, 0]

# Ottimizzazione
res = minimize(objective, x0, args=(C_impianto, C_batteria, C_elettrica, E_consumo),
               constraints=cons, options={'disp': True})

# Risultati
print("Stato dell'ottimizzazione:", res.success)
print("Messaggio dell'ottimizzazione:", res.message)
print("Potenza dell'impianto solare ottimale:", res.x[0], "kW")
print("Potenza della batteria di accumulo ottimale:", res.x[1], "kW")
print("Costo totale dell'energia elettrica:", res.fun, "euro")



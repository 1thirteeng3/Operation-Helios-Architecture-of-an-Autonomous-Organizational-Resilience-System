"""
backpressure_sim.py
--------------------

Simulação de filas e backpressure utilizando a biblioteca SimPy.  Esta função
modela um sistema de chegada de requisições (clientes) com taxa de chegada
exponencial e tempo de serviço exponencial.  Pode-se ajustar a capacidade do
servidor (número de atendentes) para ver como o backlog evolui e medir o
tempo médio de espera.

Exemplo:

```python
from sim.backpressure_sim import simulate_backpressure
metrics = simulate_backpressure(arrival_rate=5.0, service_rate=6.0, capacity=2, sim_time=1000)
print(metrics)
```

"""

import random
from typing import Dict

import simpy


def simulate_backpressure(arrival_rate: float, service_rate: float, capacity: int, sim_time: float) -> Dict[str, float]:
    """Executa uma simulação de fila M/M/c.

    Args:
        arrival_rate: taxa média de chegadas (lambda) por unidade de tempo.
        service_rate: taxa média de atendimento (mu) por atendente.
        capacity: número de atendentes (servidores) simultâneos.
        sim_time: tempo total de simulação.

    Returns:
        Dicionário com métricas: tempo médio de espera, tempo máximo de espera,
        número total de requisições processadas e número total de rejeições (caso
        a fila esteja cheia; neste modelo não há limite de fila, portanto
        rejeições = 0).
    """
    env = simpy.Environment()
    server = simpy.Resource(env, capacity)
    wait_times = []
    completed = 0

    def arrival_generator():
        nonlocal completed
        while True:
            # aguarda tempo entre chegadas
            yield env.timeout(random.expovariate(arrival_rate))
            env.process(handle_request())

    def handle_request():
        arrive_time = env.now
        with server.request() as req:
            yield req
            wait = env.now - arrive_time
            wait_times.append(wait)
            # tempo de serviço exponencial
            service_time = random.expovariate(service_rate)
            yield env.timeout(service_time)
            completed += 1

    env.process(arrival_generator())
    env.run(until=sim_time)
    avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0.0
    max_wait = max(wait_times) if wait_times else 0.0
    return {
        "avg_wait": avg_wait,
        "max_wait": max_wait,
        "completed": completed,
        "dropped": 0,
    }
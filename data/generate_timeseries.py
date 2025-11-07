#!/usr/bin/env python3
"""
generate_timeseries.py
----------------------

Este script gera dados sintéticos de telemetria em formato de séries temporais.  Cada linha representa
o estado de um nó em um timestamp específico, incluindo métricas de CPU, memória, latência e taxa de
requisições.  Os dados são gerados a partir de processos AR(1) (autoregressivos) perturbados por
ruído Gaussiano e eventos de pico gerados por um processo de Poisson.  Esses picos simulam
falhas em cascata ou cargas inesperadas que impactam múltiplos nós de forma correlacionada.

Uso:
    python generate_timeseries.py --nb-nodes 20 --duration-hours 12 --frequency-sec 60 \
        --load-profile normal --output timeseries.csv

Argumentos:
    --nb-nodes         Quantidade de nós a serem simulados (padrão: 10)
    --duration-hours   Duração total da série em horas (padrão: 24)
    --frequency-sec    Intervalo entre medições em segundos (padrão: 60)
    --load-profile     Perfil de carga: "low", "normal" ou "high" (define taxas de spikes)
    --output           Caminho para o arquivo CSV de saída (padrão: timeseries.csv)
    --seed             Semente opcional para reprodução determinística dos resultados

O arquivo resultante conterá as colunas:
    timestamp (ISO8601), node_id (int), metric_cpu (float), metric_mem (float),
    latency_ms (float), request_rate (float)
"""

import argparse
import csv
import datetime as _dt
import math
import os
import random
from typing import List, Tuple, Dict, Set


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerador de séries temporais de telemetria")
    parser.add_argument("--nb-nodes", type=int, default=10, help="Número de nós a serem simulados")
    parser.add_argument("--duration-hours", type=float, default=24.0, help="Duração em horas da série")
    parser.add_argument(
        "--frequency-sec", type=int, default=60, help="Intervalo de amostragem em segundos"
    )
    parser.add_argument(
        "--load-profile",
        type=str,
        choices=["low", "normal", "high"],
        default="normal",
        help="Perfil de carga que determina a frequência e intensidade de picos",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="timeseries.csv",
        help="Caminho do arquivo CSV a ser gerado",
    )
    parser.add_argument("--seed", type=int, default=None, help="Semente para o gerador aleatório")
    return parser.parse_args()


def generate_spike_schedule(total_steps: int, rate: float) -> List[int]:
    """Gera uma lista de índices de tempo (steps) onde ocorrerão picos.

    A taxa é interpretada como número esperado de eventos por hora.  Os tempos
    inter-arrivais são gerados por uma distribuição exponencial e convertidos para
    índices discretos.

    Args:
        total_steps: número total de steps (pontos de amostragem) na simulação.
        rate: taxa de eventos por hora.

    Returns:
        Uma lista ordenada de steps (inteiros) onde ocorrem picos.
    """
    spike_times: List[int] = []
    if rate <= 0:
        return spike_times
    # intervalo médio entre eventos em horas e depois convertido para steps
    # densidade lambda = eventos por hora; interarrivals ~ Exp(lambda)
    current_time = 0.0
    while True:
        # interarrival time in hours
        u = random.random()
        interarrival_hours = -math.log(1 - u) / rate
        current_time += interarrival_hours
        # convert to step index
        step = int(current_time * 3600)  # horas -> segundos
        # para mapear para steps de frequency_sec, faremos arredondamento após a geração
        spike_times.append(step)
        if step >= total_steps:
            break
    # filtra eventos que caíram fora do range e converte para steps discretizados
    return [min(int(t), total_steps - 1) for t in spike_times if t < total_steps]


def generate_time_series(
    nb_nodes: int,
    duration_hours: float,
    frequency_sec: int,
    load_profile: str,
    seed: int = None,
) -> List[Tuple[str, int, float, float, float, float]]:
    """Gera dados de telemetria para todos os nós.

    Retorna uma lista de tuplas com os campos:
        (timestamp_iso, node_id, cpu, mem, latency_ms, request_rate)
    """
    if seed is not None:
        random.seed(seed)
    # define parâmetros baselines por nó
    baselines = []
    for _ in range(nb_nodes):
        baseline_cpu = random.uniform(30.0, 70.0)  # percentual
        baseline_mem = random.uniform(40.0, 80.0)  # percentual
        baseline_latency = random.uniform(10.0, 100.0)  # ms
        baseline_req = random.uniform(50.0, 150.0)  # requests/s
        baselines.append((baseline_cpu, baseline_mem, baseline_latency, baseline_req))
    # define AR(1) coeficientes
    phi_cpu = 0.95
    phi_mem = 0.93
    phi_latency = 0.90
    phi_req = 0.92
    # define desvio padrão do ruído
    noise_cpu = 2.0
    noise_mem = 3.0
    noise_latency = 5.0
    noise_req = 10.0
    # define intensidade das spikes e taxa
    if load_profile == "low":
        spike_rate = 0.5  # eventos por hora
        amp_cpu = (10.0, 20.0)
        amp_mem = (15.0, 25.0)
        amp_latency = (30.0, 60.0)
        amp_req = (-20.0, -40.0)
    elif load_profile == "high":
        spike_rate = 2.0
        amp_cpu = (25.0, 40.0)
        amp_mem = (30.0, 45.0)
        amp_latency = (80.0, 200.0)
        amp_req = (-60.0, -120.0)
    else:  # normal
        spike_rate = 1.0
        amp_cpu = (15.0, 30.0)
        amp_mem = (20.0, 35.0)
        amp_latency = (50.0, 120.0)
        amp_req = (-40.0, -80.0)
    # calcula quantidade total de steps
    total_steps = int((duration_hours * 3600) / frequency_sec)
    # gera horários de spikes globais (em segundos, para depois mapear a steps)
    spike_times_sec = generate_spike_schedule(total_steps, rate=spike_rate)
    # converte para steps discretos
    spike_steps: Set[int] = set(int(t / frequency_sec) for t in spike_times_sec if t >= 0)
    # define quais nós são afetados em cada spike
    # cria lista de pares (step, conjunto de nós, variação por métrica)
    spike_events: Dict[int, Dict[int, Tuple[float, float, float, float]]] = {}
    for step in spike_steps:
        impacted_nodes = set()
        # seleciona fração de nós afetados aleatoriamente (30 a 70%)
        frac = random.uniform(0.3, 0.7)
        k = max(1, int(frac * nb_nodes))
        impacted_nodes = set(random.sample(range(nb_nodes), k))
        # define amplitude do pico para cada métrica
        cpu_amp = random.uniform(*amp_cpu)
        mem_amp = random.uniform(*amp_mem)
        latency_amp = random.uniform(*amp_latency)
        req_amp = random.uniform(*amp_req)
        for node in impacted_nodes:
            spike_events.setdefault(step, {})[node] = (
                cpu_amp * random.uniform(0.8, 1.2),
                mem_amp * random.uniform(0.8, 1.2),
                latency_amp * random.uniform(0.8, 1.2),
                req_amp * random.uniform(0.8, 1.2),
            )
    # inicializa estados com baseline
    states = []
    for baseline in baselines:
        states.append(list(baseline))  # [cpu, mem, latency, req]
    # define início da série
    start_time = _dt.datetime.utcnow()
    # guarda resultados
    records: List[Tuple[str, int, float, float, float, float]] = []
    for step in range(total_steps):
        ts = start_time + _dt.timedelta(seconds=step * frequency_sec)
        ts_iso = ts.replace(microsecond=0).isoformat() + "Z"
        # verifica se existe evento de pico neste step
        event = spike_events.get(step)
        for node_id in range(nb_nodes):
            baseline_cpu, baseline_mem, baseline_latency, baseline_req = baselines[node_id]
            cpu, mem, lat, req = states[node_id]
            # aplica dinâmica AR(1)
            cpu = baseline_cpu + phi_cpu * (cpu - baseline_cpu) + random.gauss(0, noise_cpu)
            mem = baseline_mem + phi_mem * (mem - baseline_mem) + random.gauss(0, noise_mem)
            lat = baseline_latency + phi_latency * (lat - baseline_latency) + random.gauss(0, noise_latency)
            req = baseline_req + phi_req * (req - baseline_req) + random.gauss(0, noise_req)
            # aplica evento de pico, se existir para este nó
            if event and node_id in event:
                delta_cpu, delta_mem, delta_lat, delta_req = event[node_id]
                cpu += delta_cpu
                mem += delta_mem
                lat += delta_lat
                req += delta_req
            # impede métricas negativas
            cpu = max(cpu, 0.0)
            mem = max(mem, 0.0)
            lat = max(lat, 0.0)
            req = max(req, 0.0)
            states[node_id] = [cpu, mem, lat, req]
            records.append((ts_iso, node_id, cpu, mem, lat, req))
    return records


def main() -> None:
    args = parse_args()
    records = generate_time_series(
        nb_nodes=args.nb_nodes,
        duration_hours=args.duration_hours,
        frequency_sec=args.frequency_sec,
        load_profile=args.load_profile,
        seed=args.seed,
    )
    # cria diretório se necessário
    out_path = args.output
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    # escreve CSV
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["timestamp", "node_id", "metric_cpu", "metric_mem", "latency_ms", "request_rate"]
        )
        for rec in records:
            writer.writerow(rec)
    print(f"Gerado arquivo com {len(records)} registros em {out_path}")


if __name__ == "__main__":
    main()
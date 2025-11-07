#!/usr/bin/env python3
"""
generate_transactions.py
------------------------

Este script gera dados sintéticos de eventos transacionais de recomendação.  Cada registro
corresponde a uma interação entre um usuário e um item (produto/conteúdo) em um instante
temporal, com uma pontuação contínua, um vetor de features e um rótulo binário opcional.
O objetivo é servir como base para treinamento e testes de modelos de recomendação,
detecção de drift e análises de eventos.

Uso:
    python generate_transactions.py --n-users 100 --n-items 1000 --n-records 20000 --output transactions.csv

Argumentos:
    --n-users        Número de usuários distintos (padrão: 100)
    --n-items        Número de itens distintos (padrão: 1000)
    --n-records      Número total de registros a serem gerados (padrão: 10000)
    --duration-hours Duração da janela temporal em horas (padrão: 1)
    --features       Número de features numéricas a gerar por registro (padrão: 3)
    --label-noise    Probabilidade de flipar o rótulo (padrão: 0.05)
    --output         Caminho do arquivo CSV de saída (padrão: transactions.csv)
    --seed           Semente opcional para reprodutibilidade

O arquivo produzido conterá as colunas:
    timestamp,user_id,item_id,score,<feature_1>,...,<feature_n>,label
"""

import argparse
import csv
import datetime as _dt
import math
import os
import random
from typing import List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerador de eventos de recomendação")
    parser.add_argument("--n-users", type=int, default=100, help="Número de usuários distintos")
    parser.add_argument("--n-items", type=int, default=1000, help="Número de itens distintos")
    parser.add_argument("--n-records", type=int, default=10000, help="Número de registros a gerar")
    parser.add_argument(
        "--duration-hours",
        type=float,
        default=1.0,
        help="Espalhar timestamps em uma janela de X horas",
    )
    parser.add_argument("--features", type=int, default=3, help="Número de features numéricas por registro")
    parser.add_argument(
        "--label-noise",
        type=float,
        default=0.05,
        help="Probabilidade de inverter o rótulo binário",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="transactions.csv",
        help="Caminho do arquivo CSV de saída",
    )
    parser.add_argument("--seed", type=int, default=None, help="Semente para reprodutibilidade")
    return parser.parse_args()


def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def main() -> None:
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    # gera pesos para features e bias global
    weights = [random.uniform(-2.0, 2.0) for _ in range(args.features)]
    global_bias = random.uniform(-0.5, 0.5)
    # bias por usuário e item para heterogeneidade
    user_bias = [random.uniform(-1.0, 1.0) for _ in range(args.n_users)]
    item_bias = [random.uniform(-1.0, 1.0) for _ in range(args.n_items)]
    base_time = _dt.datetime.utcnow()
    max_delta = args.duration_hours * 3600.0
    out_path = args.output
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["timestamp", "user_id", "item_id", "score"] + [f"feature_{i+1}" for i in range(args.features)] + ["label"]
        writer.writerow(header)
        for _ in range(args.n_records):
            # tempo
            delta_seconds = random.uniform(0, max_delta)
            ts = base_time + _dt.timedelta(seconds=delta_seconds)
            ts_iso = ts.replace(microsecond=0).isoformat() + "Z"
            # escolhe user e item
            user = random.randint(0, args.n_users - 1)
            item = random.randint(0, args.n_items - 1)
            # gera features contínuas (normal N(0,1))
            feats: List[float] = [random.gauss(0.0, 1.0) for _ in range(args.features)]
            # calcula score com modelo linear + logística para mapear 0-1
            linear_comb = sum(w * x for w, x in zip(weights, feats)) + global_bias + user_bias[user] + item_bias[item]
            prob = logistic(linear_comb)
            score = prob  # manter valor entre 0 e 1 como score contínuo
            # define label binário
            label = 1 if random.random() < prob else 0
            # aplica ruído no rótulo
            if random.random() < args.label_noise:
                label = 1 - label
            writer.writerow([ts_iso, user, item, round(score, 5)] + [round(feat, 5) for feat in feats] + [label])
    print(f"Gerado arquivo de transações com {args.n_records} linhas em {out_path}")


if __name__ == "__main__":
    main()
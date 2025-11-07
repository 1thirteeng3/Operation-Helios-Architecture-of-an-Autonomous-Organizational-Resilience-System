#!/usr/bin/env python3
"""
generate_logs.py
----------------

Este script sintetiza logs de aplicação e ingestão no formato JSON (um objeto por linha).  Os logs
são construídos a partir de um conjunto de serviços, níveis de severidade e mensagens pré-definidas,
com carimbos de tempo distribuídos ao longo de um intervalo especificado.  Alguns registros são
propositalmente malformados para testar a robustez de pipelines de logging.

Uso:
    python generate_logs.py --nb-logs 10000 --duration-hours 2 --output logs.jsonl

Argumentos:
    --nb-logs         Número total de registros de log a gerar (padrão: 1000)
    --duration-hours   Duração em horas sobre a qual os timestamps serão distribuídos (padrão: 1)
    --malformed-rate   Probabilidade (0-1) de gerar um log malformado (padrão: 0.01)
    --output           Caminho do arquivo de saída (padrão: logs.jsonl)
    --seed             Semente para reprodução determinística dos resultados

Cada registro válido contém:
    timestamp (ISO8601), service, level, message, trace_id, user_id, request_id

Os logs malformados podem consistir em strings truncadas, JSON incompleto ou texto livre.
"""

import argparse
import datetime as _dt
import json
import os
import random
import string
from typing import List, Dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerador de logs estruturados e malformados")
    parser.add_argument("--nb-logs", type=int, default=1000, help="Quantidade de linhas de log a gerar")
    parser.add_argument(
        "--duration-hours",
        type=float,
        default=1.0,
        help="Espalhar timestamps ao longo de X horas (padrão: 1)",
    )
    parser.add_argument(
        "--malformed-rate",
        type=float,
        default=0.01,
        help="Probabilidade de cada log ser malformado (entre 0 e 1)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="logs.jsonl",
        help="Caminho do arquivo de saída (JSON lines)",
    )
    parser.add_argument("--seed", type=int, default=None, help="Semente para o gerador aleatório")
    return parser.parse_args()


SERVICES = [
    "auth-service",
    "billing-service",
    "ingest-service",
    "recommender-service",
    "reporting-service",
    "storage-service",
    "monitoring-service",
    "notification-service",
    "user-service",
    "analytics-service",
]

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

MESSAGES = {
    "INFO": [
        "Processed request successfully",
        "Heartbeat ok",
        "User logged in",
        "Cache hit for key",
        "Scheduled job executed",
        "Loaded configuration",
    ],
    "DEBUG": [
        "Entering function",
        "Query execution plan generated",
        "Parsed payload",
        "Serialized response",
        "Response headers set",
    ],
    "WARNING": [
        "Slow response detected",
        "Retrying failed call",
        "Deprecated endpoint used",
        "High memory usage",
        "Missing optional field",
    ],
    "ERROR": [
        "Unhandled exception occurred",
        "Database connection failed",
        "Model inference timeout",
        "Failed to parse JSON",
        "Permission denied",
    ],
    "CRITICAL": [
        "Outage detected in region",
        "Data corruption detected",
        "Security breach attempted",
        "Disk failure imminent",
    ],
}


def random_hex(n: int) -> str:
    return "".join(random.choice("0123456789abcdef") for _ in range(n))


def generate_log_line(base_time: _dt.datetime, max_delta: float) -> Dict[str, object]:
    """Gera um log estruturado.

    Args:
        base_time: momento inicial de referência.
        max_delta: tempo máximo (em segundos) após base_time para deslocar o timestamp.
    Returns:
        Dicionário representando um log.
    """
    # seleciona timestamp aleatório dentro da janela
    delta_seconds = random.uniform(0, max_delta)
    ts = base_time + _dt.timedelta(seconds=delta_seconds)
    ts_iso = ts.replace(microsecond=0).isoformat() + "Z"
    # escolhe serviço e nível
    service = random.choice(SERVICES)
    level = random.choice(LEVELS)
    message = random.choice(MESSAGES[level])
    # compõe campos
    trace_id = random_hex(16)
    user_id = random.randint(1, 1000)
    request_id = random_hex(12)
    return {
        "timestamp": ts_iso,
        "service": service,
        "level": level,
        "message": message,
        "trace_id": trace_id,
        "user_id": user_id,
        "request_id": request_id,
    }


def make_malformed_line(valid_line: Dict[str, object]) -> str:
    """Retorna uma linha malformada a partir de um log válido.

    Existem várias estratégias possíveis: truncar JSON, remover chaves,
    retornar string aleatória etc. A escolha é aleatória.
    """
    strategies = ["truncated", "no_json", "missing_field"]
    strat = random.choice(strategies)
    if strat == "truncated":
        # serializa para JSON e remove os últimos caracteres
        text = json.dumps(valid_line)
        cut = random.randint(1, len(text) - 2)
        return text[:cut]
    elif strat == "no_json":
        # devolve texto livre
        return f"{valid_line['level']}::{valid_line['service']}::unexpected error code"
    else:  # missing_field
        line_copy = dict(valid_line)
        key_to_remove = random.choice(list(line_copy.keys()))
        del line_copy[key_to_remove]
        return json.dumps(line_copy)


def main() -> None:
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    # calculo da janela de tempo
    base_time = _dt.datetime.utcnow()
    max_delta = args.duration_hours * 3600.0
    out_path = args.output
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for _ in range(args.nb_logs):
            log_obj = generate_log_line(base_time, max_delta)
            # decide se será malformado
            if random.random() < args.malformed_rate:
                malformed = make_malformed_line(log_obj)
                f.write(malformed + "\n")
            else:
                f.write(json.dumps(log_obj) + "\n")
    print(f"Gerados {args.nb_logs} logs em {out_path}")


if __name__ == "__main__":
    main()
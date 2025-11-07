"""
Torna o diretório raíz um pacote Python.

Devido a restrições de nomenclatura do Python, não é possível importar
diretamente um pacote cujo nome contém hífen ("-").  Para facilitar o
consumo das submódulos deste repositório em testes e scripts, este
``__init__`` registra o módulo atual sob um nome alternativo sem hífen
(``helius_sim_lab``) no dicionário ``sys.modules``.  Assim, módulos
pode ser acessados via ``import helius_sim_lab.ml.train_gnn`` de forma
transparente.
"""

import sys as _sys

# Registra este pacote sob o nome alternativo ``helius_sim_lab`` se não existir
if 'helius_sim_lab' not in _sys.modules:
    _sys.modules['helius_sim_lab'] = _sys.modules[__name__]

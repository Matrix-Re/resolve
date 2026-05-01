# ReSolve - Distributed DNS Simulator

## Description
Projet pédagogique de simulation d’un système DNS distribué en Python.

## Objectifs
- implémenter un client DNS CLI
- implémenter un résolveur récursif
- implémenter des serveurs root, TLD et autoritaires
- gérer un cache avec TTL
- tester le fonctionnement avec pytest

## Installation

### Créer l’environnement virtuel
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Installer les dépendances
```bash
pip install -r requirements.txt
```

## Lisibilité du code
Utiliser la commande ruff pour formatter le code et le rendre plus lisible
```bash
ruff check .
ruff format .
```

## Lancer le server minimaliste
```bash
python -m servers.server
```

## Lancer une requete DNS
```bash
python -m client.cli {domain} --type {type} --host 127.0.0.1 --port 5300
```

ex :
```bash
python -m client.cli google.com --type A --host 127.0.0.1 --port 5300
```

## Lancement les tests
```bash
pytest
```
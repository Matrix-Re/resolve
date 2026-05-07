# ReSolve - Distributed DNS Simulator

## Description
Projet pédagogique de simulation d’un système DNS distribué en Python.

## Objectifs
- implémenter un client DNS CLI
- implémenter un résolveur récursif
- implémenter des serveurs root, TLD et autoritaires
- gérer un cache avec TTL
- tester le fonctionnement avec pytest
- Mettre en place une pipeline CI avec tests
- Documenter les choix techniques et l’architecture du projet.

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

## Lancer la chaîne DNS complète

Ouvrir plusieurs terminaux.

### 1. Lancer le serveur autoritaire
```bash
python -m servers.authoritative_server
```
### 2. Lancer le serveur TLD
```bash
python -m servers.tld_server
```
### 3. Lancer le serveur Root
```bash
python -m servers.root_server
```
### 4. Lancer le résolveur récursif
```bash
python -m resolver.recursive_resolver
```
### 5. Envoyer une requête DNS avec le client CLI
```bash
python -m client.cli maps.google.com --type A --host 127.0.0.1 --port 5300
```

## Côté dev

### Lisibilité du code
Utiliser Ruff pour vérifier et formater le code.
```bash
ruff check .
ruff format .
```

### Lancer les tests
```bash
pytest
```

### Couverture de tests

Lancer les tests avec couverture :
```bash
pytest --cov=. --cov-report=term-missing
```
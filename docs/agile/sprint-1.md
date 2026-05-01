# Sprint 1

## Période
Du 27 avril au 1 mai 2026

## Objectif
Mettre en place les bases du système DNS :
- architecture
- protocole
- client CLI
- serveur minimal

---

## Tâches (11 points)
- [x] Définir l’architecture globale du système DNS (1 pt)
- [x] Produire les diagrammes du système (1 pt)
- [x] Initialiser le dépôt et l’arborescence du projet (1 pt)
- [x] Rédiger le README et la documentation (1 pt)
- [x] Définir et implémenter le format des messages DNS (1 pt)
- [x] Développer un serveur minimal (2 pt)
- [x] Développer un client CLI minimal (2 pt)
- [x] Mettre en place les premiers tests unitaires (2 pt)

---

## Résultat
Le sprint a permis d’obtenir une première version fonctionnelle du système :

- communication opérationnelle entre client et serveur ;
- protocole JSON défini et implémenté (`DNSQuery` / `DNSResponse`) ;
- architecture claire et documentée ;
- premiers tests automatisés validant les échanges.

Le sprint a été terminé en avance, ce qui a permis d’anticiper la préparation du sprint suivant (définition des tickets et du backlog).

---

## Difficultés
- gestion des imports Python

---

## Améliorations
- renforcer la couverture de tests
- préparer la transition vers une implémentation réelle des serveurs DNS (autoritaire, TLD, root)


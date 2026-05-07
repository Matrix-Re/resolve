# Sprint 2

## Période
Du 2 mai au 8 mai 2026

## Objectif

Mettre en place une chaîne complète de résolution DNS simplifiée, en introduisant les serveurs autoritaires, TLD et root, ainsi qu’un résolveur récursif sans cache.

---

## Tâches

- [x] Mise en place d’une pipeline CI simple (tests automatiques) - 1 pt

- [x] Implémentation du serveur autoritaire basé sur un fichier JSON - 3 pts  
    - lecture d’un fichier de zone (ex : google.com.json)  
    - résolution de sous-domaines (maps.google.com, etc.)

- [x] Implémentation du serveur TLD - 2 pts  
    - redirection vers le serveur autoritaire approprié  

- [x] Implémentation du serveur Root - 2 pts  
    - redirection vers le bon TLD (.com)

- [x] Implémentation d’un résolveur récursif (sans cache) - 3 pts  
    - orchestration des appels Root → TLD → Autoritaire  
    - retour de la réponse finale au client

- [x] Mise à jour des tests unitaires et E2E - 2 pts  
    - test de la chaîne complète de résolution

---

## Résultat attendu

À la fin du sprint :
- une requête client traverse toute la chaîne DNS simulée :
  Client → Resolver → Root → TLD → Autoritaire → réponse
- les serveurs sont découplés mais interconnectés
- les tests valident le fonctionnement global du système

---

## Résultat

Le Sprint 2 a permis de mettre en place une chaîne complète de résolution DNS simplifiée.

Une requête envoyée par le client CLI peut désormais traverser l’ensemble des composants du système :

Client → Résolveur récursif → Root → TLD → Serveur autoritaire → Réponse finale

Le résolveur récursif orchestre les différentes étapes de résolution sans utiliser de cache. Il interroge d’abord le serveur Root afin d’identifier le TLD correspondant, puis le serveur TLD afin de récupérer le serveur autoritaire responsable du domaine. Enfin, il interroge le serveur autoritaire pour obtenir l’enregistrement DNS demandé.

Des tests unitaires ont été ajoutés pour valider le comportement de chaque composant : messages DNS, fonctions utilitaires, serveurs Root/TLD/autoritaire, résolveur récursif et client CLI.

Des tests E2E permettent également de valider le fonctionnement complet de la chaîne DNS avec plusieurs serveurs UDP lancés en parallèle.

Plusieurs refactorisations ont été réalisées afin d’améliorer la maintenabilité du projet. La classe `BaseDNSServer`, située dans `core/server.py`, centralise les comportements communs aux serveurs DNS : configuration réseau, réception des requêtes, traitement des erreurs et construction des réponses.

Une logique commune de redirection a également été isolée pour les serveurs Root et TLD, car ces deux composants ont un rôle similaire : ils ne retournent pas l’adresse IP finale, mais orientent le résolveur vers le serveur suivant.

Enfin, les constantes et les enums ont été centralisées afin d’éviter les valeurs dupliquées dans le code. Cela permet de modifier plus facilement des éléments partagés comme les ports, les chemins de configuration, les types de messages ou les codes d’erreur.

---

## Difficultés

- Gestion des erreurs intermédiaires dans le résolveur.
- Mise en place de tests E2E avec plusieurs serveurs UDP lancés en parallèle.
- Factorisation du code sans rendre l’architecture trop abstraite.
- Stabilisation de la couverture de tests.

---

## Améliorations

- Ajouter un cache dans le résolveur récursif.
- Gérer le TTL des enregistrements dans le cache.
- Ajouter de la redondance sur certains composants.
- Améliorer les logs pour mieux suivre le chemin d’une requête.
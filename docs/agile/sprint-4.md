# Sprint 4

## Période

Du 16 mai au 22 mai 2026

## Objectif

Finaliser les fonctionnalités reportées du Sprint 3 et rendre la solution utilisable dans un contexte plus proche d’un usage réel.

Ce sprint vise à :

- ajouter une redondance des serveurs Root avec mécanisme de fallback ;
- finaliser les tests liés au cache TTL et à la redondance ;
- compléter la documentation technique ;
- proposer une interface graphique permettant de gérer les fichiers de zones DNS ;
- valider l’utilisation de la solution depuis un ordinateur réel via un client DNS standard.

---

## Tâches

- [x] [ADMIN] Ajouter un client lourd d’édition des zones DNS - 3 pts

  Objectif : proposer une interface graphique simple permettant de consulter et modifier les fichiers de zones DNS sans éditer manuellement les fichiers JSON.

  Critères d’acceptation :
  - le client lourd permet de lister les zones disponibles ;
  - le client lourd permet d’afficher les enregistrements d’une zone ;
  - il est possible d’ajouter un enregistrement `A` ou `AAAA` ;
  - il est possible de modifier la valeur ou le TTL d’un enregistrement ;
  - il est possible de supprimer un enregistrement ;
  - les modifications sont sauvegardées dans le fichier JSON de la zone ;
  - la structure JSON reste compatible avec le serveur autoritaire.

---

- [x] [REAL-TEST] Tester la solution comme DNS local sur un vrai ordinateur - 3 pts

  Objectif : vérifier que la solution peut être utilisée depuis un ordinateur réel en configurant la machine pour interroger le résolveur DNS du projet.

  Critères d’acceptation :
  - le résolveur écoute sur une adresse accessible depuis la machine de test ;
  - l’ordinateur est configuré pour utiliser le résolveur du projet comme serveur DNS ;
  - une résolution de domaine gérée par le projet fonctionne depuis l’ordinateur ;
  - le test permet de valider que la solution peut être utilisée autrement que via le client CLI ;
  - la procédure de configuration est documentée ;
  - les limites sont précisées, notamment le fait que seuls les domaines présents dans les fichiers de zones du projet sont résolus.

---

- [x] [ROOT] Ajouter une redondance Root avec fallback - 3 pts

  Objectif : permettre au résolveur d’utiliser plusieurs serveurs Root afin d’assurer la continuité de service si le premier serveur Root ne répond pas.

  Critères d’acceptation :
  - le résolveur peut recevoir une liste de serveurs Root ;
  - si le premier Root ne répond pas, le résolveur interroge le Root suivant ;
  - si tous les Root échouent, une erreur claire est retournée au client ;
  - un test valide le fallback vers un Root secondaire ;
  - un test valide le cas où aucun Root n’est disponible.

---

- [x] [TEST] Compléter les tests unitaires/E2E liés au cache et à la redondance - 2 pts

  Objectif : garantir que les nouvelles fonctionnalités du Sprint 3 sont vérifiées automatiquement.

  Critères d’acceptation :
  - les tests unitaires couvrent le cache TTL ;
  - les tests unitaires couvrent la redondance Root ;
  - au moins un test E2E valide une résolution complète avec fallback Root ;
  - la couverture de code reste supérieure au seuil défini dans la pipeline ;
  - la pipeline CI reste fonctionnelle.

---

- [x] [DOC] Documenter cache, redondance et lancement Docker - 1 pt

  Objectif : mettre à jour la documentation technique du projet afin d’expliquer les nouvelles fonctionnalités du Sprint 3.

  Critères d’acceptation :
  - une page explique le fonctionnement du cache TTL ;
  - une page explique la redondance Root ;
  - une page explique le lancement avec Docker ;
  - les commandes principales sont documentées ;
  - les limites actuelles sont précisées.

---

## Résultat attendu

À la fin du sprint, le projet doit permettre :

- de poursuivre une résolution DNS même si le serveur Root principal est indisponible, grâce à un Root secondaire ;
- de valider le fonctionnement du cache TTL et du fallback Root avec des tests automatisés ;
- de gérer les zones DNS depuis une interface graphique simple ;
- d’ajouter, modifier et supprimer des enregistrements `A` et `AAAA` tout en contrôlant la validité des données ;
- d’utiliser la solution depuis un client DNS standard, en passant par une passerelle compatible avec le protocole DNS réel ;
- de disposer d’une documentation à jour sur le cache, Docker, la redondance et l’utilisation de la solution.

---

## Résultat

Le Sprint 4 a permis de finaliser les éléments qui n’avaient pas pu être terminés lors du sprint précédent et d’ajouter des fonctionnalités complémentaires au système DNS.

La redondance des serveurs Root a été mise en place au niveau du résolveur récursif. Celui-ci peut désormais recevoir plusieurs serveurs Root et interroger un serveur secondaire lorsque le serveur principal ne répond pas. Cette évolution permet de maintenir la résolution d’un domaine malgré l’indisponibilité d’un premier serveur Root.

Les tests liés aux fonctionnalités récentes ont également été complétés. Ils permettent de vérifier le comportement du cache TTL, la récupération d’une réponse encore valide depuis le cache, ainsi que le fallback vers un serveur Root secondaire. La pipeline CI continue ainsi de vérifier automatiquement la stabilité du projet.

Un client lourd d’administration des zones DNS a été développé. Cette interface graphique permet de consulter les fichiers de zones JSON, de créer ou supprimer une zone, ainsi que d’ajouter, modifier ou supprimer des enregistrements `A` et `AAAA`. Des contrôles ont été ajoutés afin de vérifier le format des domaines, l’absence de doublons, la validité du TTL et la cohérence des adresses IPv4 ou IPv6 avec le type d’enregistrement choisi.

Enfin, une passerelle DNS a été ajoutée afin de faire le lien entre le protocole DNS standard utilisé par un ordinateur et le protocole JSON interne du projet. Cette passerelle permet d’interroger la solution depuis un client DNS standard et de valider son utilisation dans un contexte plus réel que le seul client CLI développé au début du projet.

À l’issue de ce sprint, le projet dispose donc d’une chaîne de résolution DNS complète, d’un cache TTL, d’une redondance Root, d’un lancement conteneurisé, d’un outil graphique de gestion des zones et d’un accès compatible avec des requêtes DNS standards.

---

## Difficultés

- Mise en place de la redondance Root sans modifier inutilement l’architecture existante du résolveur.
- Gestion des différences de configuration entre l’exécution locale et l’exécution avec Docker, notamment l’utilisation des noms de services Docker à la place de `127.0.0.1`.
- Adaptation de la solution pour accepter des requêtes DNS standards, le protocole interne du projet reposant initialement sur des échanges JSON.
- Vérification du comportement du cache et du fallback Root dans les tests automatisés.

---

## Améliorations

- Ajouter des logs structurés afin de suivre plus facilement les étapes d’une résolution, les accès au cache et les bascules vers un Root secondaire.
- Finaliser les diagrammes d’architecture et préparer la démonstration finale du projet.
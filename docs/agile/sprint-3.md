# Sprint 3

## Période

Du 9 mai au 15 mai 2026

## Objectif

Améliorer la robustesse, les performances et le déploiement local du système DNS.

À la fin du Sprint 2, le projet dispose déjà d’une chaîne complète de résolution DNS fonctionnelle :

Client CLI → Résolveur récursif → Root → TLD → Serveur autoritaire → Réponse finale

L’objectif du Sprint 3 est maintenant de renforcer cette base avec :

- un cache TTL configurable dans le résolveur ;
- une redondance des serveurs Root avec mécanisme de fallback ;
- une dockerisation de l’infrastructure DNS ;
- des tests unitaires et E2E associés ;
- une documentation claire du fonctionnement ajouté.

Ces éléments répondent directement aux attentes du projet, notamment la présence d’un cache configurable, la redondance des serveurs racine et la documentation de l’installation/déploiement. 

---

## Tâches

- [x] [CACHE] Implémenter un cache TTL configurable dans le résolveur - 3 pts

  Objectif : permettre au résolveur récursif de stocker temporairement les réponses DNS valides afin d’éviter de refaire toute la chaîne Root → TLD → Autoritaire pour une requête déjà résolue.

  Critères d’acceptation :
  - une réponse DNS valide peut être stockée en cache ;
  - une requête identique retourne la réponse depuis le cache tant que le TTL est valide ;
  - une entrée expirée n’est plus utilisée ;
  - le cache prend en compte le couple `domain + record_type` ;
  - des tests couvrent les cas cache miss, cache hit et expiration.

---

- [ ] [ROOT] Ajouter une redondance Root avec fallback - 3 pts

  Objectif : permettre au résolveur d’utiliser plusieurs serveurs Root afin d’assurer la continuité de service si le premier serveur Root ne répond pas.

  Critères d’acceptation :
  - le résolveur peut recevoir une liste de serveurs Root ;
  - si le premier Root ne répond pas, le résolveur interroge le Root suivant ;
  - si tous les Root échouent, une erreur claire est retournée au client ;
  - un test valide le fallback vers un Root secondaire ;
  - un test valide le cas où aucun Root n’est disponible.

---

- [x] [DOCKER] Dockeriser l’infrastructure DNS avec docker-compose - 2 pts

  Objectif : simplifier le lancement de l’infrastructure DNS complète avec Docker.

  Critères d’acceptation :
  - un `Dockerfile` permet d’exécuter l’application Python ;
  - un `docker-compose.yml` lance les composants principaux ;
  - les services Root, TLD, autoritaire et résolveur peuvent être lancés ensemble ;
  - les fichiers de configuration JSON sont accessibles dans les conteneurs ;
  - la documentation explique comment lancer l’infrastructure avec Docker.

---

- [ ] [TEST] Compléter les tests unitaires/E2E liés au cache et à la redondance - 2 pts

  Objectif : garantir que les nouvelles fonctionnalités du Sprint 3 sont vérifiées automatiquement.

  Critères d’acceptation :
  - les tests unitaires couvrent le cache TTL ;
  - les tests unitaires couvrent la redondance Root ;
  - au moins un test E2E valide une résolution complète avec fallback Root ;
  - la couverture de code reste supérieure au seuil défini dans la pipeline ;
  - la pipeline CI reste fonctionnelle.

---

- [ ] [DOC] Documenter cache, redondance et lancement Docker - 1 pt

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

- de résoudre un domaine via la chaîne DNS complète ;
- de réutiliser une réponse en cache tant que son TTL est valide ;
- de continuer la résolution si un serveur Root est indisponible ;
- de lancer plus facilement l’infrastructure grâce à Docker ;
- de valider les nouvelles fonctionnalités avec des tests unitaires et E2E.

---

## Résultat

Le Sprint 3 n’a pas pu être entièrement terminé en raison d’un manque de temps personnel consacré au projet.

Cependant, plusieurs éléments importants ont été réalisés :

- mise en place d’un cache TTL dans le résolveur récursif avec affichage du contenu du cache en console
- dockerisation du projet avec un `Dockerfile` et un `docker-compose.yml` ;

Le cache permet désormais au résolveur de répondre directement à une requête déjà connue, tant que le TTL associé n’est pas expiré. Cela évite de refaire toute la chaîne de résolution Root → TLD → Autoritaire pour une même demande.

La dockerisation permet de simplifier le lancement de l’infrastructure DNS et prépare une utilisation plus propre du projet pour les démonstrations et la documentation de déploiement.

Certaines tâches prévues n’ont pas pu être finalisées pendant ce sprint, notamment :

- la redondance Root avec fallback ;
- les tests complets liés au cache et à la redondance ;
- la documentation complète des nouvelles fonctionnalités.

Ces éléments seront reportés au Sprint 4.

---

## Difficultés

- Manque de temps disponible pour finaliser l’ensemble des tickets prévus.
- Gestion de l’affichage du cache en console avec mise à jour continue du TTL.

---

## Améliorations

- Finaliser la redondance Root avec mécanisme de fallback.
- Ajouter les tests liés au fallback Root.
- Documenter le fonctionnement du cache.
- Documenter le lancement avec Docker.
- Mettre à jour les diagrammes d’architecture si nécessaire.
- Préparer un Sprint 4.
# Changelog - WLED Icons Add-on

## [0.2.4] - 2025-11-16

### Ajouté
- Sauvegarde automatique des valeurs du formulaire dans localStorage
- Les champs (hôte, ID icône, couleur, rotation, FPS, boucles) et cases à cocher sont restaurés au rechargement de la page
- Prévisualisation automatique de l'icône si un ID est sauvegardé

## [0.2.3] - 2025-11-16

### Corrigé
- Correction de la boucle infinie : la valeur -1 fonctionne maintenant correctement pour une animation en boucle continue
- Remplacement de `range(max(1, loop))` par une logique `while True` avec condition de sortie

## [0.2.2] - 2025-11-16

### Modifié
- Ajout de l'indication "(-1 = infini)" dans les champs "Boucles" de l'interface
- Les champs acceptent maintenant -1 comme valeur minimale pour les boucles infinies

## [0.2.1] - 2025-11-16

### Ajouté
- Indication dans l'interface : la valeur -1 dans le champ "Boucles" permet de faire tourner le GIF en boucle infinie

## [0.2.0] - 2025-11-16

### Ajouté
- Support des icônes LaMetric animées (GIF) avec plus de 1800 icônes disponibles
- Contrôle d'animation : FPS forcé, nombre de boucles (-1 pour boucle infinie)
- Transformations d'orientation : rotation (0/90/180/270°) et miroirs (H/V)
- Interface web moderne avec support du mode sombre automatique
- Prévisualisation des icônes LaMetric en temps réel
- Recolorisation des icônes monochromes via couleur hex
- Upload de GIFs 8x8 personnalisés
- Notifications toast pour les retours utilisateur

### Modifié
- Remplacement des icônes MDI par les icônes LaMetric natives 8x8
- Refonte complète de l'interface utilisateur (design moderne responsive)
- Architecture HTML externe pour faciliter la maintenance
- Amélioration de la gestion des erreurs et des logs

### Supprimé
- Section d'upload PNG 8x8 statique
- Références aux icônes Material Design Icons (MDI)

## [0.1.1] - 2025-11-16

### Corrigé
- Problème de cache navigateur lors des mises à jour
- Affichage des nouveaux contrôles UI

## [0.1.0] - 2025-11-15

### Ajouté
- Version initiale de l'add-on FastAPI
- Interface Ingress pour Home Assistant
- Support des icônes MDI avec rendu SVG
- Upload PNG et GIF
- API REST pour intégration

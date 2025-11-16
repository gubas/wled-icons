# Changelog - WLED Icons Add-on

## [0.2.0] - 2025-11-16

### Ajouté
- Support des icônes LaMetric animées (GIF) avec plus de 1800 icônes disponibles
- Contrôle d'animation : FPS forcé, nombre de boucles (infini avec -1)
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

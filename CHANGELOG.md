# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-11-16

### Intégration Home Assistant

#### Ajouté
- Nouveau service `show_lametric` avec support complet des icônes LaMetric animées
- Paramètres avancés : `icon_id`, `rotate`, `flip_h`, `flip_v`, `animate`, `fps`, `loop`
- Support des boucles infinies avec `loop: -1`
- Valeur par défaut pour `addon_url` dans le config flow

#### Modifié
- Remplacement du service `show_mdi` par `show_lametric`
- Simplification : appel direct à l'add-on (pas de fallback local)
- Timeout augmenté à 30s pour les animations longues
- Host et addon_url peuvent être préconfigurés dans l'intégration

#### Supprimé
- Service `show_static` (PNG upload)
- Fallback local avec cairosvg (tout passe par l'add-on)
- Dépendances Pillow et requests du manifest (inutilisées)

## [0.2.0] - 2025-01-XX

### Added
- **Support des icônes LaMetric animées** : Intégration complète de l'API LaMetric avec plus de 1800 icônes 8x8 pixel-art
- **Animations GIF** : Lecture frame-by-frame avec contrôle FPS (forcé ou timing GIF original) et nombre de boucles (-1 pour infini)
- **Transformations d'orientation** : Rotation (0/90/180/270°), miroirs horizontal/vertical pour ajuster l'orientation de la matrice
- **Recolorisation** : Changement de couleur pour icônes LaMetric monochromes via paramètre hex color
- **Interface web moderne** : UI responsive avec dark mode automatique (CSS custom properties + media query)
- **Prévisualisation d'icônes** : Affichage en temps réel de l'icône LaMetric avant envoi WLED
- **Notifications toast** : Messages de succès/erreur avec animations CSS
- **Service `show_lametric`** : Remplacement de `show_mdi` avec paramètres `icon_id`, `animate`, `fps`, `loop`
- **Upload GIF personnalisé** : Support d'envoi de GIFs 8x8 custom via interface web
- Architecture externe HTML : Séparation du code HTML/CSS/JS dans `index.html` pour faciliter la maintenance

### Changed
- **Terminologie** : Renommage "MDI" → "LaMetric" dans toute l'interface et la documentation
- **Format d'icônes** : Abandon SVG rasterization au profit des icônes 8x8 natives LaMetric (JPG/GIF)
- **Structure UI** : Nouvelle mise en page par cartes avec sections Configuration/Orientation/Animation/GIF Upload
- **Code serveur** : Refactorisation de `main.py` pour servir fichier HTML externe via `FileResponse`
- **Version bump** : 0.1.1 → 0.2.0 pour forcer rebuild automatique lors des mises à jour
- **Documentation** : README entièrement réécrit avec exemples d'automatisations, dépannage, ressources LaMetric

### Removed
- **Upload PNG 8x8** : Suppression de la section upload PNG statique (simplification UI)
- **Références MDI** : Retrait complet des références à Material Design Icons

### Fixed
- **Cache navigateur** : Corrections du système de versioning pour garantir le refresh UI
- **Rendu HTML** : Résolution des problèmes d'affichage d'HTML inline en Python
- **Gestion d'erreurs** : Amélioration du retour d'erreur pour icônes non trouvées

## [0.1.1] - 2025-01-XX

### Fixed
- **Cache UI** : Incrémentation de version pour forcer la reconstruction de l'add-on
- **Affichage HTML** : Correction du rendu des nouveaux contrôles UI

## [0.1.0] - 2025-11-15

### Added
- Première version avec script Python standalone
- Support icônes LaMetric basique
- Blueprint Home Assistant
- Shell command pour intégration HA

[0.2.0]: https://github.com/gubas/wled-icons/releases/tag/v0.2.0
[0.1.1]: https://github.com/gubas/wled-icons/releases/tag/v0.1.1
[0.1.0]: https://github.com/gubas/wled-icons/releases/tag/v0.1.0

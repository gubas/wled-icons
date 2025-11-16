# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-16

### Added
- Home Assistant Add-on avec FastAPI pour le rendu des icônes
- UI Ingress pour tester les icônes directement depuis Supervisor
- Config flow pour configurer l'intégration via l'UI Home Assistant
- Support complet des icônes Material Design Icons (MDI)
- Rendu de fichiers PNG 8x8 statiques
- Support d'animations GIF avec contrôle FPS et loop
- Services Home Assistant: `wled_icons.show_mdi`, `wled_icons.show_static`, `wled_icons.show_gif`
- Recolorisation des icônes MDI/SVG avec couleur hex personnalisable
- Translations FR/EN pour config flow et services
- Workflow GitHub Actions pour validation CI
- Documentation complète de publication add-on

### Changed
- Migration vers architecture add-on + intégration custom component
- Abandon de l'approche blueprint + shell_command pour simplifier la maintenance

### Removed
- Script Python standalone `lametric_to_wled.py`
- Blueprint d'automatisation Home Assistant
- Package YAML avec shell_command
- Scripts Home Assistant legacy

## [0.1.0] - 2025-11-15

### Added
- Première version avec script Python standalone
- Support icônes LaMetric (abandonné par la suite)
- Blueprint Home Assistant basique
- Shell command pour intégration HA

[0.2.0]: https://github.com/gubas/wled-icons/releases/tag/v0.2.0
[0.1.0]: https://github.com/gubas/wled-icons/releases/tag/v0.1.0

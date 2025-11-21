# Changelog

## [0.7.3] - 2025-11-21

### Corrections
- 🐛 **Build Docker** : Correction erreur build (lien symbolique → copie réelle)
- 📦 Le dossier `integration/` contient maintenant une copie physique

## [0.7.2] - 2025-11-21

### Intégration Home Assistant
- 🔄 **Auto-installation** : L'intégration se copie automatiquement dans `/config/custom_components/` au démarrage de l'add-on
- 🗑️ **Service `show_gif` supprimé** : Endpoint désactivé côté add-on, service retiré de l'intégration
- 💡 **Paramètre `brightness` ajouté** : Contrôle de la luminosité (0-255) dans le service `show_lametric`
- ⏹️ **Nouveau service `stop`** : Arrêt des animations en cours depuis Home Assistant
- 🔄 **Mise à jour simplifiée** : Plus besoin de copier manuellement l'intégration, elle se met à jour avec l'add-on

## [0.7.1] - 2025-11-21

### Corrections
- 🐚 **Script shell** : Utilisation de `#!/bin/sh` natif Alpine au lieu de `bash` pour réduire les dépendances
- 📦 **Image minimale** : Suppression de l'installation de bash (~2-3 MB économisés)

## [0.7.0] - 2025-11-21

### Optimisations Docker
- 🐋 **Image Alpine** : Migration de Debian Slim vers Alpine Linux pour réduire la taille de l'image de ~60%
- 🗑️ **Dépendances allégées** : Suppression de cairosvg et ses dépendances lourdes (cairo, pango, gdk-pixbuf)
- 🚫 **Endpoint SVG supprimé** : Retrait de `/show/svg` et `rasterize_svg()` (obsolètes)
- 📦 **Build optimisé** : Réduction du temps de build et de la taille finale (~50-80 MB au lieu de ~150-200 MB)
- 🧹 **.dockerignore amélioré** : Exclusion de plus de fichiers inutiles (venv, node_modules, IDE, db)

## [0.6.7] - 2025-11-21

### Interface Utilisateur
- 📐 **Layout optimisé** : Le bloc "Créer une Icône Personnalisée" occupe maintenant tout l'espace disponible
- ⬆️ **Alignement amélioré** : Les 3 blocs principaux sont alignés en haut
- 📦 **En-tête compact** : Réduction de l'espace occupé par le bloc titre
- ⚖️ **Boutons d'action équilibrés** : Les boutons "Envoyer" et "Arrêter" ont la même taille
- 💾 **Bouton Sauvegarder centré** : Positionné au centre sous la grille

## [0.6.6] - 2025-11-21

### Interface Utilisateur
- 🎬 **Options d'animation masquables** : Les contrôles d'animation sont repliables
- 🧹 **Cohérence UI** : Structure identique au bloc "Options d'orientation"
- 📦 **Interface compacte** : Options avancées masquées par défaut

## [0.6.5] - 2025-11-19

### Interface Utilisateur
- 🔧 **Icône Configuration** : Ajout d'une icône engrenage (mdi-cog) au titre du bloc Configuration
- 💡 **Icône principale unifiée** : Utilisation de l'icône officielle Home Assistant (mdi:led-strip-variant)
- 🧩 **Dépendance MDI** : Intégration de la webfont Material Design Icons via CDN

## [0.6.4] - 2025-11-19

### Interface Utilisateur
- 🎯 **Layout optimisé** : Boutons d'édition repositionnés à droite de la grille
- 📐 **Boutons ultra-compacts** : Réduction à 32x32px pour les boutons d'édition
- 🎬 **Contrôles animation réduits** : Taille des boutons de frames diminuée
- 💾 **Sauvegarder repositionné** : Bouton déplacé sous la grille

## [0.6.3] - 2025-11-19

### Interface Utilisateur
- ⏹️ **Bouton Arrêter** : Ajout d'un bouton pour arrêter l'animation en cours
- 🎨 **Éditeur compact** : Boutons d'édition réduits en icônes uniquement
- ↶↷ **Nouvelles icônes** : Remplacement des icônes ⏮️⏭️ par ↶↷ pour undo/redo
- 📤 **Icône envoi** : Ajout de l'émoji 📤 sur le bouton "Afficher sur WLED"

## [0.6.2] - 2025-11-19

### Corrections Critiques
- 🐛 **Plantages résolus** : Correction du système d'animation
- 🧵 **Threading** : Les animations tournent en arrière-plan dans des threads dédiés
- ⛔ **Arrêt propre** : Nouvelle animation arrête automatiquement la précédente
- 🔁 **Boucles infinies** : Gestion correcte des boucles infinies (-1)
- 💡 **Luminosité GIF** : Support de la luminosité pour les GIFs uploadés

## [0.6.1] - 2025-11-19

### Interface Utilisateur
- 💡 **Luminosité centralisée** : Déplacement du slider dans le bloc de configuration principal
- 🧹 **Éditeur épuré** : Suppression des boutons redondants
- 🔄 **Flux simplifié** : L'envoi vers WLED se fait uniquement via le bouton principal

## [0.6.0] - 2025-11-18

### Refactoring
- 🏗️ **Architecture Frontend** : Séparation complète du code (HTML, JS, CSS)
- 🧹 **Nettoyage** : Extraction de ~940 lignes de JavaScript vers `app.js`
- 🔢 **Constantes** : Remplacement des "nombres magiques" par des constantes globales
- 🚀 **Performance** : Chargement optimisé des ressources

## [0.5.8] - 2025-11-18

### Ajouté
- 💡 **Contrôle luminosité** : Slider 1-255 pour régler l'intensité avant envoi WLED
- ✏️ **Outil pipette** : Copier les couleurs en cliquant sur un pixel
- 🪠 **Symétrie automatique** : Miroir horizontal/vertical en temps réel
- ⏮️⏭️ **Undo/Redo** : Historique de 50 états + raccourcis Ctrl+Z / Ctrl+Y
- 🔌 **API REST étendue** : 7 nouveaux endpoints pour automatisation

## Versions antérieures

Voir le fichier CHANGELOG.md complet à la racine du projet pour l'historique complet.

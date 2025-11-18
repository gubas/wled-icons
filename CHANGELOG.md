# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.8] - 2025-11-18

### Add-on

#### Ajouté
- 💡 **Contrôle luminosité** : Slider 1-255 pour régler l'intensité avant envoi WLED
- ✏️ **Outil pipette** : Copier les couleurs en cliquant sur un pixel (🎨)
- 🪠 **Symétrie automatique** : Miroir horizontal/vertical en temps réel (↔️ ↕️)
- ⏮️⏭️ **Undo/Redo** : Historique de 50 états + raccourcis Ctrl+Z / Ctrl+Y
- 🔌 **API REST étendue** : 7 nouveaux endpoints pour automatisation :
  - Contrôle luminosité WLED
  - Récupération d'état WLED
  - On/Off WLED
  - Affichage séquentiel d'icônes (slideshow)
  - Recherche d'icônes par nom/ID

#### Amélioré
- 🎨 **Système d'outils** : Basculer entre dessin/pipette (curseur adapté)
- ⌨️ **Raccourcis clavier** : Support Ctrl+Z, Ctrl+Y, Ctrl+Shift+Z
- 🔹 **Feedback visuel** : Style actif sur l'outil sélectionné
- 💾 **Historique intelligent** : Sauvegarde avant chaque action, buffer circulaire
- 📈 **Précision luminosité** : Application correcte sur RGB avec arrondi

## [0.5.7] - 2025-11-18

### Add-on

#### Corrigé
- 🐛 **Affichage ID dialogue** : Correction de l'affichage de l'ID généré avec styles inline
- ❌ **Suppression bouton 📋** : Retrait du gros bouton de copie (clic direct sur le champ)
- 🎨 **Styles forcés** : Utilisation de styles inline pour contourner les problèmes CSS
- 🔍 **Logs debug** : Ajout de console.log pour tracer la génération de l'ID

## [0.5.6] - 2025-11-18

### Add-on

#### Amélioré
- 🎨 **Interface épurée** : Suppression de l'icône 📋 devant l'ID (6 chiffres uniquement)
- 🚫 **Masquage intelligent** : La ligne de nom disparaît si l'icône n'a pas de nom personnalisé
- 📏 **Boutons compacts** : Réduction de la taille des boutons d'action (📤 📋 🗑️)
- 💬 **Micro popup** : Messages flottants en haut à droite avec animation douce
- ✨ **Animation moderne** : Apparition en fondu avec translateY pour les notifications
- 🎯 **Badge animation** : Affichage sur la date si pas de nom personnalisé

## [0.5.5] - 2025-11-17

### Add-on

#### Amélioré
- 🎨 **Affichage bibliothèque** : IDs raccourcis (6 derniers chiffres) pour plus de lisibilité
- 🎭 **Noms intelligents** : 🎨 au lieu de "Sans nom" pour les icônes non nommées
- 💬 **Tooltip ID complet** : Survol affiche l'ID complet même si affichage court
- 🔤 **Style amélioré** : Police monospace, espacement lettres, effet zoom au survol
- ✅ **Copie complète** : Cliquer copie toujours l'ID complet (pas la version courte)

## [0.5.4] - 2025-11-17

### Add-on

#### Corrigé
- 🐛 **CORRECTION CRITIQUE** : Les icônes WI s'affichent maintenant correctement sur WLED !
- 📦 **Format de tableau** : Conversion de la matrice 8x8 en tableau plat de 64 pixels (format WLED)
- ✅ **Alignement avec LaMetric** : Les icônes WI utilisent maintenant le même format que les icônes LaMetric (64x3)
- 🎬 **Animations** : Correction du format pour les animations frame par frame également
- 🔄 **Transformations** : Gestion correcte des rotations/miroirs pour les deux formats

## [0.5.3] - 2025-11-17

### Add-on

#### Amélioré
- 🔍 **Logs send_frame** : Logs détaillés dans la fonction d'envoi vers WLED (adresse, dimensions, payload, réponse)
- 📊 **Diagnostic envoi** : Affichage de la première ligne de pixels et du statut de réponse WLED
- ⚠️ **Gestion d'erreurs** : Capture des exceptions de connexion avec messages explicites
- 🎯 **Source tracking** : Ajout de `"source": "custom"` dans la réponse des icônes WI

## [0.5.2] - 2025-11-17

### Add-on

#### Amélioré
- 🔍 **Debug avancé** : Logs supplémentaires pour identifier pourquoi les icônes WI ne sont pas détectées (type, repr, startswith)
- 🐛 **Investigation** : Ajout de vérifications pour comprendre le problème de routage LaMetric vs WI

## [0.5.1] - 2025-11-17

### Add-on

#### Amélioré
- 🔍 **Logs détaillés** : Ajout de logs côté serveur pour le traitement des icônes WI
- 📊 **Debug client** : Console logs pour suivre les requêtes d'envoi d'icônes
- 🛠️ **Diagnostic** : Affichage des icônes disponibles et détails des erreurs
- ⚠️ **Messages d'erreur** : Affichage du détail des erreurs HTTP dans l'interface

## [0.5.0] - 2025-11-17

### Add-on

#### Ajouté
- ✨ **Support des icônes personnalisées dans le formulaire** : Les icônes WI... peuvent maintenant être utilisées directement
- 🔍 **Preview intelligente** : Détection automatique du type d'icône (LaMetric ou WI...) avec aperçu adapté
- 📤 **Bouton "Utiliser dans le formulaire"** : Permet d'utiliser une icône de la bibliothèque en un clic
- 🎯 **Navigation automatique** : Scroll vers le formulaire après sélection d'une icône

#### Amélioré
- 🏷️ **Label du champ ID** : Indique maintenant qu'on peut utiliser les deux types d'icônes
- 📋 **Gestion des erreurs** : Message si l'icône personnalisée n'est pas trouvée
- 🎨 **UX de la bibliothèque** : Trois boutons par icône (📤 Utiliser, 📋 Copier, 🗑️ Supprimer)

## [0.4.9] - 2025-11-17

### Add-on

#### Corrigé
- 🐛 **Affichage de l'ID** : L'ID n'apparaissait pas dans la bibliothèque ("undefined") - l'API ajoute maintenant l'ID dans chaque objet icône
- ✨ **Style du champ ID généré** : Le champ d'ID dans le dialogue de sauvegarde utilise maintenant une police monospace, est centré et bien visible
- 🎨 **Amélioration visuelle** : Police Courier New, couleur primaire, padding généreux pour le champ d'ID

## [0.4.8] - 2025-11-17

### Add-on

#### Amélioré
- ✨ **Affichage de l'ID** : L'ID est maintenant très visible avec un fond gris et l'icône 📋
- 📋 **Copie d'ID facilitée** : Cliquer directement sur l'ID le copie dans le presse-papier
- 🎯 **UX améliorée** : Effet de survol et tooltip "Cliquer pour copier l'ID"
- 🔤 **Sélection de texte** : L'ID peut aussi être sélectionné manuellement (user-select: all)

## [0.4.7] - 2025-11-17

### Add-on

#### Corrigé
- 🐛 **Correction du bouton Sauvegarder** : Le bouton appelle maintenant la bonne fonction `openSaveDialog()` au lieu de `showSaveDialog()`

## [0.4.6] - 2025-11-17

### Add-on

#### Amélioré
- ✨ **Dialogue de sauvegarde** : L'ID généré est maintenant affiché avant la sauvegarde
- 📋 **Copie d'ID** : Possibilité de copier l'ID directement depuis le dialogue en cliquant sur le champ ou le bouton 📋
- 🔖 **Génération d'ID** : L'ID est pré-généré à l'ouverture du dialogue pour une meilleure visibilité

## [0.4.5] - 2025-11-17

### Add-on

#### Corrigé
- 🐛 **Correction critique** : Les appels API `/api/icons` utilisent maintenant `basePath` pour fonctionner avec l'ingress Home Assistant
- ✅ La sauvegarde, le chargement et la suppression d'icônes fonctionnent maintenant correctement
- 🔗 Toutes les URLs relatives sont maintenant préfixées avec le chemin d'ingress

## [0.4.4] - 2025-11-17

### Add-on

#### Amélioré
- 🔍 Ajout de logs détaillés côté client (console F12) pour le débogage des sauvegardes
- 📋 Ajout de logs serveur pour tracer les opérations de sauvegarde d'icônes
- 🚀 Logs au démarrage affichant les chemins des fichiers (data, HTML, CSS)
- 🛠️ Message d'erreur invitant à consulter la console pour plus de détails

## [0.4.3] - 2025-11-17

### Add-on

#### Corrigé
- 🐛 Les erreurs de sauvegarde/suppression s'affichent maintenant dans des popups (alert) au lieu de messages discrets
- 📊 Affichage du code HTTP et du message d'erreur détaillé pour faciliter le débogage

## [0.4.2] - 2025-11-17

### Add-on

#### Amélioré
- 📐 Mise en page responsive en grille CSS (1/2/3 colonnes selon la largeur d'écran)
- 🎨 Éditeur pixel art : grille de dessin positionnée à côté de la palette de couleurs sur desktop
- 📑 Ajout d'onglets pour séparer "✏️ Dessin" et "🎬 Animation"
- ⚙️ Options d'orientation cachées par défaut avec bouton toggle
- 📚 Bibliothèque "Mes Créations" dans une carte dédiée pleine largeur
- 🐛 Correction : la boîte de dialogue de sauvegarde se ferme maintenant même en cas d'erreur
- ✨ Les blocs se réorganisent automatiquement selon l'espace disponible

## [0.4.1] - 2025-11-17

### Add-on

#### Amélioré
- Extraction du CSS dans un fichier séparé (`styles.css`) pour améliorer la maintenabilité
- Réduction de la taille du fichier `index.html` de 1436 à 861 lignes
- Meilleure organisation du code (séparation HTML/CSS)
- Amélioration du cache navigateur (le CSS peut être mis en cache indépendamment)

## [0.4.0] - 2025-11-17

### Intégration Home Assistant

#### Ajouté
- Support des animations frame par frame dans l'éditeur pixel art
- Stockage persistant des icônes WI côté serveur (dans `/data/custom_icons.json`)
- Bibliothèque d'icônes partagée entre tous les appareils
- Les icônes WI peuvent maintenant contenir plusieurs frames animées
- Prévisualisation d'animation en temps réel dans l'éditeur
- Badge indiquant le nombre de frames dans la bibliothèque
- Support complet des paramètres `animate`, `fps`, `loop` pour les icônes WI animées

#### Modifié
- **API Breaking Change** : Renommage de tous les endpoints et variables MDI en icon/lametric
  - Endpoint `/show/mdi` → `/show/icon`
  - Modèle `MdiRequest` → `IconRequest`
  - Champs formulaire `mdi`, `mdi_fps`, `mdi_loop` → `icon_id`, `icon_fps`, `icon_loop`
  - Clés localStorage `wled_mdi*` → `wled_icon*`
- Format de stockage des icônes : support `frames` (array) en plus de `grid` (legacy)
- L'éditeur sauvegarde maintenant toutes les frames au lieu d'une seule grille

#### Amélioré
- Les icônes WI sont maintenant sauvegardées côté serveur au lieu du localStorage
- Backup automatique avec Home Assistant (dossier `/data`)
- Pas de perte d'icônes lors du vidage du cache navigateur
- Interface d'animation complète : ajout/duplication/suppression de frames
- Compteur de frames et navigation entre frames avec miniatures

### Add-on

#### Ajouté
- 🎬 **Animations frame par frame** : Créez des GIFs animés pixel par pixel
- ➕ Bouton pour ajouter une nouvelle frame
- 📋 Bouton pour dupliquer la frame courante
- 🗑️ Bouton pour supprimer une frame
- ▶️ Prévisualisation d'animation avec canvas 64x64px
- Réglage du FPS (1-30, recommandé: 8)
- Liste de miniatures des frames avec navigation cliquable
- Compteur "Frame X/Y" pour suivre la position
- API REST complète pour les icônes personnalisées :
  - `GET /api/icons` - Liste toutes les icônes
  - `GET /api/icons/{icon_id}` - Récupère une icône
  - `POST /api/icons/{icon_id}` - Sauvegarde/met à jour
  - `DELETE /api/icons/{icon_id}` - Supprime
  - `POST /api/icons/{icon_id}/display` - Affiche sur WLED

#### Modifié
- Endpoint `/show/mdi` renommé en `/show/icon`
- Les icônes WI animées sont maintenant lues frame par frame avec le FPS spécifié
- Modèle `CustomIcon` support `frames` (array) + `fps` en plus de `grid` (legacy)
- Stockage dans `/data/custom_icons.json` au lieu de localStorage navigateur

#### Amélioré
- Performance de l'affichage des animations personnalisées
- Compatibilité ascendante : les anciennes icônes avec `grid` sont toujours supportées
- Les transformations (rotation, miroirs) s'appliquent à chaque frame des animations

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

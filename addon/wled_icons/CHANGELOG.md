# Changelog - WLED Icons Add-on

## [0.5.2] - 2025-11-17

### Amélioré
- 🔍 **Logs de debug détaillés** : Affichage du type Python et repr() de l'icon_id reçu
- 🐛 **Test startswith** : Vérification explicite si icon_id.startswith('WI') retourne True/False
- 🛠️ **Investigation** : Identification du problème de détection des icônes personnalisées vs LaMetric

## [0.5.1] - 2025-11-17

### Amélioré
- 🔍 **Logs serveur détaillés** : Suivi complet du traitement des icônes personnalisées (icon_id reçu, icônes disponibles, erreurs)
- 📊 **Logs console client** : console.log pour toutes les requêtes et réponses d'envoi d'icônes
- 🛠️ **Diagnostic amélioré** : Affichage de la liste des IDs disponibles en cas d'erreur 404
- ⚠️ **Messages d'erreur explicites** : Détail des erreurs HTTP affiché dans l'interface utilisateur

## [0.5.0] - 2025-11-17

### Ajouté
- ✨ **Intégration complète des icônes personnalisées** : Les icônes WI... peuvent être utilisées dans le formulaire principal
- 🔍 **Preview intelligente** : La fonction `previewIcon()` détecte automatiquement si c'est une icône LaMetric ou personnalisée
- 📤 **Bouton "Utiliser dans le formulaire"** : Nouveau bouton dans la bibliothèque pour utiliser l'icône en un clic
- 🎯 **Auto-scroll** : Navigation automatique vers le formulaire après sélection

### Amélioré
- 🏷️ **Clarté du formulaire** : Le label indique "ID Icône (LaMetric ou WI...)"
- 📋 **Trois actions par icône** : 📤 Utiliser, 📋 Copier ID, 🗑️ Supprimer
- ⚠️ **Gestion des erreurs** : Message explicite si l'icône WI... n'existe pas

## [0.4.9] - 2025-11-17

### Corrigé
- 🐛 **Bug ID "undefined"** : L'API `/api/icons` ajoute maintenant le champ `id` dans chaque objet icône retourné
- ✨ **Champ ID généré** : Style amélioré avec police monospace (Courier New), texte centré et couleur primaire
- 🎨 **Visibilité** : Le champ d'ID dans le dialogue est maintenant clairement visible et lisible

## [0.4.8] - 2025-11-17

### Amélioré
- ✨ **Visibilité de l'ID** : L'ID des icônes est maintenant affiché avec un fond gris, padding et icône 📋
- 📋 **Copie facilitée** : Cliquer sur l'ID le copie directement dans le presse-papier
- 🎯 **Meilleure UX** : Effet hover sur l'ID et tooltip explicatif
- 🔤 **Sélection manuelle** : L'ID peut aussi être sélectionné et copié manuellement

## [0.4.7] - 2025-11-17

### Corrigé
- 🐛 **Bouton Sauvegarder** : Correction de l'appel de fonction (`openSaveDialog()` au lieu de `showSaveDialog()`)

## [0.4.6] - 2025-11-17

### Amélioré
- ✨ **Dialogue de sauvegarde** : L'ID généré est maintenant affiché avant la sauvegarde
- 📋 **Copie d'ID** : Possibilité de copier l'ID directement depuis le dialogue en cliquant sur le champ ou le bouton 📋
- 🔢 **Génération d'ID** : L'ID est pré-généré à l'ouverture du dialogue pour une meilleure visibilité

## [0.4.5] - 2025-11-17

### Corrigé
- 🐛 **Correction critique du bug de sauvegarde** : Tous les appels API utilisent maintenant `basePath`
- 🔗 Les URLs `/api/icons`, `/api/icons/{icon_id}` sont maintenant correctement préfixées
- ✅ Résolution du problème HTTP 404 sur les endpoints API avec l'ingress Home Assistant
- 💾 La sauvegarde d'icônes personnalisées fonctionne maintenant correctement
- 🗑️ La suppression d'icônes fonctionne également
- 📚 Le chargement de la bibliothèque d'icônes est opérationnel

## [0.4.4] - 2025-11-17

### Amélioré
- 🔍 **Logs de débogage détaillés** : Ajout de console.log pour tracer les requêtes de sauvegarde
- 📋 Logs serveur Python pour chaque opération de sauvegarde/suppression d'icône
- 🚀 Logs au démarrage du serveur affichant les chemins critiques (DATA_DIR, ICONS_FILE, etc.)
- 🛠️ Message d'erreur amélioré invitant à ouvrir la console (F12) pour diagnostic
- 📊 Affichage du statut HTTP et des données envoyées dans la console pour faciliter le débogage

## [0.4.3] - 2025-11-17

### Corrigé
- 🐛 **Messages d'erreur améliorés** : Les erreurs de sauvegarde/suppression s'affichent dans des popups alert() au lieu de messages discrets
- 📊 Affichage du code HTTP et du message d'erreur complet pour faciliter le diagnostic
- ✅ L'utilisateur est maintenant toujours informé visuellement en cas d'échec

## [0.4.2] - 2025-11-17

### Amélioré
- 📐 **Mise en page responsive en grille CSS** : 1 colonne (mobile) → 2 colonnes (1024px+) → 3 colonnes (1440px+)
- 🎨 **Éditeur optimisé** : Grille de dessin 8x8 positionnée à côté de la palette de couleurs sur desktop
- 📑 **Onglets éditeur** : Séparation claire entre "✏️ Dessin" et "🎬 Animation"
- ⚙️ **Options d'orientation** : Masquées par défaut, affichables via bouton "⚙️ Options d'orientation"
- 📚 **Bibliothèque dédiée** : "Mes Créations Sauvegardées" dans une carte pleine largeur
- ✨ Les cartes se réorganisent automatiquement selon l'espace disponible (pas de largeur max fixe)
- 🖥️ Meilleure utilisation de l'espace sur grand écran

### Corrigé
- 🐛 La boîte de dialogue de sauvegarde se ferme maintenant toujours (même en cas d'erreur serveur)
- 🐛 Suppression de la duplication de la bibliothèque dans les onglets

## [0.4.1] - 2025-11-17

### Amélioré
- 📁 Extraction du CSS dans un fichier séparé (`styles.css`)
- 🎯 Amélioration de la maintenabilité du code
- 📉 Réduction de la taille de `index.html` (1436 → 861 lignes, -40%)
- ⚡ Meilleure performance de cache navigateur
- 🔧 Séparation des préoccupations (HTML structure / CSS présentation)
- Ajout de l'endpoint `/styles.css` pour servir la feuille de style

## [0.4.0] - 2025-11-17

### Ajouté
- 🎬 **Animations frame par frame** : Créez des icônes animées en dessinant chaque image
- ➕ Ajouter des frames pour créer une animation complète
- 📋 Dupliquer la frame courante pour faciliter l'édition
- 🗑️ Supprimer une frame (minimum 1 frame)
- ▶️ Prévisualisation d'animation en temps réel (canvas 64x64px)
- Contrôle du FPS : 1-30 images par seconde (recommandé: 8)
- Liste de miniatures cliquables pour naviguer entre les frames
- Compteur "Frame 1/5" pour voir la position actuelle
- Badge 🎬 avec nombre de frames dans la bibliothèque
- 💾 **Stockage persistant côté serveur** : Les icônes WI sont maintenant sauvegardées dans `/data/custom_icons.json`
- Bibliothèque partagée entre tous les appareils (pas seulement le navigateur)
- Backup automatique avec Home Assistant
- API REST complète pour les icônes personnalisées :
  - `GET /api/icons` - Liste toutes les icônes
  - `GET /api/icons/{icon_id}` - Récupère une icône spécifique
  - `POST /api/icons/{icon_id}` - Sauvegarde ou met à jour une icône
  - `DELETE /api/icons/{icon_id}` - Supprime une icône
  - `POST /api/icons/{icon_id}/display` - Affiche une icône sur WLED

### Modifié
- **Breaking Change** : Endpoint `/show/mdi` renommé en `/show/icon`
- **Breaking Change** : Modèle `MdiRequest` renommé en `IconRequest`
- Champs formulaire renommés : `mdi` → `icon_id`, `mdi_fps` → `icon_fps`, `mdi_loop` → `icon_loop`
- Clés localStorage renommées : `wled_mdi` → `wled_icon_id`, etc.
- Format de stockage : `frames` (array de grilles) + `fps` au lieu de `grid` simple
- Les icônes WI animées affichent frame par frame avec le FPS spécifié
- Modèle `CustomIcon` support `frames` (optionnel) + `grid` (legacy, optionnel) + `fps`

### Amélioré
- Les icônes ne sont plus perdues lors du vidage du cache navigateur
- Les transformations (rotation, miroirs) s'appliquent à chaque frame des animations
- Compatibilité ascendante : les anciennes icônes avec `grid` fonctionnent toujours
- Les animations WI peuvent maintenant utiliser `animate`, `fps`, `loop` (incluant `-1` pour infini)
- Message de sauvegarde indique le nombre de frames : "✅ Icône sauvegardée : WI123 (3 frames)"
- Message de chargement indique aussi le nombre de frames

## [0.3.0] - 2025-11-17

### Ajouté
- 🎨 **Éditeur de pixel art 8x8** : Créez vos propres icônes directement dans l'interface
- Palette de 20 couleurs prédéfinies + sélecteur de couleur personnalisé
- Dessin au clic et au glissement (souris + tactile)
- Sauvegarde automatique dans localStorage
- Export PNG 8x8 pour téléchargement
- Envoi direct sur WLED depuis l'éditeur
- Boutons Effacer/Remplir pour édition rapide
- Support mobile et tablette complet

## [0.2.5] - 2025-11-16

### Optimisé
- Dockerfile multi-stage pour réduire la taille de l'image finale (-30% environ)
- Séparation build/runtime : compilation dans stage builder, runtime minimal dans stage final
- Ajout d'un fichier .dockerignore pour exclure fichiers inutiles du contexte Docker
- Installation sélective des bibliothèques (uniquement runtime, pas les paquets -dev)
- Optimisation des layers Docker avec nettoyage apt-get clean

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

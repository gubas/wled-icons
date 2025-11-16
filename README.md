# Contrôle WLED 8x8 avec icônes Material Design

Ce projet permet d'afficher des icônes Material Design (MDI) et des images (PNG/GIF) sur une matrice WLED 8x8, intégrable à Home Assistant.

## Approche
- Rendu d'une icône MDI / SVG / PNG / GIF et réduction en 8x8.
- Envoi direct à WLED via l'API JSON (`POST /json/state`) avec `seg.i` (tableau des 64 pixels RGB).
- Animation GIF: frames envoyées avec respect de la durée ou FPS forcé.
- Deux composants : Add-on (rendu + API) et Intégration Home Assistant (services).

## Installation / Déploiement
Utilisez uniquement l'add-on et l'intégration Home Assistant. Plus de dépendances Python à installer dans l'environnement principal.

### Publication GitHub & HACS
1. Créez un dépôt GitHub séparé (recommandé) pour l'intégration HACS:
```
wled-icons-hacs/
  hacs.json
  README.md
  custom_components/wled_icons/...
  .github/workflows/hacs.yml
```
2. Créez un autre dépôt pour l'add-on (ou dossier à la racine d'un dépôt add-ons):
```
wled-icons-addon-repo/
  repository.json
  wled_icons/
    config.json
    Dockerfile
    run.sh
    app/
      main.py
    requirements.txt
  README.md
```
3. Mettez à jour `repository.json` avec votre nom d'utilisateur et URL correcte.
4. Tagguez une release initiale pour l'intégration (ex: `v0.2.0`). Le champ `version` du `manifest.json` doit refléter la release.
5. Ajoutez le dépôt custom dans HACS: HACS > Intégrations > Menu > Dépôts personnalisés > URL + catégorie "Intégration".
6. Après validation, les utilisateurs peuvent rechercher "WLED Icons" dans HACS (ou l'ajouter depuis Dépôts Custom).
7. Pour l'add-on: Supervisor > Add-ons > Dépôts > Ajouter l'URL du dépôt add-on puis installer "WLED Icons".

### Versioning
- Utiliser SemVer: MAJ mineure pour nouvelles fonctions, patch pour corrections.
- Garder cohérence entre tag Git et `manifest.json`.
- L'add-on peut avoir un numéro distinct; documenter compatibilité dans README.

### Fichiers ajoutés
- `hacs.json`: nécessaire à la racine du repo HACS pour le rendu README.
- `translations/`: support multilingue config flow + services.
- `repository.json`: index pour le dépôt d'add-ons.
- Workflow `.github/workflows/hacs.yml`: validation HACS et lint minimal add-on.

### Étapes de Release Intégration
1. Incrémenter `manifest.json` version.
2. Mettre à jour README si besoin.
3. Créer tag `vX.Y.Z` sur GitHub.
4. Vérifier Actions (HACS validation green).
5. Annoncer changelog (voir suggestion section Roadmap / Ajouts).

### Licence
Projet sous licence MIT. Voir fichier `LICENSE` à la racine.

## Icônes Material Design (MDI)
- Fournissez simplement le nom de l'icône (ex: `home`, `weather-sunny`) au service ou endpoint.
- Une couleur hex optionnelle peut recoloriser toutes les zones non transparentes (ex: `#00AEEF`).
- Les SVG sont récupérés depuis le dépôt officiel MDI puis rasterisés en 8x8 par l'add-on.

Autres sources:
- SVG personnalisé (envoyé via endpoint `/show/svg` depuis un client externe si besoin — non exposé dans l'intégration pour l'instant).
- PNG 8x8 ou GIF animé stockés dans `/config/www` et utilisés via services `show_static` / `show_gif`.

## Rendu des icônes
Le rendu est effectué par l'add-on (FastAPI) :
- `GET /` UI Ingress (formulaire simple de test)
- `POST /show/mdi` (JSON: `host`, `name`, `color?`)
- `POST /show/png` (JSON: `host`, `png` base64)
- `POST /show/gif` (JSON: `host`, `gif` base64, `fps?`, `loop?`)

L'intégration Home Assistant appelle ces endpoints et expose des services plus simples qui utilisent la configuration enregistrée (host WLED, addon_url).

## Historique
Ancienne implémentation (script standalone + blueprint / shell_command) retirée pour réduire la maintenance. Utiliser exclusivement add-on + intégration.

## Module complémentaire (Add-on) + Intégration

Pour éviter les soucis de dépendances (CairoSVG) dans Home Assistant, utilisez l'add-on et l'intégration fournie:

1) Add-on:
- Copiez le dossier `addon/wled_icons/` dans votre dépôt local d'add-ons (`/addons/wled_icons/` si vous utilisez le partage local) puis installez-le depuis l'UI Supervisor (Add-ons > Bouton menu > Dépôts > Ajouter dépôt local si nécessaire).
- Démarrez l'add-on. Il écoute par défaut sur le port `8234`.

2) Intégration (custom component):
- Copiez `custom_components/wled_icons/` dans `/config/custom_components/wled_icons/`.
- Redémarrez Home Assistant. Vous disposez de services:
  - `wled_icons.show_mdi` (champs: `host`, `name`, `color`, `addon_url`)
  - `wled_icons.show_static` (champs: `host`, `file`, `addon_url`)
  - `wled_icons.show_gif` (champs: `host`, `file`, `fps`, `loop`, `addon_url`)

3) Exemples d'appel (dans Outils de développement > Services):
```yaml
service: wled_icons.show_mdi
data:
  host: 192.168.1.50
  name: home
  color: "#00AEEF"
  addon_url: http://homeassistant.local:8234
```

```yaml
service: wled_icons.show_gif
data:
  host: 192.168.1.50
  file: /config/www/anim.gif
  fps: 8
  loop: 2
  addon_url: http://homeassistant.local:8234
```

Notes:
- Si `addon_url` est omis, l'intégration tentera un rendu local (PNG/GIF OK; MDI nécessite `cairosvg` dans l'environnement HA, déconseillé).
- L'add-on effectue le rendu des MDI/SVG et envoie les frames à WLED; pour GIF, il respecte la durée des frames ou FPS forcé.
- L'UI Ingress de l'add-on fournit une page de test immédiat (Supervisor > Add-ons > WLED Icons > Ouvrir Ingress).

### Configuration via UI (config flow)
Après copie du dossier `custom_components/wled_icons/`, un redémarrage permet d'ajouter l'intégration depuis Paramètres > Appareils & Services > Ajouter une intégration > "WLED Icons". Elle demande:
 - Host WLED (ex: 192.168.1.50)
 - URL add-on (ex: http://homeassistant.local:8234) facultatif

Une fois ajoutée, les services peuvent être appelés sans fournir `host` ni `addon_url` (ils utilisent la config). Vous pouvez toujours surcharger en passant explicitement `host`/`addon_url` si nécessaire.

## Roadmap
- Cache local des SVG MDI pour usage hors-ligne
- Palette optimisée / dithering
- Presets WLED générés dynamiquement

## Notes d'environnement HA
- Aucun paquet supplémentaire à installer dans l'environnement Core HA : tout le rendu graphique est délégué à l'add-on (container séparé).
- Le fallback local (sans add-on) pour MDI est déconseillé car dépend de `cairosvg`.

## Licence & Remarques
Projet publié sous licence MIT (voir fichier `LICENSE`).

Les icônes Material Design sont sous licence Apache 2.0 (Pictogrammers/Templarian).
Ne pas distribuer d'icônes tierces sous copyright sans autorisation.

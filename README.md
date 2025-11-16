# Contrôle WLED 8x8 avec icônes Material Design

Ce projet permet d'afficher des icônes Material Design (MDI) et des images (PNG/GIF) sur une matrice WLED 8x8, intégrable à Home Assistant.

## Approche
- Rendu d'une icône MDI / SVG / PNG / GIF et réduction en 8x8.
- Envoi direct à WLED via l'API JSON (`POST /json/state`) avec `seg.i` (tableau des 64 pixels RGB).
- Animation GIF: frames envoyées avec respect de la durée ou FPS forcé.
- Deux composants : Add-on (rendu + API) et Intégration Home Assistant (services).

## Installation / Déploiement
Utilisez uniquement l'add-on et l'intégration Home Assistant. Plus de dépendances Python à installer dans l'environnement principal.

### Publication GitHub
1. (Same repo) Créez un dépôt GitHub et placez les deux composants au même endroit:
```
gubas/wled-icons/ (repo unique recommandé)
  README.md
  custom_components/wled_icons/...
  .github/workflows/ (CI workflows)
```
2. Placez l'add-on dans le répertoire `wled_icons/` du même dépôt:
```
gubas/wled-icons/
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
3. Mettez à jour `repository.json` avec votre nom d'utilisateur et URL correcte (ex: `https://github.com/gubas/wled-icons`).
4. Tagguez une release initiale pour l'intégration (ex: `v0.2.0`). Le champ `version` du `manifest.json` doit refléter la release.
5. Après push et tag, créez une release GitHub pour l'intégration (non obligatoire).
7. Pour l'add-on: Supervisor > Add-ons > Dépôts > Ajouter l'URL du dépôt add-on puis installer "WLED Icons".

### Versioning
- Utiliser SemVer: MAJ mineure pour nouvelles fonctions, patch pour corrections.
- Garder cohérence entre tag Git et `manifest.json`.
- L'add-on peut avoir un numéro distinct; documenter compatibilité dans README.

### Fichiers ajoutés
- `translations/`: support multilingue config flow + services.
- `repository.json`: index pour le dépôt d'add-ons.
 - Workflow `.github/workflows/`: CI workflows (validation, publish).

### Étapes de Release Intégration
1. Incrémenter `manifest.json` version.
2. Mettre à jour README si besoin.
3. Créer tag `vX.Y.Z` sur GitHub.
4. Vérifier Actions (CI green).
5. Annoncer changelog (voir suggestion section Roadmap / Ajouts).

### Release checklist — Add-on
1. Vérifier `addon/wled_icons/config.json`: le champ `version` doit être mis à jour et `slug` est correct.
2. Créer un tag Git et pousser les sources (ex: `git tag v0.2.0 && git push --tags`).
3. Créez une release GitHub. Ajoutez changelog et notes. Publier release va déclencher la CI de publication d'image.
4. L'action `publish_addon.yml` construira une image multi-arch (GHCR) et la publiera automatiquement lors d'une release. Pour que GHCR accepte la publication, autorisez `GITHUB_TOKEN` (normalement fourni automatiquement par GitHub Actions).
5. Optionnel: si vous souhaitez que le Supervisor télécharge l'image directement (au lieu de builder localement), définissez `image` dans `addon/wled_icons/config.json` pour pointer sur `ghcr.io/gubas/wled-icons-addons:vX.Y.Z`.

### Release checklist — Integration
1. Mettre à jour `custom_components/wled_icons/manifest.json` avec la nouvelle `version`.
2. Mettre à jour la section changelog pour la nouvelle version (`CHANGELOG.md`).
3. Créer un tag et release GitHub (ex: `v0.2.0`).
4. Vérifiez le pipeline ci et corrigez toute erreur éventuelle.

### Publier l'intégration
1. Poussez le tag `vX.Y.Z` et publiez la release.
2. Mettre à jour `CHANGELOG.md` et `manifest.json`.
3. L'intégration est prête pour l'installation manuelle par l'utilisateur.

### Publish GHCR / Docker (optionnel mais recommandé pour add-on)
1. Configurez GitHub Secrets (Settings -> Secrets) si vous voulez publier sur GHCR au delà de `GITHUB_TOKEN` (optionnel). Par défaut `GITHUB_TOKEN` suffit pour un repo public.
2. La CI `publish_addon.yml` est déclenchée sur une release : elle construit l'image multi-arch et la push vers `ghcr.io/gubas/wled-icons-addons:vX.Y.Z`.
3. Ajoutez ce tag en tant qu'image dans `addon/wled_icons/config.json` si vous voulez que Supervisor utilise l'image prête plutôt que builder localement.

### Exemple: Automation Home Assistant
Voici une automation simple qui affiche l'icône MDI "home" sur la matrice, puis active un effet WLED :

```yaml
alias: WLED Affiche Home + Rainbow
description: "Affiche l'icône home puis active l'effet Rainbow"
trigger:
  - platform: state
    entity_id: input_boolean.wled_trigger
    to: 'on'
action:
  - service: wled_icons.show_mdi
    data:
      name: home
      color: '#00AEEF'
  - delay: '00:00:02'  # attend 2 sec après affichage
  - service: light.turn_on
    target:
      entity_id: light.wled_matrix
    data:
      effect: Rainbow
mode: single
```

Note: Remplacez `input_boolean.wled_trigger` par le déclencheur de votre choix et `light.wled_matrix` par l'entité WLED dans votre Home Assistant.

### Tester l'add-on (local / debug)
1. Build localement (hors HA):
```bash
docker build -t wled_icons_test ./addon/wled_icons
docker run --rm -p 8234:8234 wled_icons_test
```
2. Ouvrez `http://localhost:8234` pour tester l'UI Ingress (même si hors Supervisor) ; utilisez les boutons pour envoyer des icônes au WLED host.
3. Vérifier logs si erreur: `docker logs <container>` ou depuis Supervisor : Add-ons > WLED Icons > Logs.

### Troubleshooting courant
-- L'intégration ne s'affiche pas: vérifiez la release GitHub et la valeur `version` dans `manifest.json`, puis exécutez la CI.
- Add-on ne démarre pas: vérifier `config.json` (champs `slug`, `name`, `version`). Assurez-vous que `run.sh` est exécutable. Vérifiez les logs du conteneur dans Supervisor.
- Ingress ne s'affiche pas: assurez-vous que l'add-on a `ingress: true` dans config.json et que l'utilisateur a accès (Supervisor configuration, network).
- Images MDI manquantes: Si une icône MDI n'est pas trouvée, vérifiez le nom (ex: `weather-sunny`) et que le repo MDI est accessible. L'add-on retourne 404 si non trouvé.
- Problèmes GHCR: si la CI ne publie pas l'image, vérifiez les logs d'Actions et si la permission pour `GITHUB_TOKEN` a le scope `packages:write` (par défaut c'est correct pour le même repo).

### Mise à jour rapide (workflow)
- `@main`: développement
 - `git tag vX.Y.Z && git push --tags`: crée release et déclenche publication GHCR.

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

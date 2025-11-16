# WLED Icons - Affichage d'icônes LaMetric sur matrice LED 8x8

Affichez des icônes **LaMetric animées** sur votre matrice WLED 8x8 directement depuis Home Assistant.

## ✨ Fonctionnalités

- 🎨 **Icônes LaMetric** : Plus de 1800 icônes 8x8 pixel-art optimisées pour LED
- 🎬 **GIFs animés** : Support complet des animations LaMetric avec contrôle FPS/boucles
- 🔄 **Transformations** : Rotation (0/90/180/270°) et miroirs (H/V) pour orientation matrice
- 🎨 **Recolorisation** : Changement de couleur des icônes monochromes
- 📤 **Upload personnalisé** : Envoi de vos propres GIFs 8x8
- 🌓 **Interface moderne** : UI responsive avec support dark mode
- 🏠 **Intégration HA** : Services Home Assistant pour automatisations

## 📦 Architecture

- **Add-on Home Assistant** : FastAPI server avec Ingress UI (port 8234)
- **Intégration custom** : Services HA + config flow
- **API LaMetric** : Téléchargement direct des icônes depuis `developer.lametric.com`

## 🚀 Installation

### 1. Ajout du dépôt d'add-ons

Dans Home Assistant :
1. **Paramètres** → **Modules complémentaires** → **Dépôt de modules complémentaires**
2. Ajoutez : `https://github.com/gubas/wled-icons`
3. Installez **"WLED Icons"**
4. Démarrez l'add-on

### 2. Installation de l'intégration

**Option A - Installation manuelle** :
1. Téléchargez le dossier `custom_components/wled_icons` depuis [GitHub](https://github.com/gubas/wled-icons)
2. Copiez-le dans `<config>/custom_components/wled_icons/`
3. Redémarrez Home Assistant complètement
4. **Paramètres** → **Appareils et services** → **+ Ajouter une intégration** → "WLED Icons"
5. Configurez :
   - **Adresse WLED** : IP de votre matrice (ex: `192.168.1.50`)
   - **URL Add-on** : `http://localhost:8234` (valeur par défaut)

**Option B - Via HACS** (après publication) :
1. HACS → Intégrations → Menu → Dépôts personnalisés
2. Ajoutez `https://github.com/gubas/wled-icons` (Intégration)
3. Recherchez "WLED Icons" et installez
4. Redémarrez Home Assistant
5. Ajoutez l'intégration via l'interface

## 🎮 Utilisation

### Interface Web (Ingress)

1. Ouvrez l'add-on → **Ouvrir l'interface web**
2. Entrez l'ID d'une icône LaMetric (ex: `1486` pour serpent animé)
3. Ajustez orientation, couleur, animation
4. Cliquez **"Afficher sur WLED"**

**Trouver des icônes** : [Galerie LaMetric](https://developer.lametric.com/icons)

### Services Home Assistant

L'intégration expose deux services pour vos automatisations :

#### `wled_icons.show_lametric`
Affiche une icône LaMetric (statique ou animée).

**Paramètres** :
- `icon_id` (string, **requis**) : ID LaMetric (ex: `1486`, `2867`)
- `host` (string, optionnel) : IP WLED (utilise la config si omis)
- `color` (string, optionnel) : Couleur hex pour recolorisation (ex: `#FF0000`)
- `rotate` (int, optionnel) : Rotation 0/90/180/270° (défaut: 0)
- `flip_h` (bool, optionnel) : Miroir horizontal
- `flip_v` (bool, optionnel) : Miroir vertical
- `animate` (bool, optionnel) : Activer animation GIF (défaut: true)
- `fps` (int, optionnel) : FPS forcé pour animation (sinon timing GIF original)
- `loop` (int, optionnel) : Nombre de boucles (défaut: 1, **-1 = infini**)
- `addon_url` (string, optionnel) : URL add-on (utilise la config si omis)

**Exemples** :
```yaml
# Icône statique simple
service: wled_icons.show_lametric
data:
  icon_id: "2"  # Maison

# Icône animée avec rotation
service: wled_icons.show_lametric
data:
  icon_id: "1486"  # Serpent animé
  rotate: 90
  animate: true
  fps: 10
  loop: 3

# Animation en boucle infinie
service: wled_icons.show_lametric
data:
  icon_id: "2867"  # Pluie animée
  loop: -1
```

#### `wled_icons.show_gif`
Affiche un GIF 8x8 personnalisé depuis le système de fichiers Home Assistant.

**Paramètres** :
- `file` (string, **requis**) : Chemin du GIF (ex: `/config/www/anim.gif`)
- `host` (string, optionnel) : IP WLED
- `fps` (int, optionnel) : FPS forcé
- `loop` (int, optionnel) : Nombre de boucles (**-1 = infini**)
- `addon_url` (string, optionnel) : URL add-on

**Exemple** :
```yaml
service: wled_icons.show_gif
data:
  file: "/config/www/custom_animation.gif"
  fps: 12
  loop: 2
```

### Automatisations

**Icône animée en boucle infinie** :
```yaml
alias: WLED Pluie Continue
trigger:
  - platform: state
    entity_id: binary_sensor.rain
    to: 'on'
action:
  - service: wled_icons.show_lametric
    data:
      icon_id: "2867"  # Pluie animée
      animate: true
      loop: -1  # Boucle infinie
```

**Stop animation (afficher icône statique)** :
```yaml
alias: WLED Stop Animation
trigger:
  - platform: state
    entity_id: binary_sensor.rain
    to: 'off'
action:
  - service: wled_icons.show_lametric
    data:
      icon_id: "2"  # Maison statique
      animate: false
```

**Notification avec orientation personnalisée** :
```yaml
alias: Notification Arrivée
trigger:
  - platform: state
    entity_id: person.john
    to: 'home'
action:
  - service: wled_icons.show_lametric
    data:
      icon_id: "2"  # Maison
      color: '#00FF00'
      rotate: 90
      flip_h: true
  - delay: '00:00:05'
  - service: light.turn_on
    target:
      entity_id: light.wled_matrix
    data:
      effect: Fireworks
```

**Animation temporisée** :
```yaml
alias: WLED Timer Icon
trigger:
  - platform: state
    entity_id: timer.cooking
    to: 'active'
action:
  - service: wled_icons.show_lametric
    data:
      icon_id: "1486"  # Animation serpent
      fps: 8
      loop: 5  # 5 boucles puis s'arrête
```

## 🛠️ Développement

### Structure du projet
```
gubas/wled-icons/
├── custom_components/wled_icons/   # Intégration HA
│   ├── __init__.py                 # Setup integration
│   ├── config_flow.py              # Config UI
│   ├── manifest.json               # Metadata
│   └── translations/               # i18n (en/fr)
├── wled_icons/                     # Add-on
│   ├── config.json                 # Add-on config
│   ├── Dockerfile                  # Multi-arch build
│   ├── app/
│   │   ├── main.py                 # FastAPI server
│   │   └── index.html              # Web UI
│   └── requirements.txt
├── .github/workflows/
│   ├── validate.yml                # CI checks
│   └── publish_addon.yml           # Docker publish GHCR
├── repository.json                 # Add-on repository index
└── README.md
```

### Test local (Docker)
```bash
docker build -t wled_icons_test ./wled_icons
docker run --rm -p 8234:8234 wled_icons_test
# Ouvrez http://localhost:8234
```

### Versioning

**Add-on** : Incrémentez `wled_icons/config.json` → `version` à chaque changement pour forcer rebuild Home Assistant.

**Intégration** : Incrémentez `custom_components/wled_icons/manifest.json` → `version` puis tagguez Git `vX.Y.Z`.

**SemVer** :
- **Major** : Breaking changes API
- **Minor** : Nouvelles fonctionnalités
- **Patch** : Bugfixes

### Publication

**Add-on** :
1. Mise à jour `wled_icons/config.json` version
2. Tag Git + GitHub Release
3. CI `publish_addon.yml` publie sur GHCR multi-arch

**Intégration** :
1. Mise à jour `manifest.json` version
2. Mise à jour `CHANGELOG.md`
3. Tag Git `vX.Y.Z` + GitHub Release

## 🐛 Dépannage

**L'intégration n'apparaît pas** :
- Vérifiez que le dossier est bien dans `<config>/custom_components/wled_icons/`
- Redémarrez Home Assistant **complètement** (pas juste reload)
- Consultez les logs : **Paramètres** → **Système** → **Journaux** (cherchez "wled_icons")
- Vérifiez le fichier `manifest.json` (doit contenir `"domain": "wled_icons"`)

**Erreur 500 au chargement du config flow** :
- Vérifiez que tous les fichiers sont présents (surtout `translations/`)
- Version minimum : Home Assistant 2024.6.0
- Consultez les logs pour plus de détails

**Icône ne s'affiche pas** :
- Vérifiez que l'add-on est démarré et accessible
- Testez l'URL add-on : `http://localhost:8234` dans un navigateur
- Vérifiez IP WLED dans la config de l'intégration
- Testez WLED directement : `curl -X POST http://<IP>/json/state -d '{"on":true}'`
- Vérifiez les logs de l'add-on : **Add-ons** → **WLED Icons** → **Logs**

**L'add-on ne démarre pas** :
- Vérifiez les logs de l'add-on pour les erreurs
- Assurez-vous que le port 8234 n'est pas déjà utilisé
- Rebuild l'add-on après mise à jour (incrémenter version force rebuild)

**UI add-on ne se met pas à jour** :
- Version incrémentée dans `config.json` ?
- Redémarrez l'add-on après rebuild
- Videz le cache navigateur (Ctrl+Shift+R ou Cmd+Shift+R)

**Animation saccadée** :
- Réglez le paramètre `fps` (recommandé : 8-12 FPS pour 8x8)
- Vérifiez la latence réseau vers WLED
- Utilisez une connexion filaire si possible

**Animation ne boucle pas infiniment** :
- Vérifiez que `loop: -1` est bien défini
- Version add-on 0.2.3+ requise pour support boucle infinie
- Consultez les logs pour voir si l'animation s'arrête prématurément

**Icône mal orientée** :
- Utilisez les paramètres `rotate` (0/90/180/270) et `flip_h`/`flip_v`
- Testez via l'interface web de l'add-on pour trouver la bonne orientation
- Sauvegardez les valeurs qui fonctionnent (localStorage dans le navigateur)

## 📚 Ressources

- [Galerie LaMetric Icons](https://developer.lametric.com/icons) : 1800+ icônes
- [API WLED](https://kno.wled.ge/interfaces/json-api/) : Documentation JSON API
- [Awtrix3](https://github.com/Blueforcer/awtrix3) : Inspiration LaMetric

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique complet des versions.

## 🤝 Contribution

Issues et PRs bienvenues sur GitHub : [gubas/wled-icons](https://github.com/gubas/wled-icons)

## 📄 Licence

MIT

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

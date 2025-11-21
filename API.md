# Documentation API REST - WLED Icons

Version: 0.6.7

L'add-on WLED Icons expose une API REST complète pour l'automatisation et le contrôle avancé des panneaux WLED depuis Home Assistant ou d'autres outils.

## Table des matières

- [Endpoints Icônes](#endpoints-icônes)
- [Endpoints WLED](#endpoints-wled)
- [Endpoints Automatisation](#endpoints-automatisation)
- [Exemples Home Assistant](#exemples-home-assistant)

---

## Endpoints Icônes

### `GET /api/icons`

Récupère la liste de toutes les icônes personnalisées.

**Réponse :**
```json
{
  "icons": [
    {
      "id": "WI1731932400123456",
      "name": "Coeur",
      "grid": [["#FF0000", ...], ...],
      "date": "2025-11-18T10:30:00"
    }
  ]
}
```

---

### `POST /api/icons`

Crée une nouvelle icône personnalisée.

**Body :**
```json
{
  "id": "WI1731932400123456",
  "name": "Mon icône",
  "grid": [
    ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
    ...
  ]
}
```

**Réponse :**
```json
{
  "ok": true,
  "id": "WI1731932400123456"
}
```

---

### `DELETE /api/icons/{icon_id}`

Supprime une icône personnalisée.

**Réponse :**
```json
{
  "ok": true,
  "deleted": "WI1731932400123456"
}
```

---

### `GET /api/icons/search?q={query}&limit={limit}`

Recherche des icônes par nom ou ID.

**Paramètres :**
- `q` : Terme de recherche (nom ou ID partiel)
- `limit` : Nombre max de résultats (défaut: 20)

**Exemple :**
```bash
GET /api/icons/search?q=coeur&limit=10
```

**Réponse :**
```json
{
  "icons": [
    {
      "id": "WI1731932400123456",
      "name": "Coeur rouge",
      "grid": [...]
    }
  ],
  "count": 1
}
```

---

## Endpoints WLED

### `POST /api/wled/brightness`

Ajuste la luminosité du panneau WLED sans modifier le contenu.

**Body :**
```json
{
  "host": "192.168.1.100",
  "brightness": 128
}
```

**Réponse :**
```json
{
  "ok": true,
  "brightness": 128
}
```

---

### `POST /api/wled/state`

Récupère l'état actuel du panneau WLED.

**Body :**
```json
{
  "host": "192.168.1.100"
}
```

**Réponse :**
```json
{
  "on": true,
  "bri": 255,
  "seg": [...],
  ...
}
```

---

### `POST /api/wled/on`

Allume le panneau WLED.

**Body :**
```json
{
  "host": "192.168.1.100"
}
```

---

### `POST /api/wled/off`

Éteint le panneau WLED.

**Body :**
```json
{
  "host": "192.168.1.100"
}
```

---

## Endpoints Automatisation

### `POST /api/icons/bulk-display`

Affiche plusieurs icônes séquentiellement (diaporama).

**Body :**
```json
{
  "icons": ["WI1731932400123456", "WI1731932400789012"],
  "host": "192.168.1.100",
  "duration": 2.0,
  "brightness": 200,
  "rotate": 0,
  "flip_h": false,
  "flip_v": false
}
```

**Paramètres :**
- `icons` : Liste des IDs d'icônes à afficher
- `host` : Adresse IP du WLED
- `duration` : Durée d'affichage par icône en secondes (défaut: 2.0)
- `brightness` : Luminosité 0-255 (défaut: 255)
- `rotate` : Rotation 0/90/180/270° (défaut: 0)
- `flip_h` : Miroir horizontal (défaut: false)
- `flip_v` : Miroir vertical (défaut: false)

**Réponse :**
```json
{
  "ok": true,
  "displayed": ["WI1731932400123456", "WI1731932400789012"],
  "count": 2
}
```

---

### `POST /show/icon`

Affiche une icône LaMetric ou personnalisée (WI) sur WLED.

**Body :**
```json
{
  "icon_id": "1486",
  "host": "192.168.1.100",
  "color": "#FF0000",
  "brightness": 200,
  "rotate": 0,
  "flip_h": false,
  "flip_v": false,
  "animate": true,
  "fps": 8,
  "loop": -1
}
```

**Paramètres :**
- `icon_id` : ID LaMetric (ex: "1486") ou ID personnalisé (ex: "WI1731932400123456")
- `host` : Adresse IP du WLED
- `color` : Couleur hex pour recolorisation (optionnel)
- `brightness` : Luminosité 1-255 (défaut: 255)
- `rotate` : Rotation 0/90/180/270° (défaut: 0)
- `flip_h` : Miroir horizontal (défaut: false)
- `flip_v` : Miroir vertical (défaut: false)
- `animate` : Activer l'animation pour les GIFs (défaut: true)
- `fps` : FPS forcé pour l'animation (optionnel, sinon timing GIF)
- `loop` : Nombre de boucles, -1 = infini (défaut: 1)

**Réponse :**
```json
{
  "ok": true,
  "source": "lametric"
}
```

---

### `POST /stop`

Arrête l'animation en cours et rend la main à WLED.

**Body :**
```json
{
  "host": "192.168.1.100"
}
```

**Réponse :**
```json
{
  "ok": true,
  "message": "Animation stopped"
}
```

---

## Exemples Home Assistant

### Script: Afficher un message d'accueil

```yaml
script:
  wled_welcome:
    sequence:
      - service: rest_command.wled_bulk_display
        data:
          icons: ["WI1731932400001", "WI1731932400002", "WI1731932400003"]
          duration: 3
          brightness: 150
```

### REST Command: Luminosité WLED

```yaml
rest_command:
  wled_set_brightness:
    url: "http://homeassistant.local:8234/api/wled/brightness"
    method: POST
    content_type: "application/json"
    payload: '{"host": "{{ host }}", "brightness": {{ brightness }}}'
```

### Automation: WLED nocturne

```yaml
automation:
  - alias: "WLED luminosité nocturne"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: rest_command.wled_set_brightness
        data:
          host: "192.168.1.100"
          brightness: 50
```

### REST Command: Recherche d'icônes

```yaml
rest_command:
  wled_search_icons:
    url: "http://homeassistant.local:8234/api/icons/search?q={{ query }}&limit=10"
    method: GET
```

### REST Command: Diaporama d'icônes

```yaml
rest_command:
  wled_bulk_display:
    url: "http://homeassistant.local:8234/api/icons/bulk-display"
    method: POST
    content_type: "application/json"
    payload: >
      {
        "icons": {{ icons | tojson }},
        "host": "{{ host }}",
        "duration": {{ duration | default(2.0) }},
        "brightness": {{ brightness | default(255) }}
      }
```

### Automation: Météo du matin

```yaml
automation:
  - alias: "Météo matinale WLED"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: rest_command.wled_bulk_display
        data:
          host: "192.168.1.100"
          icons: >
            {% if is_state('weather.home', 'sunny') %}
              ["WI_SUNNY", "WI_TEMP_HIGH"]
            {% elif is_state('weather.home', 'rainy') %}
              ["WI_RAIN", "WI_UMBRELLA"]
            {% else %}
              ["WI_CLOUDY"]
            {% endif %}
          duration: 5
          brightness: 200
```

---

## Notes

- Toutes les requêtes retournent des codes HTTP standards (200 OK, 404 Not Found, 502 Bad Gateway)
- Les erreurs de connexion WLED retournent 502 avec un message détaillé
- La luminosité est appliquée à la fois au niveau RGB (calcul pixel par pixel) et au niveau WLED (paramètre `bri`)
- Les transformations (rotation, miroir) sont appliquées avant l'envoi au WLED
- L'historique undo/redo n'est disponible que dans l'interface web (pas via API)

---

**Base URL** : L'add-on est accessible via l'ingress Home Assistant ou directement sur le port 8234.

Exemples :
- Ingress : `http://homeassistant.local:8123/api/hassio_ingress/xxx/api/icons`
- Direct : `http://homeassistant.local:8234/api/icons`

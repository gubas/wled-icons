# Version 0.5.8 - Résumé des changements

## 🎨 Nouvelles fonctionnalités créatives

### 1. Outil Pipette 🎨
- Cliquez sur un pixel pour copier sa couleur
- Bouton pipette dans la barre d'outils
- Le curseur change en mode pipette
- Message de confirmation avec la couleur copiée

### 2. Symétrie automatique 🪞
- **Symétrie horizontale** (↔️) : Miroir gauche-droite en temps réel
- **Symétrie verticale** (↕️) : Miroir haut-bas en temps réel
- Combinable : Activez les deux pour symétrie centrale (4 quadrants)
- Boutons avec feedback visuel (actif/inactif)

### 3. Historique Undo/Redo ⏮️⏭️
- Annuler jusqu'à 50 actions
- **Raccourcis clavier** :
  - `Ctrl+Z` (ou `Cmd+Z` sur Mac) : Annuler
  - `Ctrl+Y` ou `Ctrl+Shift+Z` : Refaire
- Buffer circulaire intelligent (garde les 50 dernières actions)
- Sauvegarde automatique avant chaque dessin
- Messages de confirmation à chaque undo/redo

## 💡 Contrôle de luminosité

### Slider de luminosité
- Range 1-255 (norme WLED)
- Appliqué avant l'envoi au panneau
- **Double application** :
  1. Calcul RGB pixel par pixel : `r = r * brightness / 255`
  2. Paramètre WLED `bri` dans le payload
- Affichage en temps réel de la valeur
- Message de confirmation avec la luminosité utilisée

## 🔌 API REST étendue

7 nouveaux endpoints pour l'automatisation avancée :

### 1. Contrôle luminosité
```http
POST /api/wled/brightness
Body: {"host": "192.168.1.100", "brightness": 128}
```

### 2. État WLED
```http
POST /api/wled/state
Body: {"host": "192.168.1.100"}
```

### 3. Allumer WLED
```http
POST /api/wled/on
Body: {"host": "192.168.1.100"}
```

### 4. Éteindre WLED
```http
POST /api/wled/off
Body: {"host": "192.168.1.100"}
```

### 5. Affichage séquentiel (diaporama)
```http
POST /api/icons/bulk-display
Body: {
  "icons": ["WI1234", "WI5678"],
  "host": "192.168.1.100",
  "duration": 2.0,
  "brightness": 200
}
```

### 6. Recherche d'icônes
```http
GET /api/icons/search?q=coeur&limit=10
```

### 7. Paramètre brightness ajouté
Tous les endpoints d'envoi supportent maintenant `brightness: 0-255`

## 📚 Documentation

- **API.md** : Documentation complète de tous les endpoints
- **test_api.py** : Script de test pour valider les nouveaux endpoints
- **README.md** : Mise à jour avec les nouvelles fonctionnalités
- **Exemples Home Assistant** : REST commands et automations

## 🔧 Améliorations techniques

### Interface utilisateur
- Style `.active` pour les boutons d'outils sélectionnés
- Curseur qui change selon l'outil (crosshair pour dessin, cell pour pipette)
- Contrôle de luminosité intégré dans la grille (2 colonnes)
- Design cohérent avec le reste de l'interface

### Backend
- Fonction `send_frame()` accepte maintenant `brightness` en paramètre
- Logs améliorés pour debug (brightness, payload complet)
- Gestion d'erreur robuste pour tous les endpoints
- Support timeout de 5s pour requêtes WLED

### Code
- Buffer circulaire pour historique (limite mémoire)
- Deep copy des grids pour éviter mutations
- Event listeners keyboard avec preventDefault
- Support Ctrl/Cmd pour compatibilité Mac/Windows/Linux

## 🎯 Cas d'usage

### Créatif
1. **Dessin symétrique** : Créer des icônes symétriques rapidement (cœurs, étoiles...)
2. **Copie de couleurs** : Pipette pour réutiliser des couleurs exactes
3. **Expérimentation** : Undo/Redo pour tester sans crainte

### Automatisation
1. **Slideshow d'icônes** : Afficher plusieurs icônes séquentiellement
2. **Luminosité adaptative** : Ajuster selon l'heure (jour/nuit)
3. **Recherche intelligente** : Trouver des icônes par nom ou ID
4. **Contrôle complet** : On/Off/Brightness via Home Assistant

## 📊 Statistiques

- **Lignes ajoutées** : ~180 lignes (HTML + Python)
- **Nouveaux endpoints** : 7
- **Nouvelles fonctions JS** : 5 (saveToHistory, undo, redo, toggleTool, toggleSymmetry)
- **Nouveaux boutons UI** : 6 (Draw, Pipette, Undo, Redo, SymH, SymV)
- **Nouvelles classes Pydantic** : 3 (BrightnessRequest, WLEDStateRequest, BulkDisplayRequest)

## ⚡ Performance

- Historique : O(1) pour undo/redo (accès direct à l'index)
- Limite mémoire : 50 états × 64 pixels × 7 bytes = ~22 KB max
- Symétrie : Calcul en temps réel sans impact visible
- Pipette : Lecture instantanée de la couleur au clic

## 🔄 Compatibilité

- Rétro-compatible avec 0.5.7 (aucune breaking change)
- API REST backward compatible (nouveaux endpoints seulement)
- Format de stockage icônes inchangé
- Intégration Home Assistant compatible

## 📝 Notes de version

Cette version transforme l'éditeur en outil professionnel avec :
- Confort d'édition (undo/redo, pipette)
- Outils créatifs (symétrie)
- Contrôle précis (luminosité)
- Automatisation avancée (7 nouveaux endpoints)

Idéal pour :
- Créer des icônes complexes rapidement
- Automatiser des scénarios d'affichage
- Contrôler finement l'apparence des LEDs
- Intégrer dans des systèmes domotiques avancés

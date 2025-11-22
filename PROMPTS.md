# Commandes Copilot Raccourcies

Ce fichier contient des raccourcis pour les tâches répétitives du projet WLED Icons.

## 🚀 Release

**Commande :** `release VERSION`

**Exemple :** `release 0.7.4`

**Ce qui sera fait :**
1. Analyser les commits depuis le dernier tag
2. Générer un changelog détaillé avec emojis
3. Synchroniser l'intégration (custom_components → addon/wled_icons/integration)
4. Mettre à jour la version dans config.json
5. Mettre à jour VERSION dans README.md
6. Ajouter l'entrée dans les 2 CHANGELOG.md
7. Créer commit git + tag
8. Afficher les commandes de push

---

## 📝 Autres raccourcis utiles

### `sync-integration`
Copie custom_components/wled_icons vers addon/wled_icons/integration

### `update-version X.X.X`
Met à jour uniquement le numéro de version (config.json + README.md)

### `changelog MESSAGE`
Ajoute une entrée de changelog avec la version actuelle

### `check-integration`
Vérifie que l'intégration est synchronisée avec l'add-on (endpoints, services, etc.)

---

## 📋 Pour utiliser ces raccourcis

Utilise simplement le format :
```
@workspace /release 0.7.4
```

Ou demande directement :
```
Fais une release 0.7.4
```

Je comprendrai et exécuterai automatiquement toutes les étapes !

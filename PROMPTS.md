# Commandes Copilot Raccourcies

Ce fichier contient des raccourcis pour les tâches répétitives du projet WLED Icons.

## 🚀 Release (AUTOMATIQUE)

**Commande :** `release VERSION` ou `/release VERSION`

**Exemple :** `release 0.7.5`

**Ce qui sera fait AUTOMATIQUEMENT (sans confirmation) :**

1. ✅ **Analyser les commits** depuis le dernier tag
2. ✅ **Générer un changelog détaillé** avec emojis basé sur les commits
3. ✅ **Synchroniser l'intégration** : `custom_components/wled_icons` → `addon/wled_icons/integration`
4. ✅ **Mettre à jour la version** dans `addon/wled_icons/config.json`
5. ✅ **Mettre à jour le README** : VERSION X.X.X
6. ✅ **Ajouter l'entrée** dans les 2 `CHANGELOG.md` (racine + addon)
7. ✅ **Commit git** : `Release vX.X.X: [message généré]`
8. ✅ **Créer le tag** : `vX.X.X`
9. ✅ **Push automatique** : `git push wled-icons main && git push wled-icons vX.X.X`

**Message final :** Lien vers la release GitHub

---

## 📝 Autres raccourcis utiles

### `sync-integration`
Copie `custom_components/wled_icons` vers `addon/wled_icons/integration`

### `check-integration`
Vérifie que l'intégration est synchronisée avec l'add-on (endpoints, services, paramètres)

### `update-docs`
Met à jour API.md avec les endpoints actuels de l'add-on

---

## 🎯 Utilisation

Tape simplement dans le chat :
```
release 0.7.5
```

Ou avec slash :
```
/release 0.7.5
```

Je m'occupe de tout automatiquement ! 🚀

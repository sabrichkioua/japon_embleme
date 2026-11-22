V0.8 - Filtrage chromatique expérimental

1. Conserver data.geojson, prefectures.geojson et images/ à côté de index.html.
2. Renommer atlas_japon_v08_couleurs.html en index.html.
3. Exécuter : python3 extraction_couleurs_emblemes.py --site /chemin/vers/dossier/site
4. Vérifier la création de emblem_colors.json et emblem_colors.csv.
5. Recharger la page depuis un serveur HTTP local.
6. Tester dominant et présent (>= 10 % de pixels opaques).

Sans emblem_colors.json, le filtre reste désactivé, le reste de l'atlas fonctionne.
Le script d'analyse est exploratoire : les nuances et les pixels d'anticrénelage peuvent affecter les résultats.
Ne pas publier emblem_colors.csv si inutile.

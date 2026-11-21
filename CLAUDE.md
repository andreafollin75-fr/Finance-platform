# Projet : plateforme gratuite de suivi de l'actualité financière (avec explications)

> Ce fichier est le brief du projet. Lis-le en entier avant d'écrire du code.
> Les sections marquées **[À CONFIRMER]** contiennent des choix par défaut que je peux modifier : pose-moi la question avant de coder si tu as un doute.

## 0. Règle de langue (prioritaire) : TOUT EN ANGLAIS

**Tout ce qui est produit dans ce projet doit être en anglais**, sans exception :
- l'interface du site (menus, boutons, titres, messages d'erreur, pages « About » et « Legal ») ;
- tout le contenu pédagogique (glossaire, leçons, parcours, briefings) ;
- les sources de données : uniquement des sources en anglais ;
- le code (noms de variables, de fonctions, de fichiers et de dossiers), les commentaires, les messages de commit, le `README.md`, `SOURCES.md` et toute la documentation ;
- l'avertissement légal et les étiquettes (ex. « automatic summary »).

Seule exception : **ce brief `CLAUDE.md` reste en français**, et tu peux me parler en français dans la conversation. Tout ce que tu écris dans le projet, lui, est en anglais.

Si tu hésites sur la traduction d'un terme financier, utilise le terme standard employé dans la presse financière anglophone.

## 1. Objectif

Créer un site web personnel, que je pourrai partager plus tard, qui me permet de suivre l'actualité financière mise à jour automatiquement, avec :
- des explications et du contexte sur les news ;
- des analyses simples ;
- des explications de notions financières (glossaire, leçons), accessibles à un public non expert.

Public cible : débutant à intermédiaire, lecteurs anglophones. **[À CONFIRMER]**

## 2. Contrainte principale : 100 % gratuit

- Aucun service payant, aucune carte bancaire requise.
- Hébergement : site **statique** sur GitHub Pages (ou Cloudflare Pages).
- Automatisation : GitHub Actions (dépôt public), exécution planifiée (cron) toutes les 30 à 60 minutes.
- Données : uniquement des sources gratuites (RSS, API ouvertes ou avec clé gratuite).
- Pas de base de données serveur : les données sont des fichiers JSON/Markdown versionnés ou générés au build.
- **Aucune dépendance obligatoire à une API d'IA payante.** Le site doit fonctionner entièrement sans IA (voir section 5).

## 3. Périmètre éditorial **[À CONFIRMER]**

- Thèmes par défaut : Europe, États-Unis, macro-économie et banques centrales, marchés (indices, taux, devises, matières premières).
- Crypto : hors périmètre au départ, à ajouter plus tard si je le demande.
- Langue de l'interface, du contenu et des sources : anglais uniquement (voir section 0).

## 4. Architecture proposée

Tu peux proposer mieux, mais explique pourquoi et reste dans la contrainte « gratuit et statique ».

- **Pipeline de données (Python)** : récupère les flux RSS, nettoie, déduplique, classe par thème, écrit des fichiers JSON dans `data/`.
- **Site (Astro, ou autre générateur statique simple)** : lit `data/` et le contenu Markdown (`content/`) et génère les pages.
- **Déploiement** : workflow GitHub Actions qui lance le pipeline, build le site et déploie sur GitHub Pages, sur planning et à chaque push.
- Structure indicative (noms en anglais) :

```
/pipeline        Python scripts (fetch, dedupe, classify, export)
/data            generated JSON (news, markets, calendar)
/content
  /glossary      one concept = one .md file
  /learning-paths   short lessons, ordered
/site            static site code
/.github/workflows
```

### Sources de données (à vérifier, tester et documenter dans `SOURCES.md`)
- Flux RSS de médias financiers anglophones, de la BCE (ECB), de la Fed, de la Bank of England, etc. Vérifie que chaque flux existe vraiment et fonctionne avant de l'ajouter.
- FRED (clé gratuite), Eurostat, BCE (API de données statistiques), SEC EDGAR pour les résultats d'entreprises US.
- Données de marché : privilégie des sources gratuites et stables. Si tu utilises une source non officielle (ex. Yahoo Finance via bibliothèque tierce), isole-la derrière une interface pour pouvoir la remplacer, et gère les pannes.

Pour chaque source : respecter les conditions d'utilisation, mettre un User-Agent explicite, limiter la fréquence des requêtes, et mettre en cache.

## 5. Fonctionnalités par phases

### Phase 1 : MVP (priorité absolue, sans IA)
1. Récupération des flux RSS configurables dans un fichier `pipeline/sources.yml` (nom, URL, thème).
2. Déduplication et regroupement simple des articles proches.
3. Page d'accueil : fil d'actualité filtrable par thème, avec titre, source, date, extrait court et **lien vers l'article original**.
4. Glossaire (« Glossary ») : au moins 40 notions rédigées par toi en anglais (voir liste en annexe), chacune avec définition simple, exemple concret, pourquoi c'est important, notions liées.
5. Détection automatique des termes du glossaire dans les titres/extraits, avec infobulle ou lien vers la définition.
6. Page « Daily Briefing » : sélection des news les plus importantes (règle de scoring simple et documentée : nombre de sources qui en parlent, fraîcheur, thème).
7. Workflow GitHub Actions fonctionnel avec déploiement automatique.

### Phase 2
- Tableau de bord de marché (indices, taux, devises, matières premières) avec graphiques simples et accessibles.
- Calendrier économique (réunions de banques centrales, publications d'inflation, emploi, etc.).
- Parcours d'apprentissage (« Learning Paths ») : 10 à 15 leçons courtes, de « What is a stock? » à « Understanding a central bank decision ».
- Recherche dans le site (côté client, ex. Pagefind).
- Watchlist et filtres sauvegardés côté navigateur (localStorage).
- Flux RSS du site lui-même, et mode sombre.

### Phase 3 (optionnel, seulement si je le demande)
- Résumés et explications automatiques via une **API d'IA à offre gratuite** (clé stockée dans les secrets GitHub, jamais dans le code).
  - Doit être strictement optionnel : activé par une variable d'environnement.
  - Repli obligatoire : si l'appel échoue ou si le quota est atteint, on affiche le titre et l'extrait sans résumé, sans casser le build.
  - Mettre en cache les résumés déjà générés pour ne jamais consommer deux fois le même appel.
  - Les résumés ne doivent contenir aucun chiffre qui ne figure pas dans la source.
  - Les contenus générés sont clairement étiquetés « Automatic summary ».
  - Les résumés sont rédigés en anglais.
- Digest hebdomadaire (« Weekly Digest »).

## 6. Règles de contenu et légales (non négociables)

- **Ne jamais republier un article en entier** : titre, courte description fournie par le flux, et lien vers la source uniquement.
- Chaque page d'actualité cite la source et renvoie vers elle.
- Mention visible sur tout le site, en anglais : *« Educational and informational content only. This site does not provide investment advice. »* Et une page « About / Legal » qui l'explique.
- Pas de recommandations d'achat/vente, pas de prévisions de cours présentées comme certaines.
- Contenu pédagogique : exact, nuancé, en anglais clair, sans jargon non expliqué. Si tu n'es pas sûr d'un fait, ne l'invente pas : signale-le-moi.
- Pas de chiffres inventés : tout chiffre affiché vient d'une source de données identifiée, avec sa date.

## 7. Qualité et robustesse

- Le pipeline ne doit jamais faire échouer tout le déploiement parce qu'une source est en panne : log de l'erreur, on garde les dernières données valides.
- Tests pour la déduplication, la classification, la détection de termes du glossaire.
- Accessibilité (contrastes, navigation clavier, responsive mobile d'abord).
- Performances : pages légères, pas de gros frameworks côté client sans raison.
- Code commenté simplement (en anglais), `README.md` clair (en anglais) : comment ajouter une source, une notion de glossaire, lancer en local, déployer.
- Pas de secret dans le dépôt. Si une clé API est nécessaire, documente où la créer (gratuitement) et comment l'ajouter aux secrets GitHub.

## 8. Méthode de travail

1. Commence par me poser les questions **[À CONFIRMER]** restantes (maximum 5, groupées), puis propose un plan court de la Phase 1.
2. Attends mon accord sur le plan, puis construis par petites étapes.
3. Fais des commits fréquents et clairs (messages de commit en anglais).
4. À la fin de chaque étape : dis-moi ce qui fonctionne, ce que j'ai à tester, et ce qui reste.
5. Teste réellement ce que tu écris (lance le pipeline, ouvre le site en local) avant de dire que c'est terminé.
6. Si une contrainte « gratuit » est menacée (limite de quota, service qui devient payant), préviens-moi au lieu de contourner.

## 9. Critères de réussite de la Phase 1

- [ ] Le dépôt est public et le site est en ligne sur une URL gratuite.
- [ ] Le fil d'actualité se met à jour tout seul au moins toutes les heures.
- [ ] Au moins 8 sources RSS anglophones fonctionnelles, configurables dans `sources.yml`.
- [ ] Au moins 40 notions dans le glossaire, avec détection automatique dans les titres.
- [ ] Une page « Daily Briefing » générée sans IA.
- [ ] Page « About / Legal » et avertissement présents.
- [ ] Tout le site, le code et la documentation sont en anglais.
- [ ] README permettant à quelqu'un d'autre de reproduire le projet.

## Annexe : notions de glossaire à rédiger en priorité (en anglais)

Inflation, deflation, policy rate (key interest rate), ECB, Fed, interest rate, spread, government bonds (Treasuries, Bunds, OATs), bond yield, bond, stock (share), dividend, stock index (S&P 500, Nasdaq, Euro Stoxx 50), ETF, P/E ratio, market capitalization, volatility, VIX, bull and bear markets, recession, GDP, unemployment rate, trade balance, public debt, budget deficit, quantitative easing, quantitative tightening, yield curve, yield curve inversion, exchange rate (EUR/USD), commodities, oil (Brent, WTI), gold, liquidity, leverage, short selling, derivatives, options, quarterly earnings, guidance, IPO, mergers and acquisitions, credit rating, systemic risk, diversification, compound interest.

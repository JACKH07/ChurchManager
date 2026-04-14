# ChurchManager - Système de Gestion Ecclésiastique

Application web complète de gestion d'église avec hiérarchie à 5 niveaux, gestion des fidèles, cotisations, événements et rapports.

## Stack Technique

| Couche | Technologie |
|--------|-------------|
| Frontend | React.js 18 + TypeScript + Vite |
| UI | TailwindCSS v3 + composants personnalisés |
| Graphiques | Recharts |
| State | Zustand + React Query |
| Backend | Django 6 + Django REST Framework |
| Auth | JWT (SimpleJWT) + RBAC |
| BDD | SQLite (dev) / PostgreSQL (prod) |
| Cache/Queue | Redis + Celery |
| Conteneurs | Docker + Docker Compose |

## Démarrage rapide

### Prérequis

- Python 3.12+
- Node.js 18+
- (optionnel) Docker + Docker Compose

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

L'application sera disponible sur **http://localhost:5173**

### Avec Docker Compose (recommandé pour la production)

```bash
docker-compose up -d
```

## Accès par défaut

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Super Admin | admin@churchmanager.org | Admin@2026! |

## Architecture hiérarchique

```
National
  └── Région (code 2 lettres)
        └── District (code 2 chiffres)
              └── Paroisse (code 3 chiffres)
                    └── Église Locale (code 3 chiffres)
                          └── Fidèle (code unique généré)
```

### Format du code fidèle

```
REG-DIS-PAR-EGL-XXXX-AAAA
AB - 01 - 003 - 012 - 0145 - 2024
```

## Modules disponibles

- ✅ **Tableau de bord** — KPIs, graphiques, alertes
- ✅ **Hiérarchie** — Régions, Districts, Paroisses, Églises
- ✅ **Fidèles** — Annuaire, carte de membre PDF + QR Code
- ✅ **Cotisations** — Enregistrement, validation, résumé financier
- ✅ **Événements** — Création, inscriptions, calendrier
- ✅ **Rapports** — Financiers et fidèles
- ✅ **Notifications** — Système de notifications en temps réel
- ✅ **RBAC** — 7 niveaux de rôles

## API Documentation

Une fois le backend lancé :
- Swagger UI : http://localhost:8000/api/docs/
- ReDoc : http://localhost:8000/api/redoc/

## Rôles et permissions

| Rôle | Périmètre |
|------|-----------|
| Super Admin | Tout |
| Admin National | Toute la hiérarchie |
| Admin Région | Sa région et au-dessous |
| Superviseur District | Son district |
| Chef Paroisse | Sa paroisse |
| Pasteur Local | Son église |
| Fidèle | Son profil |

## Variables d'environnement

Copier `.env.example` → `.env` dans le dossier `backend/` et `frontend/`.

## Structure du projet

```
ChurchManager/
├── backend/
│   ├── accounts/        # Authentification, utilisateurs, RBAC
│   ├── hierarchy/       # Régions, Districts, Paroisses, Églises
│   ├── members/         # Fidèles, Ministères, Transferts
│   ├── contributions/   # Cotisations, Paiements, Reçus
│   ├── events/          # Événements, Annonces
│   ├── notifications/   # Notifications utilisateurs
│   ├── reports/         # Dashboard, Rapports
│   └── config/          # Settings Django, URLs, Celery
├── frontend/
│   ├── src/
│   │   ├── api/         # Clients API Axios
│   │   ├── components/  # Composants UI réutilisables
│   │   ├── pages/       # Pages de l'application
│   │   ├── store/       # État global (Zustand)
│   │   └── utils/       # Utilitaires
│   └── public/
├── docker-compose.yml
└── README.md
```

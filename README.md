# SGA — Sistema de Gestión de Accidentes

Plataforma web para la gestión operativa y analítica del ciclo de vida completo de accidentes viales, con visualización geoespacial en tiempo real, despacho de emergencias y dashboard de KPIs.

---

## Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Frontend | Angular (standalone) | 21.x |
| UI | CSS plano (sin Tailwind), Leaflet 1.9.4 + MarkerCluster 1.5.3 (CDN) | — |
| Backend | Django + Django REST Framework | 5.x |
| Base de datos operacional | Apache Pinot (vía Kafka) | — |
| Mensajería | Kafka | — |
| Autenticación | JWT (djangorestframework-simplejwt) | — |
| Entorno | Python venv (backend) | 3.x |

---

## Estructura del Proyecto

```
/
├── frontend/                  # Angular standalone SPA
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/          # Servicios, modelos, interceptors, guards
│   │   │   ├── features/      # Páginas por rol (operador/, admin/)
│   │   │   └── shared/        # Componentes reutilizables
│   │   ├── assets/
│   │   └── types/             # Declaraciones .d.ts (Leaflet)
│   └── package.json
├── backend/                   # Django REST API
│   ├── accidentes/
│   │   ├── views/             # auth_views, accidente_views, catalogo_views
│   │   ├── services/          # Lógica de negocio (accidente_service, kafka_repo, pinot_repo)
│   │   ├── serializers/       # DRF serializers
│   │   └── management/        # Comandos seed (seed_auth_users, seed_data)
│   └── core/                  # settings.py, urls.py globales
├── database/                  # Scripts SQL, schemas
├── uml/                       # Diagramas
├── docker-compose.yml         # Infraestructura (Kafka, Pinot, ZK)
└── SGA(...).md                # SRS — Especificación de Requerimientos
```

---

## Cómo ejecutar

### Backend

```bash
cd backend
# Activar venv (Windows)
.\venv\Scripts\Activate.ps1
# Activar venv (Linux/Mac)
source venv/bin/activate

python manage.py migrate
python manage.py seed_data          # Seed completo de datos en Kafka/Pinot
python manage.py seed_auth_users    # Crear 4 usuarios JWT
python manage.py runserver
```

El backend corre en `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
ng serve
```

El frontend corre en `http://localhost:4200`.

---

## Usuarios JWT (seed)

| Usuario | Rol | Contraseña |
|---------|-----|-----------|
| `operador_sga` | Operador | `sga_secure_pwd_2026` |
| `admin_sga` | Administrador | `sga_secure_pwd_2026` |
| `supervisor_sga` | Supervisor | `sga_secure_pwd_2026` |
| `despachador_sga` | Despachador | `sga_secure_pwd_2026` |

Endpoint de login: `POST /api/v1/auth/login/` con JSON `{ "username": "...", "password": "..." }`.

---

## Convenciones y Decisiones de Arquitectura

### Frontend
- **Componentes standalone** (no NgModules).
- **Signals** para estado reactivo (no RxJS BehaviorSubject para estado local).
- **CSS plano con variables CSS** — paleta oscura táctica con colores desaturados. No usar Tailwind ni librerías UI externas.
- **Leaflet vía CDN** (no npm). Tipos declarados en `src/types/leaflet.d.ts`. MarkerCluster añadido vía CDN (`leaflet.markercluster` 1.5.3) con severidad por colores en iconos de cluster.
- **Marcadores SVG personalizados** — pines con gradiente cromático por severidad (sin números), animación de pulso para accidentes activos, efecto hover (escala + glow). Popups rediseñados con cabecera degradada, badge de severidad y estadísticas SVG inline.
- **Estilo Double-Bezel** en cards: `border-radius: 10px`, transiciones `cubic-bezier(0.16, 1, 0.3, 1)` 200ms.
- **Interceptor HTTP** para JWT (`auth.interceptor.ts`) y manejo de errores (`error.interceptor.ts`).
- **Rutas públicas**: `/mapa` (AllowAny). **Rutas protegidas**: `/dashboard`, `/lista`, `/registro` (requieren auth. guard).

### Backend
- **DRF con JWTAuthentication + IsAuthenticated** por defecto. Vistas públicas (catálogos, mapa) tienen `permission_classes = [AllowAny]`.
- **Servicios separados**: `accidente_service.py` (lógica de negocio), `pinot_repo.py` (consultas a Pinot), `kafka_repo.py` (producción de eventos).
- **Vistas DRF puras** (no ViewSets) para control fino.
- **JWT sin refresh token** configurado; el frontend persiste el token en `localStorage`.

---

## Errores Conocidos y Cómo Evitarlos

### 1. Mismatch de valores de estado (frontend ↔ backend)
**Error**: El listado muestra `ACTIVO` en vez de `Reportado`, y los filtros no funcionan.

**Causa**: El backend seedea los estados como `ACTIVO`, `EN_ATENCION`, `CONTROLADO`, `ARCHIVADO`. El frontend debe usar EXACTAMENTE esos valores en el array `estados[]` de `lista-accidentes.ts`.

**Solución**: Mapa de estados en `lista-accidentes.ts:62`:
```typescript
readonly estados = [
  { value: 'ACTIVO', label: 'Reportado', ... },
  { value: 'EN_ATENCION', label: 'En Atención', ... },
  { value: 'CONTROLADO', label: 'Despejado', ... },
  { value: 'ARCHIVADO', label: 'Archivado', ... }
];
```

### 2. `idelementofisico_id` hardcodeado en registro
**Error**: Al registrar un accidente, el campo `idelementofisico_id` siempre se enviaba como `1`.

**Causa**: El método `buildPayload()` usaba `idelementofisico_id: 1` en vez de mapear los checkboxes.

**Solución**: `matchElementoFisicoId()` en `registro-accidente.ts:522` que busca en el catálogo `elementosFisicos` la combinación exacta de checkboxes seleccionados.

### 3. `idestadoclima_id` hardcodeado
**Error**: Similar al anterior, se enviaba `idestadoclima_id: 1`.

**Causa**: Frontend hardcodeaba 1, backend usaba `=` en vez de `LIKE` para matchear nombres bilingües (el catálogo puede tener "Soleado" o "Sunny").

**Solución**: Backend usa `LIKE '%{cond_escaped}%'` y frontend usa el valor seleccionado del dropdown de clima.

### 4. Comboboxes de ubicación no se llenan al editar
**Error**: Al editar un accidente, los comboboxes de país/estado/ciudad/calle no se seleccionan automáticamente.

**Causa**: El método `poblarCascadaConIds()` fallaba cuando los IDs numéricos no coincidían exactamente con los valores de los arrays de opciones, y no tenía fallback por nombre.

**Solución**: Agregar fallback por nombre de calle/ciudad, tolerar ID=0, validación con función `pid()`.

### 5. Estados duplicados en seed data
**Nota**: Los seed data de `tiposestadosincidentes` tienen 5 registros, pero IDs 2 y 3 tienen nombres distintos (`EN_ATENCION` vs `EN_TRASLADO`). El mapeo en el servicio trata ambos como `EN_ATENCION`. Si se agregan nuevos estados, actualizar TAMBIÉN el `estados_catalogo` en `accidente_service.py` y el array `estados[]` en `lista-accidentes.ts`.

### 6. `idusuario_id` hardcodeado
Al crear/actualizar accidentes y estados, `idusuario_id` se envía como `1`. No se usa el usuario autenticado del JWT. Pendiente de corregir.

### 7. Tipos de TypeScript para MarkerCluster no declarados
**Error**: `L.markerClusterGroup` da error de tipo en compilación (`Property 'markerClusterGroup' does not exist on type 'typeof L'`).

**Causa**: `leaflet.markercluster` no tiene tipos nativos. Solo se declararon tipos mínimos en `leaflet.d.ts`.

**Solución**: Ya declarado en `src/types/leaflet.d.ts`. Si se actualiza la librería, verificar que los tipos sigan siendo compatibles con la sintaxis `L.markerClusterGroup()`.

### 8. Dashboard lento por múltiples queries secuenciales a Pinot
**Error**: El dashboard tarda varios segundos en cargar porque ejecuta 7 queries secuenciales a Pinot.

**Causa**: Cada llamada a `PinotRepository.execute_query()` es una request HTTP síncrona. 6 queries con JOINs usan multi-stage engine, que es más lento.

**Solución implementada**: 
- Caché en memoria con Django `LocMemCache` (TTL 60s) — la primera carga puede tardar, las siguientes son instantáneas.
- KPIs combinados en una sola query (antes eran 2 separadas).
- Timeout reducido de 15s a 5s para fallar rápido si Pinot no responde.

---

## Flujo de Autenticación

1. Usuario ingresa credenciales en `LoginModalComponent`.
2. `AuthService.login()` envía POST a `/auth/login/`.
3. Backend valida contra `django.contrib.auth.models.User` y devuelve JWT + refresh token.
4. Frontend guarda access token, refresh token y username en `localStorage`.
5. `auth.interceptor.ts` adjunta `Authorization: Bearer <token>` a cada request HTTP.
6. Si el servidor responde 401, el interceptor intenta renovar el token via `POST /auth/refresh/` con el refresh token guardado.
7. Si el refresh es exitoso, se re-intenta la request original con el nuevo token.
8. Si el refresh falla, se limpia la sesión y redirige a `/mapa`.
9. `auth.guard.ts` protege rutas redirigiendo a `/mapa` si no hay sesión.
10. `AuthService.restoreSession()` en el constructor restaura sesión desde `localStorage` al recargar la página.

---

## Flujo de Estado de Accidente

```
Reportado (ACTIVO) → En Atención (EN_ATENCION) → Despejado (CONTROLADO) → Archivado (ARCHIVADO)
```

- Cada transición crea un registro en `accidentestiposestadosincidentes_topic` (Kafka → Pinot).
- El estado actual se resuelve consultando el registro con `MAX(fechahoramodificado)` por accidente.
- El listado y detalle usan `estado_actual` resuelto en backend (nunca hardcodeado).

---

## Catálogos (públicos, AllowAny)

| Endpoint | Descripción |
|----------|-------------|
| `POST /api/v1/auth/refresh/` | Renovar JWT (refresh token) |
| `GET /api/v1/catalogos/paises/` | Países |
| `GET /api/v1/catalogos/estados/` | Estados/provincias por país |
| `GET /api/v1/catalogos/ciudades/` | Ciudades por estado |
| `GET /api/v1/catalogos/calles/` | Calles por ciudad |
| `GET /api/v1/catalogos/severidades/` | Niveles de severidad |
| `GET /api/v1/catalogos/tipos-accidente/` | Tipos de accidente |
| `GET /api/v1/catalogos/tipos-estado/` | Estados del incidente |
| `GET /api/v1/catalogos/estados-clima/` | Estados climáticos |
| `GET /api/v1/catalogos/elementos-fisicos/` | Elementos físicos de la vía |
| `GET /api/v1/catalogos/tipos-vehiculo/` | Tipos de vehículo |
| `GET /api/v1/catalogos/fuentes-reporte/` | Fuentes de reporte |

---

## Comandos Útiles

```bash
# Re-seedear datos de prueba
python manage.py seed_data

# Re-seedear usuarios JWT
python manage.py seed_auth_users

# Build frontend
cd frontend && npx ng build

# Verificar sintaxis Python
python -m py_compile accidentes/services/accidente_service.py
```

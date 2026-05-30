# SGA — Frontend

Angular 21 standalone SPA para el Sistema de Gestión de Accidentes.

---

## Stack

- Angular 21 (standalone, signals, effects)
- CSS plano (sin Tailwind ni librerías UI externas)
- Leaflet 1.9.4 vía CDN para mapas
- JWT auth via `djangorestframework-simplejwt`

---

## Estructura

```
src/app/
├── core/
│   ├── services/          # AuthService, AccidenteService, ToastService
│   ├── models/            # Interfaces TS (AccidenteDetalle, etc.)
│   ├── interceptors/      # auth.interceptor, error.interceptor
│   └── guards/            # auth.guard
├── features/
│   └── operador/          # dashboard, lista-accidentes, registro-accidente,
│                          # mapa-page, panel-detalle, actualizar-estado,
│                          # despacho-modal
├── shared/
│   └── components/        # login-modal, badge-severidad
└── types/                 # leaflet.d.ts
```

---

## Comandos

```bash
ng serve          # Dev en http://localhost:4200
ng build          # Producción en dist/
```

---

## Convenciones Frontend

- **Signals** para estado reactivo local (no RxJS BehaviorSubject).
- **CSS plano con variables** (paleta en `styles.css`). No Tailwind.
- **Double-Bezel**: cards con `border-radius: 10px`, transiciones `cubic-bezier(0.16, 1, 0.3, 1)` 200ms.
- **Interceptor JWT**: adjunta `Bearer <token>` a cada request.
- **Leaflet CDN**: tipos en `types/leaflet.d.ts`, mapa cargado globalmente vía `<script>` en `index.html`.

---

## Errores Frecuentes

### Estados (ACTIVO, EN_ATENCION, etc.)
Los valores del backend para `estado_actual` son `ACTIVO`, `EN_ATENCION`, `CONTROLADO`, `ARCHIVADO`. El array `estados[]` en `lista-accidentes.ts` debe usar esos values. Ver README raíz.

### Leaflet sin tipos
Instalado global vía CDN. No importar desde npm. El archivo `types/leaflet.d.ts` declara `declare var L: any`.

### JWT expirado
Sin refresh token. Si da 401, redirigir a login. Sesión persiste en `localStorage` (claves `sga_token` y `sga_username`).

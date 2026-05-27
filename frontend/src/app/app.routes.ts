import { Routes } from '@angular/router';
import { DashboardComponent } from './features/operador/dashboard/dashboard';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'mapa', 
    loadComponent: () => import('./features/operador/mapa-page/mapa-page').then(m => m.MapaPageComponent) 
  },
  { 
    path: 'registro-accidente', 
    loadComponent: () => import('./features/operador/registro-accidente/registro-accidente').then(m => m.RegistroAccidenteComponent),
    canActivate: [authGuard]
  },
  { 
    path: 'accidentes', 
    loadComponent: () => import('./features/operador/lista-accidentes/lista-accidentes').then(m => m.ListaAccidentesComponent),
    canActivate: [authGuard]
  },
  { path: '**', redirectTo: 'dashboard' }
];


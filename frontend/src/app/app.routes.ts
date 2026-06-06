import { Routes } from '@angular/router';
import { DashboardComponent } from './features/PKG1_Gestion_Accidentes/CU20_Dashboard_KPIs/dashboard';
import { authGuard } from './core/guards/auth.guard';
import { analistaGuard } from './core/guards/analista.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'mapa', 
    loadComponent: () => import('./features/PKG1_Gestion_Accidentes/CU02_Visualizar_Mapa/mapa-page').then(m => m.MapaPageComponent) 
  },
  { 
    path: 'mapa-publico', 
    loadComponent: () => import('./features/PKG4_Portal_Externo/CU15_Consultar_Mapa_Publico/mapa-publico-page/mapa-publico-page').then(m => m.MapaPublicoPageComponent) 
  },
  { 
    path: 'registro-accidente', 
    loadComponent: () => import('./features/PKG1_Gestion_Accidentes/CU01_Registrar_Accidente/registro-accidente').then(m => m.RegistroAccidenteComponent),
    canActivate: [authGuard]
  },
  { 
    path: 'accidentes', 
    loadComponent: () => import('./features/PKG3_Consulta_Analisis/CU10_Buscar_Accidentes/lista-accidentes').then(m => m.ListaAccidentesComponent),
    canActivate: [authGuard]
  },
  { 
    path: 'analitico', 
    loadComponent: () => import('./features/PKG3_Consulta_Analisis/layout-analitico/layout-analitico').then(m => m.LayoutAnaliticoComponent),
    canActivate: [authGuard, analistaGuard],
    children: [
      { 
        path: 'accidentes', 
        loadComponent: () => import('./features/PKG3_Consulta_Analisis/CU10_Buscar_Accidentes/lista-analitico/lista-accidentes-analitico').then(m => m.ListaAccidentesAnaliticoComponent) 
      },
      { 
        path: 'expediente/:id', 
        loadComponent: () => import('./features/PKG3_Consulta_Analisis/CU14_Solicitar_Expediente/expediente/expediente').then(m => m.ExpedienteComponent) 
      },
      { path: '', redirectTo: 'accidentes', pathMatch: 'full' }
    ]
  },
  { 
    path: 'responder', 
    loadComponent: () => import('./features/PKG2_Respuesta_Emergencias/CU07_Recibir_Despacho/recibir-despacho/recibir-despacho').then(m => m.RecibirDespachoComponent),
    canActivate: [authGuard]
  },
  { 
    path: 'unidades', 
    loadComponent: () => import('./features/PKG5_Administracion/CU17_Gestionar_Unidades_Emergencia/gestionar-unidades/gestionar-unidades').then(m => m.GestionarUnidadesComponent),
    canActivate: [authGuard]
  },
  { path: '**', redirectTo: 'dashboard' }
];


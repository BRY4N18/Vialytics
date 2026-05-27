import {
  Component,
  output,
  signal,
  computed,
  effect,
  inject,
  OnInit,
  OnDestroy,
  untracked,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { MapaService } from '../../../core/services/mapa.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class HeaderComponent implements OnInit, OnDestroy {
  readonly mapaService = inject(MapaService);
  readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  filtrosCambiados = output<{ severidad?: number; estado?: string }>();
  nuevoAccidenteClick = output<void>();

  readonly currentTime = signal(new Date());
  readonly isMapaRoute = signal(false);
  
  readonly selectedSeveridad = computed(() => this.mapaService.filtros().severidad);
  readonly selectedEstado = computed(() => this.mapaService.filtros().estado);
  readonly selectedFechaInicio = computed(() => this.mapaService.filtros().fecha_inicio);
  readonly selectedFechaFin = computed(() => this.mapaService.filtros().fecha_fin);

  // Dynamic date range constraints for citizen and operator
  readonly minDate = computed(() => {
    return ''; // No constraint, allowing custom date queries back in time
  });

  readonly maxDate = computed(() => {
    return this.formatDate(new Date()); // Restrict to today's date to prevent selecting future dates
  });

  readonly formattedTime = computed(() =>
    this.currentTime().toLocaleTimeString('es-EC', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  );

  readonly formattedDate = computed(() =>
    this.currentTime().toLocaleDateString('es-EC', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  );

  readonly severidades = [
    { value: 1, label: 'Leve', color: '#10B981' },
    { value: 2, label: 'Moderado', color: '#F59E0B' },
    { value: 3, label: 'Grave', color: '#EF4444' },
    { value: 4, label: 'Fatal', color: '#7C3AED' },
  ];

  readonly estados = [
    'ACTIVO',
    'EN_ATENCION',
    'CONTROLADO',
    'CERRADO',
    'ARCHIVADO',
  ];

  private clockInterval?: ReturnType<typeof setInterval>;
  private routerSub?: Subscription;

  constructor() {
    // Reset date range filters when login state changes to preserve role boundaries
    effect(() => {
      const logged = this.authService.isLoggedIn();
      const today = new Date();
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(today.getDate() - 7);

      const current = untracked(() => this.mapaService.filtros());
      this.mapaService.setFiltros({
        ...current,
        fecha_inicio: this.formatDate(sevenDaysAgo),
        fecha_fin: this.formatDate(today)
      });
    });
  }

  ngOnInit(): void {
    this.clockInterval = setInterval(() => {
      this.currentTime.set(new Date());
    }, 1000);

    // Track active route to show/hide filters (only visible on map page)
    this.isMapaRoute.set(this.router.url.includes('/mapa'));
    this.routerSub = this.router.events.subscribe(() => {
      this.isMapaRoute.set(this.router.url.includes('/mapa'));
    });
  }

  ngOnDestroy(): void {
    if (this.clockInterval) clearInterval(this.clockInterval);
    if (this.routerSub) this.routerSub.unsubscribe();
  }

  private formatDate(date: Date): string {
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  onSeveridadChange(value: string): void {
    const sev = value ? Number(value) : undefined;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      severidad: sev
    });
    this.emitFiltros();
  }

  onEstadoChange(value: string): void {
    const est = value || undefined;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      estado: est
    });
    this.emitFiltros();
  }

  onFechaInicioChange(value: string): void {
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      fecha_inicio: value || undefined
    });
    this.emitFiltros();
  }

  onFechaFinChange(value: string): void {
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      fecha_fin: value || undefined
    });
    this.emitFiltros();
  }

  clearFiltros(): void {
    const today = new Date();
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(today.getDate() - 7);

    this.mapaService.setFiltros({
      fecha_inicio: this.formatDate(sevenDaysAgo),
      fecha_fin: this.formatDate(today)
    });
    this.emitFiltros();
  }

  private emitFiltros(): void {
    this.filtrosCambiados.emit({
      severidad: this.selectedSeveridad(),
      estado: this.selectedEstado(),
    });
  }

  onNuevoAccidente(): void {
    this.nuevoAccidenteClick.emit();
  }
}

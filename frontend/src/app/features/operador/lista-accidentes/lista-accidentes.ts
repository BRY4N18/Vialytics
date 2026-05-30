import { Component, OnInit, inject, signal, computed, effect, DestroyRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { AccidenteService } from '../../../core/services/accidente.service';
import { AccidenteMapa, Ciudad } from '../../../core/models/accidente.model';
import { ActualizarEstadoComponent } from '../actualizar-estado/actualizar-estado';

@Component({
  selector: 'app-lista-accidentes',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, ActualizarEstadoComponent],
  templateUrl: './lista-accidentes.html',
  styleUrl: './lista-accidentes.css'
})
export class ListaAccidentesComponent implements OnInit {
  private readonly accidenteService = inject(AccidenteService);
  private readonly destroyRef = inject(DestroyRef);

  readonly Math = Math;

  // Actualizar Estado signals
  readonly selectedAccidenteId = signal<string | null>(null);
  readonly selectedAccidenteEstado = signal<string | null>(null);
  readonly mostrarActualizarEstado = signal(false);

  // States
  readonly listadoOriginal = signal<AccidenteMapa[]>([]);
  readonly totalRecords = signal(0);
  readonly isLoading = signal(false);
  readonly errorMessage = signal<string | null>(null);

  // Filters (bound via inputs)
  readonly searchTerm = signal('');
  readonly filterSeveridad = signal<number | null>(null);
  readonly filterEstado = signal<string>('');
  readonly filterSoloActivos = signal(false);
  readonly filterCiudadId = signal<number | null>(null);
  readonly filterFechaDesde = signal<string>('');
  readonly filterFechaHasta = signal<string>('');
  readonly filterMinHeridos = signal<number | null>(null);
  readonly filterMaxHeridos = signal<number | null>(null);
  readonly filterMinFallecidos = signal<number | null>(null);
  readonly filterMaxFallecidos = signal<number | null>(null);

  // Catalog data for filters
  readonly ciudades = signal<Ciudad[]>([]);

  // Pagination
  readonly currentPage = signal(1);
  readonly itemsPerPage = 8;

  // Severidades catalog
  readonly severidades = [
    { value: 1, label: 'Leve', color: '#22A076', bg: 'rgba(34, 160, 118, 0.1)' },
    { value: 2, label: 'Moderado', color: '#D99726', bg: 'rgba(217, 151, 38, 0.1)' },
    { value: 3, label: 'Grave', color: '#DB5757', bg: 'rgba(219, 87, 87, 0.1)' },
    { value: 4, label: 'Fatal', color: '#844EDA', bg: 'rgba(132, 78, 218, 0.1)' }
  ];

  // Estados catalog — values must match backend seed data
  readonly estados = [
    { value: 'ACTIVO', label: 'Reportado', bg: 'rgba(82, 136, 224, 0.15)', color: '#5288E0' },
    { value: 'EN_ATENCION', label: 'En Atención', bg: 'rgba(217, 151, 38, 0.15)', color: '#D99726' },
    { value: 'CONTROLADO', label: 'Despejado', bg: 'rgba(34, 160, 118, 0.15)', color: '#22A076' },
    { value: 'ARCHIVADO', label: 'Archivado', bg: 'rgba(160, 160, 160, 0.15)', color: '#A0A0A0' }
  ];

  constructor() {
    effect(() => {
      const page = this.currentPage();
      const search = this.searchTerm();
      const sev = this.filterSeveridad();
      const est = this.filterEstado();
      const soloActivos = this.filterSoloActivos();
      const ciudadId = this.filterCiudadId();
      const fechaDesde = this.filterFechaDesde();
      const fechaHasta = this.filterFechaHasta();
      const minHeridos = this.filterMinHeridos();
      const maxHeridos = this.filterMaxHeridos();
      const minFallecidos = this.filterMinFallecidos();
      const maxFallecidos = this.filterMaxFallecidos();

      this.cargarAccidentesReactivo(
        page, search, sev, est, soloActivos,
        ciudadId, fechaDesde, fechaHasta,
        minHeridos, maxHeridos, minFallecidos, maxFallecidos
      );
    });
  }

  async ngOnInit(): Promise<void> {
    try {
      const c = await firstValueFrom(this.accidenteService.getCiudades());
      this.ciudades.set(c);
    } catch {}
  }

  cargarAccidentesReactivo(
    page: number, search: string, severidad: number | null, estado: string, soloActivos: boolean,
    ciudadId: number | null, fechaDesde: string, fechaHasta: string,
    minHeridos: number | null, maxHeridos: number | null,
    minFallecidos: number | null, maxFallecidos: number | null
  ): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.accidenteService.getAccidentesPaginados({
      page,
      page_size: this.itemsPerPage,
      search: search || undefined,
      severidad: severidad !== null ? severidad : undefined,
      estado: estado || undefined,
      solo_activos: soloActivos || undefined,
      ciudad_id: ciudadId ?? undefined,
      fecha_desde: fechaDesde || undefined,
      fecha_hasta: fechaHasta || undefined,
      min_heridos: minHeridos ?? undefined,
      max_heridos: maxHeridos ?? undefined,
      min_fallecidos: minFallecidos ?? undefined,
      max_fallecidos: maxFallecidos ?? undefined,
    }).subscribe({
      next: (data) => {
        this.listadoOriginal.set(data.results);
        this.totalRecords.set(data.total_records);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err.message || 'Error al conectar con la base de datos.');
        this.isLoading.set(false);
      }
    });
  }

  cargarAccidentes(): void {
    this.cargarAccidentesReactivo(
      this.currentPage(), this.searchTerm(), this.filterSeveridad(), this.filterEstado(),
      this.filterSoloActivos(), this.filterCiudadId(), this.filterFechaDesde(),
      this.filterFechaHasta(), this.filterMinHeridos(), this.filterMaxHeridos(),
      this.filterMinFallecidos(), this.filterMaxFallecidos()
    );
  }

  onAbrirActualizarEstado(acc: AccidenteMapa): void {
    this.selectedAccidenteId.set(acc.idaccidente);
    this.selectedAccidenteEstado.set(acc.estado_actual);
    this.mostrarActualizarEstado.set(true);
  }

  onCerrarActualizarEstado(): void {
    this.mostrarActualizarEstado.set(false);
    this.selectedAccidenteId.set(null);
    this.selectedAccidenteEstado.set(null);
    this.cargarAccidentes();
  }

  readonly paginatedAccidentes = computed(() => this.listadoOriginal());

  readonly totalVictimas = computed(() =>
    this.listadoOriginal().reduce((sum, acc) => sum + (acc.numheridos || 0) + (acc.numfallecidos || 0), 0)
  );

  readonly totalFallecidos = computed(() =>
    this.listadoOriginal().reduce((sum, acc) => sum + (acc.numfallecidos || 0), 0)
  );

  readonly totalHeridos = computed(() =>
    this.listadoOriginal().reduce((sum, acc) => sum + (acc.numheridos || 0), 0)
  );

  readonly totalPages = computed(() =>
    Math.ceil(this.totalRecords() / this.itemsPerPage) || 1
  );

  // Smart Pagination Visible Pages logic: displays 1 ... (curr-2) (curr-1) (curr) (curr+1) (curr+2) ... last
  readonly visiblePages = computed(() => {
    const current = this.currentPage();
    const total = this.totalPages();
    const pages: (number | string)[] = [];

    if (total <= 7) {
      for (let i = 1; i <= total; i++) {
        pages.push(i);
      }
    } else {
      pages.push(1);

      if (current > 4) {
        pages.push('...');
      }

      const start = Math.max(2, current - 2);
      const end = Math.min(total - 1, current + 2);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (current < total - 3) {
        pages.push('...');
      }

      pages.push(total);
    }

    return pages;
  });

  getSeveridadLabel(nivel: number): string {
    return this.severidades.find(s => s.value === nivel)?.label || 'Desconocido';
  }

  getSeveridadStyles(nivel: number) {
    const item = this.severidades.find(s => s.value === nivel);
    return {
      color: item?.color || '#9CA3AF',
      backgroundColor: item?.bg || 'rgba(255, 255, 255, 0.05)',
      border: `1px solid ${item?.color}33`
    };
  }

  getEstadoLabel(estado: string): string {
    return this.estados.find(e => e.value === estado)?.label || estado;
  }

  getEstadoStyles(estado: string) {
    const item = this.estados.find(e => e.value === estado);
    return {
      color: item?.color || '#9CA3AF',
      backgroundColor: item?.bg || 'rgba(255, 255, 255, 0.05)',
      border: `1px solid ${item?.color}33`
    };
  }

  cambiarPagina(pagina: number): void {
    if (pagina >= 1 && pagina <= this.totalPages()) {
      this.currentPage.set(pagina);
    }
  }

  onSeveridadSelect(value: any): void {
    const val = value === 'null' || value === null || value === '' ? null : Number(value);
    this.filterSeveridad.set(val);
    this.currentPage.set(1);
  }

  onCiudadSelect(value: any): void {
    const val = value === 'null' || value === '' || value === null ? null : Number(value);
    this.filterCiudadId.set(val);
    this.currentPage.set(1);
  }

  limpiarFiltros(): void {
    this.searchTerm.set('');
    this.filterSeveridad.set(null);
    this.filterEstado.set('');
    this.filterSoloActivos.set(false);
    this.filterCiudadId.set(null);
    this.filterFechaDesde.set('');
    this.filterFechaHasta.set('');
    this.filterMinHeridos.set(null);
    this.filterMaxHeridos.set(null);
    this.filterMinFallecidos.set(null);
    this.filterMaxFallecidos.set(null);
    this.currentPage.set(1);
  }

  onFilterKeydown(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (target) {
      target.value = target.value.replace(/[^0-9]/g, '');
    }
  }
}

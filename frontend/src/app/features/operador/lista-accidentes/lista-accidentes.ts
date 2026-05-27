import { Component, OnInit, inject, signal, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AccidenteService } from '../../../core/services/accidente.service';
import { AccidenteMapa } from '../../../core/models/accidente.model';

@Component({
  selector: 'app-lista-accidentes',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './lista-accidentes.html',
  styleUrl: './lista-accidentes.css'
})
export class ListaAccidentesComponent implements OnInit {
  private readonly accidenteService = inject(AccidenteService);

  readonly Math = Math;

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

  // Pagination
  readonly currentPage = signal(1);
  readonly itemsPerPage = 8;

  // Severidades catalog
  readonly severidades = [
    { value: 1, label: 'Leve', color: '#10B981', bg: 'rgba(16, 185, 129, 0.1)' },
    { value: 2, label: 'Moderado', color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)' },
    { value: 3, label: 'Grave', color: '#EF4444', bg: 'rgba(239, 68, 68, 0.1)' },
    { value: 4, label: 'Fatal', color: '#7C3AED', bg: 'rgba(124, 58, 237, 0.1)' }
  ];

  // Estados catalog
  readonly estados = [
    { value: 'ACTIVO', label: 'Activo', bg: 'rgba(59, 130, 246, 0.15)', color: '#3B82F6' },
    { value: 'EN_ATENCION', label: 'En Atención', bg: 'rgba(124, 58, 237, 0.15)', color: '#8B5CF6' },
    { value: 'CONTROLADO', label: 'Controlado', bg: 'rgba(16, 185, 129, 0.15)', color: '#10B981' },
    { value: 'CERRADO', label: 'Cerrado', bg: 'rgba(107, 114, 128, 0.15)', color: '#9CA3AF' },
    { value: 'ARCHIVADO', label: 'Archivado', bg: 'rgba(156, 163, 175, 0.08)', color: '#6B7280' }
  ];

  constructor() {
    // Reactive effect: reload data automatically when page, search or filters change
    effect(() => {
      const page = this.currentPage();
      const search = this.searchTerm();
      const sev = this.filterSeveridad();
      const est = this.filterEstado();
      const soloActivos = this.filterSoloActivos();

      this.cargarAccidentesReactivo(page, search, sev, est, soloActivos);
    });
  }

  ngOnInit(): void {}

  cargarAccidentesReactivo(page: number, search: string, severidad: number | null, estado: string, soloActivos: boolean): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.accidenteService.getAccidentesPaginados({
      page,
      page_size: this.itemsPerPage,
      search: search || undefined,
      severidad: severidad !== null ? severidad : undefined,
      estado: estado || undefined,
      solo_activos: soloActivos || undefined
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
    // Manually trigger reload by modifying current page (which kicks off the effect)
    const page = this.currentPage();
    this.cargarAccidentesReactivo(
      page, 
      this.searchTerm(), 
      this.filterSeveridad(), 
      this.filterEstado(), 
      this.filterSoloActivos()
    );
  }

  // Computed values based on loaded list items
  readonly paginatedAccidentes = computed(() => {
    return this.listadoOriginal();
  });

  readonly totalVictimas = computed(() => {
    return this.listadoOriginal().reduce((sum, acc) => sum + (acc.numheridos || 0) + (acc.numfallecidos || 0), 0);
  });

  readonly totalFallecidos = computed(() => {
    return this.listadoOriginal().reduce((sum, acc) => sum + (acc.numfallecidos || 0), 0);
  });

  readonly totalHeridos = computed(() => {
    return this.listadoOriginal().reduce((sum, acc) => sum + (acc.numheridos || 0), 0);
  });

  readonly totalPages = computed(() => {
    return Math.ceil(this.totalRecords() / this.itemsPerPage) || 1;
  });

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

  limpiarFiltros(): void {
    this.searchTerm.set('');
    this.filterSeveridad.set(null);
    this.filterEstado.set('');
    this.filterSoloActivos.set(false);
    this.currentPage.set(1);
  }
}

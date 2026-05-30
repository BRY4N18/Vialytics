import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { MapaComponent } from '../mapa/mapa';
import { PanelDetalleComponent } from '../panel-detalle/panel-detalle';
import { DespachoComponent } from '../despacho/despacho';
import { ActualizarEstadoComponent } from '../actualizar-estado/actualizar-estado';
import { MapaService } from '../../../core/services/mapa.service';
import { AuthService } from '../../../core/services/auth.service';
import { AccidenteService } from '../../../core/services/accidente.service';
import { AccidenteMapa, Pais, Estado, Condado, Ciudad, Calle } from '../../../core/models/accidente.model';

@Component({
  selector: 'app-mapa-page',
  standalone: true,
  imports: [
    CommonModule,
    MapaComponent,
    PanelDetalleComponent,
    DespachoComponent,
    ActualizarEstadoComponent
  ],
  templateUrl: './mapa-page.html',
  styleUrl: './mapa-page.css'
})
export class MapaPageComponent implements OnInit, OnDestroy {
  readonly mapaService = inject(MapaService);
  readonly authService = inject(AuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly accidenteService = inject(AccidenteService);

  readonly selectedAccidenteId = signal<string | null>(null);
  readonly selectedAccidenteEstado = signal<string | null>(null);

  readonly mostrarDespacho = signal(false);
  readonly mostrarActualizarEstado = signal(false);
  readonly filtrosAbiertos = signal(true);

  // CatÃ¡logos de ubicaciÃ³n
  readonly paisesList = signal<Pais[]>([]);
  readonly estadosList = signal<Estado[]>([]);
  readonly condadosList = signal<Condado[]>([]);
  readonly ciudadesList = signal<Ciudad[]>([]);
  readonly callesList = signal<Calle[]>([]);

  private querySub?: Subscription;

  readonly severidades = [
    { value: 1, label: 'Leve', color: '#10B981' },
    { value: 2, label: 'Moderado', color: '#F59E0B' },
    { value: 3, label: 'Grave', color: '#EF4444' },
    { value: 4, label: 'Fatal', color: '#7C3AED' },
  ];

  readonly estados = [
    'Reportado',
    'Asignado',
    'En Escena',
    'Despejado',
    'Archivado',
  ];



  ngOnInit(): void {
    this.querySub = this.route.queryParams.subscribe(params => {
      const selectedId = params['selected'];
      if (selectedId) {
        this.selectedAccidenteId.set(selectedId);
      }
    });
    this.cargarPaises();
  }

  ngOnDestroy(): void {
    this.querySub?.unsubscribe();
  }

  onAccidenteSeleccionado(accidente: AccidenteMapa): void {
    if (!this.authService.isLoggedIn()) return;
    this.selectedAccidenteId.set(accidente.idaccidente);
    this.selectedAccidenteEstado.set(accidente.estado_actual);
  }

  onUbicacionSeleccionada(loc: { lat: number; lng: number }): void {
    console.log('MapaPage - UbicaciÃ³n seleccionada:', loc);
  }

  onCerrarDetalle(): void {
    this.selectedAccidenteId.set(null);
    this.selectedAccidenteEstado.set(null);
  }

  onAbrirDespacho(): void {
    this.mostrarDespacho.set(true);
  }

  onCerrarDespacho(): void {
    this.mostrarDespacho.set(false);
    this.mapaService.refrescar();
    const id = this.selectedAccidenteId();
    if (id) {
      this.selectedAccidenteId.set(null);
      setTimeout(() => this.selectedAccidenteId.set(id), 100);
    }
  }

  onAbrirActualizarEstado(): void {
    this.mostrarActualizarEstado.set(true);
  }

  onCerrarActualizarEstado(): void {
    this.mostrarActualizarEstado.set(false);
    this.mapaService.refrescar();
    const id = this.selectedAccidenteId();
    if (id) {
      this.selectedAccidenteId.set(null);
      setTimeout(() => this.selectedAccidenteId.set(id), 100);
    }
  }

  toggleFiltros(): void {
    this.filtrosAbiertos.update(v => !v);
  }

  // --- Filtros de severidad y estado ---
  onSeveridadChange(value: string): void {
    const sev = value ? Number(value) : undefined;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      severidad: sev
    });
  }

  onEstadoChange(value: string): void {
    const est = value || undefined;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      estado: est
    });
  }

  onFechaInicioChange(value: string): void {
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      fecha_inicio: value || undefined
    });
  }

  onFechaFinChange(value: string): void {
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      fecha_fin: value || undefined
    });
  }

  // --- Carga de catÃ¡logos de ubicaciÃ³n ---
  cargarPaises(): void {
    this.accidenteService.getPaises().subscribe({
      next: (list) => this.paisesList.set(list),
    });
  }

  onPaisChange(value: string): void {
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      idpais: value || undefined,
      idestado: undefined,
      idcondado: undefined,
      idciudad: undefined,
      idcalle: undefined,
    });
    this.estadosList.set([]);
    this.condadosList.set([]);
    this.ciudadesList.set([]);
    this.callesList.set([]);
    if (value) {
      this.accidenteService.getEstados(value).subscribe({
        next: (list) => this.estadosList.set(list),
      });
    }
  }

  onIdEstadoChange(value: string): void {
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      idestado: value || undefined,
      idcondado: undefined,
      idciudad: undefined,
      idcalle: undefined,
    });
    this.condadosList.set([]);
    this.ciudadesList.set([]);
    this.callesList.set([]);
    if (value) {
      this.accidenteService.getCondados(value).subscribe({
        next: (list) => this.condadosList.set(list),
      });
    }
  }

  onCondadoChange(value: string): void {
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      idcondado: value || undefined,
      idciudad: undefined,
      idcalle: undefined,
    });
    this.ciudadesList.set([]);
    this.callesList.set([]);
    if (value) {
      this.accidenteService.getCiudades(value).subscribe({
        next: (list) => this.ciudadesList.set(list),
      });
    }
  }

  onCiudadChange(value: string): void {
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      idciudad: value || undefined,
      idcalle: undefined,
    });
    this.callesList.set([]);
    if (value) {
      this.accidenteService.getCalles(value).subscribe({
        next: (list) => this.callesList.set(list),
      });
    }
  }

  onCalleChange(value: string): void {
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      idcalle: value || undefined,
    });
  }

  clearFiltros(): void {
    this.mapaService.setFiltros({});
    this.paisesList.set([]);
    this.estadosList.set([]);
    this.condadosList.set([]);
    this.ciudadesList.set([]);
    this.callesList.set([]);
  }

  private formatDate(date: Date): string {
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }
}

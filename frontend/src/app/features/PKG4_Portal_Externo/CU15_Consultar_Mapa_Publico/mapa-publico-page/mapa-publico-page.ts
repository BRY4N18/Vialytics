import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MapaComponent } from '../../../PKG1_Gestion_Accidentes/CU02_Visualizar_Mapa/mapa/mapa';
import { MapaService } from '../../../../core/services/mapa.service';
import { AccidenteService } from '../../../../core/services/accidente.service';
import { Pais, Estado, Condado, Ciudad } from '../../../../core/models/accidente.model';

@Component({
  selector: 'app-mapa-publico-page',
  standalone: true,
  imports: [CommonModule, MapaComponent],
  templateUrl: './mapa-publico-page.html'
})
export class MapaPublicoPageComponent implements OnInit {
  private readonly mapaService = inject(MapaService);
  private readonly accidenteService = inject(AccidenteService);

  readonly filtrosAbiertos = signal(true);

  readonly paisesList = signal<Pais[]>([]);
  readonly estadosList = signal<Estado[]>([]);
  readonly condadosList = signal<Condado[]>([]);
  readonly ciudadesList = signal<Ciudad[]>([]);

  readonly severidades = [
    { value: 1, label: 'Leve', color: '#10B981' },
    { value: 2, label: 'Moderado', color: '#F59E0B' },
    { value: 3, label: 'Grave', color: '#EF4444' },
    { value: 4, label: 'Fatal', color: '#7C3AED' },
  ];

  ngOnInit(): void {
    this.cargarPaises();
  }

  toggleFiltros(): void {
    this.filtrosAbiertos.update(v => !v);
  }

  onSeveridadChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      severidad: value ? Number(value) : undefined
    });
  }

  onFechaInicioChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      fecha_inicio: value || undefined
    });
  }

  onFechaFinChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      fecha_fin: value || undefined
    });
  }

  cargarPaises(): void {
    this.accidenteService.getPaises().subscribe({
      next: (list) => this.paisesList.set(list),
    });
  }

  onPaisChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      idpais: value || undefined,
      idestado: undefined,
      idcondado: undefined,
      idciudad: undefined,
    });
    this.estadosList.set([]);
    this.condadosList.set([]);
    this.ciudadesList.set([]);
    if (value) {
      this.accidenteService.getEstados(value).subscribe({
        next: (list) => this.estadosList.set(list),
      });
    }
  }

  onIdEstadoChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      idestado: value || undefined,
      idcondado: undefined,
      idciudad: undefined,
    });
    this.condadosList.set([]);
    this.ciudadesList.set([]);
    if (value) {
      this.accidenteService.getCondados(value).subscribe({
        next: (list) => this.condadosList.set(list),
      });
    }
  }

  onCondadoChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      idcondado: value || undefined,
      idciudad: undefined,
    });
    this.ciudadesList.set([]);
    if (value) {
      this.accidenteService.getCiudades(value).subscribe({
        next: (list) => this.ciudadesList.set(list),
      });
    }
  }

  onCiudadChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    this.mapaService.setFiltros({
      ...this.mapaService.filtros(),
      idciudad: value || undefined,
    });
  }

  clearFiltros(): void {
    this.mapaService.setFiltros({});
    this.paisesList.set([]);
    this.estadosList.set([]);
    this.condadosList.set([]);
    this.ciudadesList.set([]);
  }
}

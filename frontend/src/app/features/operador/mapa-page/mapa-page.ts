import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { MapaComponent } from '../mapa/mapa';
import { PanelDetalleComponent } from '../panel-detalle/panel-detalle';
import { DespachoComponent } from '../despacho/despacho';
import { ActualizarEstadoComponent } from '../actualizar-estado/actualizar-estado';
import { MapaService } from '../../../core/services/mapa.service';
import { AccidenteMapa } from '../../../core/models/accidente.model';

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
  private readonly route = inject(ActivatedRoute);

  readonly selectedAccidenteId = signal<string | null>(null);
  readonly selectedAccidenteEstado = signal<string | null>(null);

  readonly mostrarDespacho = signal(false);
  readonly mostrarActualizarEstado = signal(false);

  private querySub?: Subscription;

  ngOnInit(): void {
    this.querySub = this.route.queryParams.subscribe(params => {
      const selectedId = params['selected'];
      if (selectedId) {
        this.selectedAccidenteId.set(selectedId);
      }
    });
  }

  ngOnDestroy(): void {
    this.querySub?.unsubscribe();
  }

  onAccidenteSeleccionado(accidente: AccidenteMapa): void {
    console.log('MapaPage - Accidente seleccionado:', accidente);
    this.selectedAccidenteId.set(accidente.idaccidente);
    this.selectedAccidenteEstado.set(accidente.estado_actual);
  }

  onUbicacionSeleccionada(loc: { lat: number; lng: number }): void {
    console.log('MapaPage - Ubicación seleccionada:', loc);
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
    this.mapaService.refrescar(); // Recargar mapa
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
    this.mapaService.refrescar(); // Recargar mapa
    const id = this.selectedAccidenteId();
    if (id) {
      this.selectedAccidenteId.set(null);
      setTimeout(() => this.selectedAccidenteId.set(id), 100);
    }
  }
}

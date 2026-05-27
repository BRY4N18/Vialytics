import { Injectable, signal } from '@angular/core';

export interface MapaFiltros {
  severidad?: number;
  estado?: string;
  solo_activos?: boolean;
  fecha_inicio?: string;
  fecha_fin?: string;
}

@Injectable({ providedIn: 'root' })
export class MapaService {
  readonly filtros = signal<MapaFiltros>({});
  readonly modoRegistro = signal(false);
  readonly refrescarTrigger = signal(0);

  setFiltros(filtros: MapaFiltros): void {
    this.filtros.set(filtros);
  }

  toggleModoRegistro(): void {
    this.modoRegistro.update((v) => !v);
  }

  activarModoRegistro(): void {
    this.modoRegistro.set(true);
  }

  desactivarModoRegistro(): void {
    this.modoRegistro.set(false);
  }

  refrescar(): void {
    this.refrescarTrigger.update((v) => v + 1);
  }
}

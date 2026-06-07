import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { forkJoin } from 'rxjs';
import { RouterModule } from '@angular/router';
import { DespachoService } from '../../../../core/services/despacho.service';
import { UnidadEmergenciaService } from '../../../../core/services/unidad-emergencia.service';
import { AuthService } from '../../../../core/services/auth.service';
import { ToastService } from '../../../../core/services/toast.service';
import { DespachoPendiente, NotificacionDespacho } from '../../../../core/models/despacho-pendiente.model';
import { UnidadEmergencia } from '../../../../core/models/unidad-emergencia.model';

interface TipoVehiculo {
  clave: string;
  label: string;
  color: string;
}

@Component({
  selector: 'app-recibir-despacho',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './recibir-despacho.html'
})
export class RecibirDespachoComponent implements OnInit {
  private readonly despachoService = inject(DespachoService);
  private readonly unidadEmergenciaService = inject(UnidadEmergenciaService);
  private readonly toastService = inject(ToastService);
  readonly authService = inject(AuthService);

  readonly TIPOS: TipoVehiculo[] = [
    { clave: 'AMBULANCIA', label: 'Ambulancia', color: '#F59E0B' },
    { clave: 'POLICIA', label: 'Policía', color: '#06B6D4' },
    { clave: 'BOMBEROS', label: 'Bomberos', color: '#EF4444' },
    { clave: 'GRUA', label: 'Grúa', color: '#6B7280' },
  ];

  readonly unidades = signal<UnidadEmergencia[]>([]);
  readonly notificaciones = signal<NotificacionDespacho[]>([]);
  readonly despachos = signal<DespachoPendiente[]>([]);
  readonly unidadFiltroDespachos = signal<number | null>(null);
  readonly cargandoNotificaciones = signal(false);
  readonly cargandoDespachos = signal(false);
  readonly llegandoId = signal<number | null>(null);
  readonly error = signal<string | null>(null);

  // Modal state
  readonly modalAbierto = signal(false);
  readonly notificacionSeleccionada = signal<NotificacionDespacho | null>(null);
  readonly tiposFiltrados = signal<TipoVehiculo[]>([]);
  readonly tiposExpandidos = signal<Set<string>>(new Set());
  readonly unidadesPorTipo = signal<Record<string, UnidadEmergencia[]>>({});
  readonly cargandoTipos = signal<Set<string>>(new Set());
  readonly unidadIdsSeleccionados = signal<Set<number>>(new Set());
  readonly aceptandoNotificacion = signal(false);
  readonly errorModal = signal<string | null>(null);

  readonly severidadLabel = (nivel?: number): string => {
    const labels: Record<number, string> = { 1: 'Leve', 2: 'Moderado', 3: 'Grave', 4: 'Fatal' };
    return nivel ? (labels[nivel] || 'Desconocida') : 'Desconocida';
  };

  readonly severidadColor = (nivel?: number): string => {
    const colors: Record<number, string> = { 1: '#10B981', 2: '#F59E0B', 3: '#EF4444', 4: '#7C3AED' };
    return nivel ? (colors[nivel] || '#6B7280') : '#6B7280';
  };

  ngOnInit(): void {
    this.cargarUnidades();
    this.cargarNotificaciones();
  }

  private getTipoInfo(clave: string): TipoVehiculo {
    return this.TIPOS.find(t => t.clave === clave) || { clave, label: clave, color: '#6B7280' };
  }

  cargarUnidades(): void {
    this.unidadEmergenciaService.getUnidades().subscribe({
      next: (data) => this.unidades.set(data)
    });
  }

  cargarNotificaciones(): void {
    this.cargandoNotificaciones.set(true);
    this.despachoService.getNotificaciones().subscribe({
      next: (data) => {
        this.notificaciones.set(data);
        this.cargandoNotificaciones.set(false);
      },
      error: () => this.cargandoNotificaciones.set(false)
    });
  }

  onFiltroDespachoChange(value: string): void {
    const id = Number(value);
    this.unidadFiltroDespachos.set(id || null);
    if (id) {
      this.cargarDespachos();
    } else {
      this.despachos.set([]);
    }
  }

  cargarDespachos(): void {
    const id = this.unidadFiltroDespachos();
    if (!id) return;
    this.cargandoDespachos.set(true);
    this.despachoService.getDespachosPorUnidad(id).subscribe({
      next: (data) => {
        this.despachos.set(data);
        this.cargandoDespachos.set(false);
      },
      error: () => this.cargandoDespachos.set(false)
    });
  }

  abrirModal(n: NotificacionDespacho): void {
    const tipos = n.tipos_necesarios && n.tipos_necesarios.length > 0
      ? this.TIPOS.filter(t => n.tipos_necesarios.includes(t.clave))
      : [...this.TIPOS];

    this.notificacionSeleccionada.set(n);
    this.tiposFiltrados.set(tipos);
    this.unidadIdsSeleccionados.set(new Set());
    this.unidadesPorTipo.set({});
    this.tiposExpandidos.set(new Set());
    this.cargandoTipos.set(new Set());
    this.errorModal.set(null);
    this.modalAbierto.set(true);

    if (tipos.length > 0) {
      this.tiposExpandidos.set(new Set([tipos[0].clave]));
    }

    for (const t of tipos) {
      this.cargarUnidadesPorTipo(t.clave);
    }
  }

  private cargarUnidadesPorTipo(clave: string): void {
    const loading = new Set(this.cargandoTipos());
    loading.add(clave);
    this.cargandoTipos.set(loading);

    this.unidadEmergenciaService.getUnidades({ tipo: clave, estado: 'En base', activo: 'true' }).subscribe({
      next: (data) => {
        const map = { ...this.unidadesPorTipo() };
        map[clave] = data;
        this.unidadesPorTipo.set(map);
        const loading2 = new Set(this.cargandoTipos());
        loading2.delete(clave);
        this.cargandoTipos.set(loading2);
      },
      error: () => {
        const map = { ...this.unidadesPorTipo() };
        map[clave] = [];
        this.unidadesPorTipo.set(map);
        const loading2 = new Set(this.cargandoTipos());
        loading2.delete(clave);
        this.cargandoTipos.set(loading2);
      }
    });
  }

  toggleTipoExpandido(clave: string): void {
    const s = new Set(this.tiposExpandidos());
    if (s.has(clave)) {
      s.delete(clave);
    } else {
      s.add(clave);
    }
    this.tiposExpandidos.set(s);
  }

  toggleUnidad(id: number): void {
    const s = new Set(this.unidadIdsSeleccionados());
    if (s.has(id)) {
      s.delete(id);
    } else {
      s.add(id);
    }
    this.unidadIdsSeleccionados.set(s);
  }

  cerrarModal(): void {
    this.modalAbierto.set(false);
    this.notificacionSeleccionada.set(null);
    this.tiposFiltrados.set([]);
    this.tiposExpandidos.set(new Set());
    this.unidadesPorTipo.set({});
    this.cargandoTipos.set(new Set());
    this.unidadIdsSeleccionados.set(new Set());
    this.aceptandoNotificacion.set(false);
    this.errorModal.set(null);
  }

  confirmarAceptar(): void {
    const notif = this.notificacionSeleccionada();
    const unidadIds = Array.from(this.unidadIdsSeleccionados());
    if (!notif || unidadIds.length === 0) return;

    this.aceptandoNotificacion.set(true);
    this.errorModal.set(null);

    this.despachoService.aceptarNotificacion(notif.idnotificaciondespacho, unidadIds).subscribe({
      next: () => {
        const estadoCalls = unidadIds.map(uid =>
          this.unidadEmergenciaService.actualizarEstadoUnidad(uid, 'En camino')
        );
        forkJoin(estadoCalls).subscribe({
          next: () => {
            this.toastService.show(`Despacho aceptado y ${unidadIds.length} unidad(es) en camino`);
          },
          error: () => {
            this.toastService.show('Despacho aceptado, pero algunas unidades no pudieron actualizar su estado');
          }
        });
        this.aceptandoNotificacion.set(false);
        this.cerrarModal();
        this.cargarNotificaciones();
        this.cargarUnidades();
        if (this.unidadFiltroDespachos()) {
          this.cargarDespachos();
        }
      },
      error: (err) => {
        this.aceptandoNotificacion.set(false);
        this.errorModal.set(err.message || 'Error al aceptar notificación');
      }
    });
  }

  marcarLlegada(despachoId: number): void {
    this.llegandoId.set(despachoId);
    this.despachoService.marcarLlegada(despachoId).subscribe({
      next: () => {
        this.toastService.show('Llegada registrada exitosamente');
        this.llegandoId.set(null);
        this.cargarDespachos();
      },
      error: (err) => {
        this.toastService.show(err.message || 'Error al marcar llegada');
        this.llegandoId.set(null);
      }
    });
  }

  formatoFecha(iso: string | null): string {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleString('es-EC');
    } catch {
      return iso;
    }
  }
}

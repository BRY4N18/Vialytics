import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DespachoService } from '../../../../core/services/despacho.service';
import { UnidadEmergenciaService } from '../../../../core/services/unidad-emergencia.service';
import { AuthService } from '../../../../core/services/auth.service';
import { ToastService } from '../../../../core/services/toast.service';
import { DespachoPendiente, NotificacionDespacho } from '../../../../core/models/despacho-pendiente.model';
import { UnidadEmergencia } from '../../../../core/models/unidad-emergencia.model';

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

  readonly unidades = signal<UnidadEmergencia[]>([]);
  readonly unidadSeleccionada = signal<number | null>(null);
  readonly notificaciones = signal<NotificacionDespacho[]>([]);
  readonly despachos = signal<DespachoPendiente[]>([]);
  readonly cargandoUnidades = signal(false);
  readonly cargandoNotificaciones = signal(false);
  readonly cargandoDespachos = signal(false);
  readonly aceptandoId = signal<number | null>(null);
  readonly llegandoId = signal<number | null>(null);
  readonly error = signal<string | null>(null);

  readonly unidadActual = signal<UnidadEmergencia | null>(null);

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

  cargarUnidades(): void {
    this.cargandoUnidades.set(true);
    this.unidadEmergenciaService.getUnidades().subscribe({
      next: (data) => {
        this.unidades.set(data);
        this.cargandoUnidades.set(false);
        if (data.length === 1) {
          this.seleccionarUnidad(data[0].idunidademergencia);
        }
      },
      error: () => this.cargandoUnidades.set(false)
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

  onUnidadChange(value: string): void {
    const id = Number(value);
    if (id) {
      this.seleccionarUnidad(id);
    }
  }

  seleccionarUnidad(unidadId: number): void {
    this.unidadSeleccionada.set(unidadId);
    this.unidadActual.set(this.unidades().find(u => u.idunidademergencia === unidadId) || null);
    this.cargarDespachos();
  }

  cargarDespachos(): void {
    const id = this.unidadSeleccionada();
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

  aceptarNotificacion(notificacionId: number): void {
    const unidadId = this.unidadSeleccionada();
    if (!unidadId) {
      this.toastService.show('Seleccione una unidad primero');
      return;
    }
    this.aceptandoId.set(notificacionId);
    this.despachoService.aceptarNotificacion(notificacionId, unidadId).subscribe({
      next: (res) => {
        this.toastService.show(res.mensaje || 'Despacho aceptado exitosamente');
        this.aceptandoId.set(null);
        this.cargarNotificaciones();
        this.cargarDespachos();
      },
      error: (err) => {
        this.toastService.show(err.message || 'Error al aceptar notificación');
        this.aceptandoId.set(null);
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

import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DespachoService } from '../../../../core/services/despacho.service';
import { UnidadEmergenciaService } from '../../../../core/services/unidad-emergencia.service';
import { AuthService } from '../../../../core/services/auth.service';
import { ToastService } from '../../../../core/services/toast.service';
import { DespachoPendiente } from '../../../../core/models/despacho-pendiente.model';
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
  readonly despachos = signal<DespachoPendiente[]>([]);
  readonly cargandoUnidades = signal(false);
  readonly cargandoDespachos = signal(false);
  readonly confirmandoId = signal<number | null>(null);
  readonly llegandoId = signal<number | null>(null);
  readonly error = signal<string | null>(null);
  readonly soloPendientes = signal(true);

  readonly unidadActual = computed(() => {
    const id = this.unidadSeleccionada();
    if (!id) return null;
    return this.unidades().find(u => u.idunidademergencia === id) || null;
  });

  readonly despachosPendientes = computed(() =>
    this.despachos().filter(d => !d.fechahoraconfirmacion)
  );

  readonly despachosConfirmados = computed(() =>
    this.despachos().filter(d => d.fechahoraconfirmacion && !d.fechahorallegada)
  );

  readonly despachosCompletados = computed(() =>
    this.despachos().filter(d => d.fechahoraconfirmacion && d.fechahorallegada)
  );

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
  }

  cargarUnidades(): void {
    this.cargandoUnidades.set(true);
    this.error.set(null);

    this.unidadEmergenciaService.getUnidades().subscribe({
      next: (data) => {
        this.unidades.set(data);
        this.cargandoUnidades.set(false);
        if (data.length === 1) {
          this.seleccionarUnidad(data[0].idunidademergencia);
        }
      },
      error: (err) => {
        this.error.set(err.message || 'Error al cargar unidades');
        this.cargandoUnidades.set(false);
      }
    });
  }

  onUnidadChange(value: string): void {
    const id = Number(value);
    if (id) {
      this.unidadSeleccionada.set(id);
      this.cargarDespachos();
    }
  }

  seleccionarUnidad(unidadId: number): void {
    this.unidadSeleccionada.set(unidadId);
    this.cargarDespachos();
  }

  cargarDespachos(): void {
    const id = this.unidadSeleccionada();
    if (!id) return;

    this.cargandoDespachos.set(true);
    this.error.set(null);

    this.despachoService.getDespachosPorUnidad(id, this.soloPendientes()).subscribe({
      next: (data) => {
        this.despachos.set(data);
        this.cargandoDespachos.set(false);
      },
      error: (err) => {
        this.error.set(err.message || 'Error al cargar despachos');
        this.cargandoDespachos.set(false);
      }
    });
  }

  confirmar(despachoId: number): void {
    this.confirmandoId.set(despachoId);
    this.despachoService.confirmarDespacho(despachoId).subscribe({
      next: () => {
        this.toastService.show('Despacho confirmado exitosamente');
        this.confirmandoId.set(null);
        this.cargarDespachos();
      },
      error: (err) => {
        this.toastService.show(err.message || 'Error al confirmar despacho');
        this.confirmandoId.set(null);
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

  togglePendientes(): void {
    this.soloPendientes.update(v => !v);
    this.cargarDespachos();
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

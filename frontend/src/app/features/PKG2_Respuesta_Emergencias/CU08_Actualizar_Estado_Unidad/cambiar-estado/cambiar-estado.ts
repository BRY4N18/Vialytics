import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { UnidadEmergenciaService } from '../../../../core/services/unidad-emergencia.service';
import { ToastService } from '../../../../core/services/toast.service';
import { UnidadEmergencia } from '../../../../core/models/unidad-emergencia.model';

@Component({
  selector: 'app-cambiar-estado',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './cambiar-estado.html'
})
export class CambiarEstadoComponent implements OnInit {
  private readonly unidadEmergenciaService = inject(UnidadEmergenciaService);
  private readonly toastService = inject(ToastService);

  readonly unidades = signal<UnidadEmergencia[]>([]);
  readonly unidadSeleccionada = signal<UnidadEmergencia | null>(null);
  readonly cargando = signal(false);
  readonly actualizando = signal(false);
  readonly error = signal<string | null>(null);

  readonly estadosDisponibles = ['En base', 'En camino', 'En escena', 'En traslado', 'Regreso', 'Disponible'];

  ngOnInit(): void {
    this.cargarUnidades();
  }

  cargarUnidades(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.unidadEmergenciaService.getUnidades({ activo: 'true' }).subscribe({
      next: (data) => {
        this.unidades.set(data);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err.message || 'Error al cargar unidades');
        this.cargando.set(false);
      }
    });
  }

  seleccionarUnidad(unidad: UnidadEmergencia): void {
    this.unidadSeleccionada.set(unidad);
    this.error.set(null);
  }

  cambiarEstado(nuevoEstado: string): void {
    const unidad = this.unidadSeleccionada();
    if (!unidad) return;

    this.actualizando.set(true);
    this.error.set(null);

    this.unidadEmergenciaService.actualizarEstadoUnidad(unidad.idunidademergencia, nuevoEstado).subscribe({
      next: () => {
        this.toastService.show(`Estado actualizado a "${nuevoEstado}"`);
        this.actualizando.set(false);
        unidad.estadounidad = nuevoEstado as any;
        this.unidadSeleccionada.set({ ...unidad });
        this.cargarUnidades();
      },
      error: (err) => {
        this.error.set(err.message || 'Error al actualizar estado');
        this.actualizando.set(false);
      }
    });
  }
}
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { UnidadEmergenciaService } from '../../../../core/services/unidad-emergencia.service';
import { ToastService } from '../../../../core/services/toast.service';
import { UnidadEmergencia, TipoUnidad } from '../../../../core/models/unidad-emergencia.model';

@Component({
  selector: 'app-gestionar-unidades',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './gestionar-unidades.html'
})
export class GestionarUnidadesComponent implements OnInit {
  private readonly unidadEmergenciaService = inject(UnidadEmergenciaService);
  private readonly toastService = inject(ToastService);

  readonly unidades = signal<UnidadEmergencia[]>([]);
  readonly cargando = signal(false);

  readonly tiposUnidad: TipoUnidad[] = ['AMBULANCIA', 'BOMBEROS', 'TRANSITO', 'GRUA'];

  readonly modalCrearAbierto = signal(false);
  readonly crearNombre = signal('');
  readonly crearTipo = signal('');
  readonly creando = signal(false);
  readonly errorCrear = signal<string | null>(null);

  readonly modalEditarAbierto = signal(false);
  readonly editarId = signal<number | null>(null);
  readonly editarNombre = signal('');
  readonly editarTipo = signal('');
  readonly editando = signal(false);
  readonly errorEditar = signal<string | null>(null);

  readonly togglingId = signal<number | null>(null);

  ngOnInit(): void {
    this.cargarUnidades();
  }

  cargarUnidades(): void {
    this.cargando.set(true);
    this.unidadEmergenciaService.getUnidades().subscribe({
      next: (data) => {
        this.unidades.set(data);
        this.cargando.set(false);
      },
      error: () => this.cargando.set(false)
    });
  }

  abrirModalCrear(): void {
    this.modalCrearAbierto.set(true);
    this.crearNombre.set('');
    this.crearTipo.set('');
    this.errorCrear.set(null);
  }

  cerrarModalCrear(): void {
    this.modalCrearAbierto.set(false);
  }

  crearUnidad(): void {
    const nombre = this.crearNombre().trim();
    const tipo = this.crearTipo();
    if (!nombre || !tipo) return;

    this.creando.set(true);
    this.errorCrear.set(null);

    this.unidadEmergenciaService.crearUnidad(nombre, tipo).subscribe({
      next: () => {
        this.toastService.show('Unidad creada exitosamente');
        this.creando.set(false);
        this.cerrarModalCrear();
        this.cargarUnidades();
      },
      error: (err) => {
        this.errorCrear.set(err.message || 'Error al crear unidad');
        this.creando.set(false);
      }
    });
  }

  abrirModalEditar(unidad: UnidadEmergencia): void {
    this.modalEditarAbierto.set(true);
    this.editarId.set(unidad.idunidademergencia);
    this.editarNombre.set(unidad.unidademergencia);
    this.editarTipo.set(unidad.tipounidademergencia);
    this.errorEditar.set(null);
  }

  cerrarModalEditar(): void {
    this.modalEditarAbierto.set(false);
  }

  guardarEditar(): void {
    const id = this.editarId();
    const nombre = this.editarNombre().trim();
    const tipo = this.editarTipo();
    if (!id || !nombre || !tipo) return;

    this.editando.set(true);
    this.errorEditar.set(null);

    this.unidadEmergenciaService.actualizarUnidad(id, nombre, tipo).subscribe({
      next: () => {
        this.toastService.show('Unidad actualizada exitosamente');
        this.editando.set(false);
        this.cerrarModalEditar();
        this.cargarUnidades();
      },
      error: (err) => {
        this.errorEditar.set(err.message || 'Error al actualizar unidad');
        this.editando.set(false);
      }
    });
  }

  toggleActivo(unidad: UnidadEmergencia): void {
    this.togglingId.set(unidad.idunidademergencia);
    this.unidadEmergenciaService.toggleActivo(unidad.idunidademergencia, !unidad.activo).subscribe({
      next: () => {
        this.toastService.show(unidad.activo ? 'Unidad desactivada' : 'Unidad activada');
        this.togglingId.set(null);
        this.cargarUnidades();
      },
      error: (err) => {
        this.toastService.show(err.message || 'Error al cambiar estado');
        this.togglingId.set(null);
      }
    });
  }
}

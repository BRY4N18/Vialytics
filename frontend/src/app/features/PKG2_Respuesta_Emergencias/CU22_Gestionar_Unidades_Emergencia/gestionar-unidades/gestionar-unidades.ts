import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { UnidadEmergenciaService } from '../../../../core/services/unidad-emergencia.service';
import { ToastService } from '../../../../core/services/toast.service';
import { UnidadEmergencia, TipoUnidadCatalogoItem } from '../../../../core/models/unidad-emergencia.model';

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
  readonly tiposCatalogo = signal<TipoUnidadCatalogoItem[]>([]);
  readonly cargando = signal(false);

  readonly estadosUnidad: string[] = ['En base', 'En camino', 'En escena', 'En traslado', 'Regreso', 'Disponible'];

  readonly filtroTipo = signal<string>('');
  readonly filtroEstado = signal<string>('');
  readonly filtroActivo = signal<string>('');
  readonly filtroSearch = signal<string>('');

  readonly modalCrearAbierto = signal(false);
  readonly crearNombre = signal('');
  readonly crearTipoId = signal<number | null>(null);
  readonly creando = signal(false);
  readonly errorCrear = signal<string | null>(null);

  readonly modalEditarAbierto = signal(false);
  readonly editarId = signal<number | null>(null);
  readonly editarNombre = signal('');
  readonly editarTipoId = signal<number | null>(null);
  readonly editando = signal(false);
  readonly errorEditar = signal<string | null>(null);

  readonly togglingId = signal<number | null>(null);

  private tipoStrAId(tipo: string): number | null {
    const t = this.tiposCatalogo().find(tc => tc.tipounidad === tipo);
    return t ? t.idtipounidad : null;
  }

  ngOnInit(): void {
    this.unidadEmergenciaService.getTiposUnidad().subscribe({
      next: (data) => this.tiposCatalogo.set(data)
    });
    this.cargarUnidades();
  }

  cargarUnidades(): void {
    this.cargando.set(true);
    const filtros: any = {};
    if (this.filtroTipo()) filtros.tipo = this.filtroTipo();
    if (this.filtroEstado()) filtros.estado = this.filtroEstado();
    if (this.filtroActivo()) filtros.activo = this.filtroActivo();
    if (this.filtroSearch()) filtros.search = this.filtroSearch();
    this.unidadEmergenciaService.getUnidades(filtros).subscribe({
      next: (data) => {
        this.unidades.set(data);
        this.cargando.set(false);
      },
      error: () => this.cargando.set(false)
    });
  }

  onFiltroChange(): void {
    this.cargarUnidades();
  }

  abrirModalCrear(): void {
    this.modalCrearAbierto.set(true);
    this.crearNombre.set('');
    this.crearTipoId.set(null);
    this.errorCrear.set(null);
  }

  cerrarModalCrear(): void {
    this.modalCrearAbierto.set(false);
  }

  crearUnidad(): void {
    const nombre = this.crearNombre().trim();
    const tipoId = this.crearTipoId();
    if (!nombre || tipoId === null) return;

    this.creando.set(true);
    this.errorCrear.set(null);

    this.unidadEmergenciaService.crearUnidad(nombre, tipoId).subscribe({
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
    this.editarTipoId.set(this.tipoStrAId(unidad.tipounidademergencia));
    this.errorEditar.set(null);
  }

  cerrarModalEditar(): void {
    this.modalEditarAbierto.set(false);
  }

  guardarEditar(): void {
    const id = this.editarId();
    const nombre = this.editarNombre().trim();
    const tipoId = this.editarTipoId();
    if (!id || !nombre || tipoId === null) return;

    this.editando.set(true);
    this.errorEditar.set(null);

    this.unidadEmergenciaService.actualizarUnidad(id, nombre, tipoId).subscribe({
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

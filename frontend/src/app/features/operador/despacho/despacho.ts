import { Component, OnInit, input, output, signal, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UnidadEmergenciaService } from '../../../core/services/unidad-emergencia.service';
import { AccidenteService } from '../../../core/services/accidente.service';
import { UnidadEmergencia } from '../../../core/models/unidad-emergencia.model';

@Component({
  selector: 'app-despacho',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './despacho.html'
})
export class DespachoComponent implements OnInit {
  accidenteId = input.required<string>();

  cerrar = output<void>();

  private readonly unidadEmergenciaService = inject(UnidadEmergenciaService);
  private readonly accidenteService = inject(AccidenteService);

  readonly unidades = signal<UnidadEmergencia[]>([]);
  readonly selectedUnidadesIds = signal<Set<number>>(new Set());
  readonly filtroTipo = signal<string>('TODAS');

  readonly cargando = signal(false);
  readonly guardando = signal(false);
  readonly error = signal<string | null>(null);

  // Computed state for filtered list of responding units
  readonly unidadesFiltradas = computed(() => {
    const list = this.unidades();
    const type = this.filtroTipo();
    if (type === 'TODAS') {
      return list;
    }
    return list.filter(u => u.tipounidademergencia === type);
  });

  ngOnInit(): void {
    this.cargarUnidades();
  }

  cargarUnidades(): void {
    this.cargando.set(true);
    this.error.set(null);

    this.unidadEmergenciaService.getUnidades().subscribe({
      next: (data) => {
        this.unidades.set(data);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err.message || 'Error al obtener la lista de unidades viales.');
        this.cargando.set(false);
      }
    });
  }

  isDisponible(unidad: UnidadEmergencia): boolean {
    return unidad.estadounidad === 'EN_BASE' || unidad.estadounidad === 'DISPONIBLE';
  }

  toggleSeleccion(unidadId: number): void {
    const currentSet = new Set(this.selectedUnidadesIds());
    if (currentSet.has(unidadId)) {
      currentSet.delete(unidadId);
    } else {
      currentSet.add(unidadId);
    }
    this.selectedUnidadesIds.set(currentSet);
  }

  setFiltroTipo(tipo: string): void {
    this.filtroTipo.set(tipo);
  }

  submit(): void {
    const ids = Array.from(this.selectedUnidadesIds());
    if (ids.length === 0) return;

    this.guardando.set(true);
    this.error.set(null);

    this.accidenteService.despacharUnidades(this.accidenteId(), { unidades_ids: ids }).subscribe({
      next: () => {
        this.guardando.set(false);
        this.cerrar.emit(); // Success, close dispatcher modal
      },
      error: (err) => {
        this.guardando.set(false);
        this.error.set(err.message || 'Error al realizar el despacho de unidades.');
      }
    });
  }

  onCancelar(): void {
    this.cerrar.emit();
  }
}

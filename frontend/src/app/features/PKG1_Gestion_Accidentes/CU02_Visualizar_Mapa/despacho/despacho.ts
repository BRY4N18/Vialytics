import { Component, input, output, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AccidenteService } from '../../../../core/services/accidente.service';

interface TipoVehiculo {
  clave: string;
  label: string;
  icon: string;
  color: string;
}

@Component({
  selector: 'app-despacho',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './despacho.html'
})
export class DespachoComponent {
  accidenteId = input.required<string>();

  cerrar = output<void>();

  private readonly accidenteService = inject(AccidenteService);

  readonly TIPOS: TipoVehiculo[] = [
    { clave: 'AMBULANCIA', label: 'Ambulancia', icon: 'plus', color: '#F59E0B' },
    { clave: 'POLICIA', label: 'Policía', icon: 'shield', color: '#06B6D4' },
    { clave: 'BOMBEROS', label: 'Bomberos', icon: 'flame', color: '#EF4444' },
    { clave: 'GRUA', label: 'Grúa', icon: 'truck', color: '#6B7280' },
  ];

  readonly tiposSeleccionados = signal<Set<string>>(new Set());
  readonly guardando = signal(false);
  readonly error = signal<string | null>(null);

  toggleTipo(clave: string): void {
    const s = new Set(this.tiposSeleccionados());
    if (s.has(clave)) {
      s.delete(clave);
    } else {
      s.add(clave);
    }
    this.tiposSeleccionados.set(s);
  }

  submit(): void {
    const tipos = Array.from(this.tiposSeleccionados());
    if (tipos.length === 0) return;

    this.guardando.set(true);
    this.error.set(null);

    this.accidenteService.despacharUnidades(this.accidenteId(), {
      tipos
    }).subscribe({
      next: () => {
        this.guardando.set(false);
        this.cerrar.emit();
      },
      error: (err) => {
        this.guardando.set(false);
        this.error.set(err.message || 'Error al crear notificación de despacho.');
      }
    });
  }

  onCancelar(): void {
    this.cerrar.emit();
  }
}

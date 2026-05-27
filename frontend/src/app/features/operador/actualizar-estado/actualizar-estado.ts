import { Component, OnInit, input, output, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AccidenteService } from '../../../core/services/accidente.service';
import { TipoEstadoIncidente, ActualizarEstadoPayload } from '../../../core/models/accidente.model';

@Component({
  selector: 'app-actualizar-estado',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './actualizar-estado.html',
  styleUrl: './actualizar-estado.css'
})
export class ActualizarEstadoComponent implements OnInit {
  accidenteId = input.required<string>();
  estadoActual = input.required<string>();

  cerrar = output<void>();

  private readonly fb = inject(FormBuilder);
  private readonly accidenteService = inject(AccidenteService);

  form!: FormGroup;
  readonly estados = signal<TipoEstadoIncidente[]>([]);
  readonly cargando = signal(false);
  readonly guardando = signal(false);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.buildForm();
    this.cargarEstados();
  }

  private buildForm(): void {
    this.form = this.fb.group({
      idtipoestadoincidente_id: ['', Validators.required],
      nota: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(300)]]
    });
  }

  private cargarEstados(): void {
    this.cargando.set(true);
    this.accidenteService.getTiposEstado().subscribe({
      next: (data) => {
        // Exclude the current state from options
        this.estados.set(data.filter(e => e.tipoestadoincidente !== this.estadoActual()));
        this.cargando.set(false);
      },
      error: () => {
        this.error.set('Error al cargar la lista de estados');
        this.cargando.set(false);
      }
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.guardando.set(true);
    this.error.set(null);

    const payload: ActualizarEstadoPayload = {
      idtipoestadoincidente_id: Number(this.form.value.idtipoestadoincidente_id),
      nota: this.form.value.nota
    };

    this.accidenteService.actualizarEstado(this.accidenteId(), payload).subscribe({
      next: () => {
        this.guardando.set(false);
        this.cerrar.emit(); // Success, close modal
      },
      error: (err) => {
        this.guardando.set(false);
        this.error.set(err.message || 'Error al actualizar el estado del incidente');
      }
    });
  }

  onCancelar(): void {
    this.cerrar.emit();
  }

  isInvalid(field: string): boolean {
    const ctrl = this.form.get(field);
    return !!(ctrl?.invalid && ctrl?.touched);
  }

  getError(field: string): string {
    const ctrl = this.form.get(field);
    if (!ctrl?.errors) return '';
    if (ctrl.errors['required']) return 'Este campo es requerido';
    if (ctrl.errors['minlength']) return `Mínimo ${ctrl.errors['minlength'].requiredLength} caracteres`;
    return 'Valor inválido';
  }
}

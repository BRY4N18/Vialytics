import {
  Component,
  OnInit,
  input,
  output,
  signal,
  computed,
  inject,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
} from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { AccidenteService } from '../../../core/services/accidente.service';
import { ToastService } from '../../../core/services/toast.service';
import {
  AccidenteMapa,
  TipoReportado,
  RegistroAccidentePayload,
  Pais,
  Estado,
  Condado,
  Ciudad,
  Calle,
  Clima,
  ElementoFisico,
  PeriodoDia,
} from '../../../core/models/accidente.model';

declare const L: any;

@Component({
  selector: 'app-registro-accidente',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './registro-accidente.html',
  styleUrl: './registro-accidente.css',
})
export class RegistroAccidenteComponent implements OnInit {
  ubicacion = input<{ lat: number; lng: number } | null>(null);

  cancelar = output<void>();
  accidenteRegistrado = output<AccidenteMapa>();

  private readonly fb = inject(FormBuilder);
  private readonly accidenteService = inject(AccidenteService);
  private readonly toastService = inject(ToastService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  form!: FormGroup;

  // Edit mode
  readonly modoEdicion = signal(false);
  private editId: string | null = null;
  
  // Catalogs signals
  readonly tiposReportado = signal<TipoReportado[]>([]);
  readonly paises = signal<Pais[]>([]);
  readonly estados = signal<Estado[]>([]);
  readonly condados = signal<Condado[]>([]);
  readonly ciudades = signal<Ciudad[]>([]);
  readonly calles = signal<Calle[]>([]);
  readonly climas = signal<Clima[]>([]);
  readonly elementosFisicos = signal<ElementoFisico[]>([]);
  readonly periodosDias = signal<PeriodoDia[]>([]);

  readonly cargando = signal(false);
  readonly error = signal<string | null>(null);

  // Reactivity and manual severity signals
  readonly formValues = signal({ numheridos: 0, numfallecidos: 0, numvehiculos: 1 });
  readonly modoManualSeveridad = signal(false);
  readonly severidadManual = signal<number | null>(null);

  // Interactive Modal Map and Reverse Geocoding signals
  readonly mostrarMapaModal = signal(false);
  readonly seleccionadoModalCoords = signal<{ lat: number; lng: number } | null>(null);
  readonly resolviendoDireccion = signal(false);
  readonly estadoResolucion = signal<string>('');

  private modalMap: any = null;
  private modalMarker: any = null;

  readonly severidadCalculada = computed(() => {
    const h = Number(this.formValues().numheridos) || 0;
    const f = Number(this.formValues().numfallecidos) || 0;
    const v = Number(this.formValues().numvehiculos) || 1;
    
    // Custom premium calculation matching backend severidad_service
    if (f > 0) return 4; // Crítica
    if (h >= 3 || v >= 4) return 3; // Grave
    if (h >= 1 || v >= 2) return 2; // Moderada
    return 1; // Leve
  });

  readonly severidadFinal = computed(() => {
    return this.modoManualSeveridad() && this.severidadManual() !== null
      ? this.severidadManual()!
      : this.severidadCalculada();
  });

  ngOnInit(): void {
    this.buildForm();
    
    // Dynamic live synchronization for severity computation
    this.formValues.set({
      numheridos: this.form.get('numheridos')?.value || 0,
      numfallecidos: this.form.get('numfallecidos')?.value || 0,
      numvehiculos: this.form.get('numvehiculos')?.value || 1,
    });
    this.form.valueChanges.subscribe((val) => {
      this.formValues.set({
        numheridos: Number(val.numheridos) || 0,
        numfallecidos: Number(val.numfallecidos) || 0,
        numvehiculos: Number(val.numvehiculos) || 1,
      });
    });

    this.loadInitialCatalogs();
    this.setupCascades();

    // Detect edit mode from query param
    this.route.queryParams.subscribe((params) => {
      const editId = params['edit'];
      if (editId) {
        this.editId = editId;
        this.modoEdicion.set(true);
        this.cargarDatosEdicion(editId);
      }
    });
  }

  private buildForm(): void {
    const loc = this.ubicacion();
    this.form = this.fb.group({
      latitudinicio: [loc?.lat ?? '', [Validators.required, Validators.pattern(/^-?[0-9]+(\.[0-9]+)?$/)]],
      longitudinicio: [loc?.lng ?? '', [Validators.required, Validators.pattern(/^-?[0-9]+(\.[0-9]+)?$/)]],
      
      numvehiculos: [1, [Validators.required, Validators.min(1), Validators.max(50)]],
      numheridos: [0, [Validators.required, Validators.min(0), Validators.max(200)]],
      numfallecidos: [0, [Validators.required, Validators.min(0), Validators.max(100)]],
      descripcion: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(500)]],
      
      // Cascading Location Dropdowns
      idpais_id: ['', Validators.required],
      idestado_id: [{ value: '', disabled: true }, Validators.required],
      idcondado_id: [{ value: '', disabled: true }, Validators.required],
      idciudad_id: [{ value: '', disabled: true }, Validators.required],
      idcalle_id: [{ value: '', disabled: true }, Validators.required],
      
      // Environmental catalogs (now driven dynamically via custom inputs)
      idperiododia_id: ['1'],
      idestadoclima_id: ['1'],
      idelementofisico_id: ['1'],
      idtiporeportado_id: ['', Validators.required],
      
      codigopostal: [''],
      nota_inicial: [''],

      // Detailed Custom Fields:
      // Climate
      condicion_clima: ['Despejado', Validators.required],
      temperatura_f: [72, [Validators.required, Validators.min(-100), Validators.max(150)]],
      humedad_porcentaje: [50, [Validators.required, Validators.min(0), Validators.max(100)]],
      visibilidad_millas: [10, [Validators.required, Validators.min(0), Validators.max(100)]],
      velocidad_viento_mph: [0, [Validators.required, Validators.min(0), Validators.max(200)]],
      
      // Driver State
      estadosobriedad: [true],
      nivelatencion: [true],
      condicionfisica: [true],
      usoseguridad: [true],
      
      // Physical Elements
      cerca_cruce: [false],
      cerca_semaforo: [false],
      cerca_parada: [false],
      cerca_estacion: [false],
      cerca_bache: [false],
      cerca_viatren: [false],
      
      // Day Period
      amaneceranochecer: ['Day', Validators.required],
      crepusculocivil: ['Day', Validators.required],
      crepusculonautico: ['Day', Validators.required],
      crepusculoastronomico: ['Day', Validators.required],
      
      // Station
      codigoaeropuerto: ['KJFK'],
      zonahoraria: ['US/Eastern'],
    });

    if (loc) {
      this.form.patchValue({
        latitudinicio: loc.lat,
        longitudinicio: loc.lng,
      });
    }
  }

  private loadInitialCatalogs(): void {
    this.accidenteService.getTiposReportado().subscribe({
      next: (tipos) => this.tiposReportado.set(tipos),
      error: () => this.error.set('Error cargando tipos de reporte'),
    });

    this.accidenteService.getPaises().subscribe({
      next: (p) => this.paises.set(p),
      error: () => this.error.set('Error cargando países'),
    });

    this.accidenteService.getClimas().subscribe({
      next: (c) => this.climas.set(c),
      error: () => this.error.set('Error cargando climas'),
    });

    this.accidenteService.getElementosFisicos().subscribe({
      next: (ef) => this.elementosFisicos.set(ef),
      error: () => this.error.set('Error cargando elementos físicos'),
    });

    this.accidenteService.getPeriodosDias().subscribe({
      next: (pd) => this.periodosDias.set(pd),
      error: () => this.error.set('Error cargando periodos del día'),
    });
  }

  private setupCascades(): void {
    // 1. Country Change -> Fetch States
    this.form.get('idpais_id')?.valueChanges.subscribe((paisId) => {
      const selectedPais = this.paises().find((p) => p.idpais === Number(paisId));
      const estadoCtrl = this.form.get('idestado_id');
      
      this.estados.set([]);
      this.condados.set([]);
      this.ciudades.set([]);
      this.calles.set([]);
      
      estadoCtrl?.setValue('');
      estadoCtrl?.disable();
      
      if (selectedPais) {
        this.accidenteService.getEstados(selectedPais.pais).subscribe({
          next: (est) => {
            this.estados.set(est);
            estadoCtrl?.enable();
          },
        });
      }
      this.resetLocationCascades(1);
    });

    // 2. State Change -> Fetch Counties
    this.form.get('idestado_id')?.valueChanges.subscribe((estadoId) => {
      const selectedEst = this.estados().find((e) => e.idestado === Number(estadoId));
      const condadoCtrl = this.form.get('idcondado_id');
      
      this.condados.set([]);
      this.ciudades.set([]);
      this.calles.set([]);
      
      condadoCtrl?.setValue('');
      condadoCtrl?.disable();
      
      if (selectedEst) {
        this.accidenteService.getCondados(selectedEst.estado).subscribe({
          next: (cond) => {
            this.condados.set(cond);
            condadoCtrl?.enable();
          },
        });
      }
      this.resetLocationCascades(2);
    });

    // 3. County Change -> Fetch Cities
    this.form.get('idcondado_id')?.valueChanges.subscribe((condadoId) => {
      const selectedCond = this.condados().find((c) => c.idcondado === Number(condadoId));
      const ciudadCtrl = this.form.get('idciudad_id');
      
      this.ciudades.set([]);
      this.calles.set([]);
      
      ciudadCtrl?.setValue('');
      ciudadCtrl?.disable();
      
      if (selectedCond) {
        this.accidenteService.getCiudades(selectedCond.condado).subscribe({
          next: (ciu) => {
            this.ciudades.set(ciu);
            ciudadCtrl?.enable();
          },
        });
      }
      this.resetLocationCascades(3);
    });

    // 4. City Change -> Fetch Streets
    this.form.get('idciudad_id')?.valueChanges.subscribe((ciudadId) => {
      const selectedCiu = this.ciudades().find((c) => c.idciudad === Number(ciudadId));
      const calleCtrl = this.form.get('idcalle_id');
      
      this.calles.set([]);
      calleCtrl?.setValue('');
      calleCtrl?.disable();
      
      if (selectedCiu) {
        this.accidenteService.getCalles(selectedCiu.ciudad).subscribe({
          next: (cal) => {
            this.calles.set(cal);
            calleCtrl?.enable();
          },
        });
      }
    });
  }

  private resetLocationCascades(level: number): void {
    if (level <= 1) {
      this.form.get('idcondado_id')?.setValue('');
      this.form.get('idcondado_id')?.disable();
    }
    if (level <= 2) {
      this.form.get('idciudad_id')?.setValue('');
      this.form.get('idciudad_id')?.disable();
    }
    if (level <= 3) {
      this.form.get('idcalle_id')?.setValue('');
      this.form.get('idcalle_id')?.disable();
    }
  }

  // --- PREMIUM INCREMENT/DECREMENT SELECTORS ---
  increment(field: string, max: number): void {
    const ctrl = this.form.get(field);
    if (ctrl) {
      const val = Number(ctrl.value) || 0;
      if (val < max) ctrl.setValue(val + 1);
    }
  }

  decrement(field: string, min: number): void {
    const ctrl = this.form.get(field);
    if (ctrl) {
      const val = Number(ctrl.value) || 0;
      if (val > min) ctrl.setValue(val - 1);
    }
  }

  toggleModoManualSeveridad(): void {
    const current = this.modoManualSeveridad();
    this.modoManualSeveridad.set(!current);
    if (!current) {
      this.severidadManual.set(this.severidadCalculada());
    } else {
      this.severidadManual.set(null);
    }
  }

  seleccionarSeveridadManual(level: number): void {
    if (this.modoManualSeveridad()) {
      this.severidadManual.set(level);
    }
  }

  onClimaChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    if (value === 'Despejado') {
      this.form.patchValue({ temperatura_f: 72, humedad_porcentaje: 50, visibilidad_millas: 10, velocidad_viento_mph: 0 });
    } else if (value === 'Nublado') {
      this.form.patchValue({ temperatura_f: 60, humedad_porcentaje: 65, visibilidad_millas: 10, velocidad_viento_mph: 8 });
    } else if (value === 'Lluvia Ligera') {
      this.form.patchValue({ temperatura_f: 55, humedad_porcentaje: 88, visibilidad_millas: 4, velocidad_viento_mph: 10 });
    } else if (value === 'Tormenta') {
      this.form.patchValue({ temperatura_f: 68, humedad_porcentaje: 95, visibilidad_millas: 2, velocidad_viento_mph: 18 });
    }
  }

  private buildPayload(): RegistroAccidentePayload {
    const raw = this.form.getRawValue();
    return {
      latitudinicio: Number(raw.latitudinicio),
      longitudinicio: Number(raw.longitudinicio),
      numvehiculos: Number(raw.numvehiculos),
      numheridos: Number(raw.numheridos),
      numfallecidos: Number(raw.numfallecidos),
      descripcion: raw.descripcion,
      idpais_id: Number(raw.idpais_id),
      idestado_id: Number(raw.idestado_id),
      idcondado_id: Number(raw.idcondado_id),
      idciudad_id: Number(raw.idciudad_id),
      idcalle_id: Number(raw.idcalle_id),
      idperiododia_id: Number(raw.idperiododia_id) || 1,
      idestadoclima_id: 1,
      idelementofisico_id: 1,
      idtiporeportado_id: Number(raw.idtiporeportado_id),
      idseveridad_id: this.severidadFinal(),
      nota_inicial: raw.nota_inicial || undefined,
      codigopostal: raw.codigopostal || undefined,
      condicion_clima: raw.condicion_clima,
      temperatura_f: Number(raw.temperatura_f),
      humedad_porcentaje: Number(raw.humedad_porcentaje),
      visibilidad_millas: Number(raw.visibilidad_millas),
      velocidad_viento_mph: Number(raw.velocidad_viento_mph),
      cerca_cruce: !!raw.cerca_cruce,
      cerca_semaforo: !!raw.cerca_semaforo,
      cerca_parada: !!raw.cerca_parada,
      cerca_estacion: !!raw.cerca_estacion,
      cerca_bache: !!raw.cerca_bache,
      cerca_viatren: !!raw.cerca_viatren,
      estadosobriedad: !!raw.estadosobriedad,
      nivelatencion: !!raw.nivelatencion,
      condicionfisica: !!raw.condicionfisica,
      usoseguridad: !!raw.usoseguridad,
      amaneceranochecer: raw.amaneceranochecer,
      crepusculocivil: raw.crepusculocivil,
      crepusculonautico: raw.crepusculonautico,
      crepusculoastronomico: raw.crepusculoastronomico,
      codigoaeropuerto: raw.codigoaeropuerto || undefined,
      zonahoraria: raw.zonahoraria || undefined,
    };
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.cargando.set(true);
    this.error.set(null);

    const payload = this.buildPayload();

    if (this.modoEdicion() && this.editId) {
      // UPDATE existing accident
      this.accidenteService.actualizarAccidente(this.editId, payload).subscribe({
        next: () => {
          this.cargando.set(false);
          this.toastService.show('¡Accidente actualizado correctamente!', 'success');
          this.router.navigate(['/lista-accidentes']);
        },
        error: (err) => {
          this.cargando.set(false);
          const errMsg = err.message || 'Error al actualizar el accidente';
          this.toastService.show(errMsg, 'error');
          this.error.set(errMsg);
        },
      });
    } else {
      // CREATE new accident
      this.accidenteService.registrarAccidente(payload).subscribe({
        next: (accidente) => {
          this.cargando.set(false);
          this.toastService.show('¡Accidente registrado exitosamente en el Centro de Control!', 'success');
          this.accidenteRegistrado.emit(accidente);
          this.router.navigate(['/']);
        },
        error: (err) => {
          this.cargando.set(false);
          const errMsg = err.message || 'Error al registrar el accidente en el servidor';
          this.toastService.show(errMsg, 'error');
          this.error.set(errMsg);
        },
      });
    }
  }

  private cargarDatosEdicion(id: string): void {
    this.cargando.set(true);
    this.accidenteService.getAccidenteDetalle(id).subscribe({
      next: async (detalle) => {
        this.cargando.set(false);

        // ── 1. Campos básicos ──────────────────────────────────────────────────
        this.form.patchValue({
          latitudinicio: detalle.latitudinicio,
          longitudinicio: detalle.longitudinicio,
          numvehiculos: detalle.numvehiculos ?? 1,
          numheridos: detalle.numheridos ?? 0,
          numfallecidos: detalle.numfallecidos ?? 0,
          descripcion: detalle.descripcion ?? '',
          codigopostal: detalle.codigopostal ?? '',
        });

        // ── 2. Severidad ───────────────────────────────────────────────────────
        const sevNivel = detalle.idseveridad_id ?? detalle.severidad_nivel;
        if (sevNivel) {
          this.modoManualSeveridad.set(true);
          this.severidadManual.set(sevNivel);
        }

        // ── 3. Clima ───────────────────────────────────────────────────────────
        this.form.patchValue({
          condicion_clima: detalle.condicion_clima ?? 'Despejado',
          temperatura_f: detalle.temperatura_f ?? 72,
          humedad_porcentaje: detalle.humedad_porcentaje ?? 50,
          visibilidad_millas: detalle.visibilidad_millas ?? 10,
          velocidad_viento_mph: detalle.velocidad_viento_mph ?? 0,
        });

        // ── 4. Período del día ─────────────────────────────────────────────────
        this.form.patchValue({
          amaneceranochecer: detalle.amaneceranochecer ?? 'Day',
          crepusculocivil: detalle.crepusculocivil ?? 'Day',
          crepusculonautico: detalle.crepusculonautico ?? 'Day',
          crepusculoastronomico: detalle.crepusculoastronomico ?? 'Day',
        });
        if (detalle.idperiododia_id) {
          this.form.patchValue({ idperiododia_id: detalle.idperiododia_id.toString() });
        }

        // ── 5. Elementos físicos ───────────────────────────────────────────────
        this.form.patchValue({
          cerca_cruce: detalle.cerca_cruce ?? false,
          cerca_semaforo: detalle.cerca_semaforo ?? false,
          cerca_parada: detalle.cerca_parada ?? false,
          cerca_estacion: detalle.cerca_estacion ?? false,
          cerca_bache: detalle.cerca_bache ?? false,
          cerca_viatren: detalle.cerca_viatren ?? false,
        });

        // ── 6. Estado del conductor ────────────────────────────────────────────
        this.form.patchValue({
          estadosobriedad: detalle.estadosobriedad ?? true,
          nivelatencion: detalle.nivelatencion ?? true,
          condicionfisica: detalle.condicionfisica ?? true,
          usoseguridad: detalle.usoseguridad ?? true,
        });

        // ── 7. Estación de referencia ──────────────────────────────────────────
        this.form.patchValue({
          codigoaeropuerto: detalle.codigoaeropuerto ?? 'KJFK',
          zonahoraria: detalle.zonahoraria ?? 'US/Eastern',
        });

        // ── 8. Tipo reportado ──────────────────────────────────────────────────
        if (detalle.idtiporeportado_id) {
          this.form.patchValue({ idtiporeportado_id: detalle.idtiporeportado_id.toString() });
        }

        // ── 9. Cascada de ubicación ────────────────────────────────────────────
        // Si el backend devolvió los IDs directamente, los usamos sin reverse geocoding
        const hasDirIds = detalle.idpais_id && detalle.idestado_id &&
                          detalle.idcondado_id && detalle.idciudad_id && detalle.idcalle_id;
        if (hasDirIds) {
          this.poblarCascadaConIds(detalle);
        } else if (detalle.latitudinicio && detalle.longitudinicio) {
          // Fallback: resolver desde coordenadas
          this.resolverUbicacionCascada(detalle.latitudinicio, detalle.longitudinicio);
        }
      },
      error: (err) => {
        this.cargando.set(false);
        const errMsg = 'No se pudo cargar el accidente para editar';
        this.toastService.show(errMsg, 'error');
        this.error.set(errMsg);
      },
    });
  }

  /**
   * Pre-llena la cascada de ubicación usando los IDs de clave foránea del backend
   * sin necesidad de hacer reverse geocoding externo.
   */
  private poblarCascadaConIds(detalle: any): void {
    this.resolviendoDireccion.set(true);
    this.estadoResolucion.set('Cargando datos de ubicación guardados...');

    Promise.all([
      firstValueFrom(this.accidenteService.getPaises()),
      firstValueFrom(this.accidenteService.getEstados()),
      firstValueFrom(this.accidenteService.getCondados()),
      firstValueFrom(this.accidenteService.getCiudades()),
      firstValueFrom(this.accidenteService.getCalles()),
    ]).then(([allPaises, allEstados, allCondados, allCiudades, allCalles]) => {
      const matchPais    = allPaises.find(p => p.idpais === Number(detalle.idpais_id));
      const matchEstado  = allEstados.find(e => e.idestado === Number(detalle.idestado_id));
      const matchCondado = allCondados.find(c => c.idcondado === Number(detalle.idcondado_id));
      const matchCiudad  = allCiudades.find(c => c.idciudad === Number(detalle.idciudad_id));
      const matchCalle   = allCalles.find(c => c.idcalle === Number(detalle.idcalle_id));

      this.paises.set(allPaises);

      if (matchPais) {
        const filtEstados = allEstados.filter(e => e.pais === matchPais.pais);
        this.estados.set(filtEstados);
        this.form.get('idpais_id')?.setValue(matchPais.idpais.toString(), { emitEvent: false });
        this.form.get('idestado_id')?.enable({ emitEvent: false });
      }
      if (matchEstado) {
        const filtCondados = allCondados.filter(c => c.estado === matchEstado.estado);
        this.condados.set(filtCondados);
        this.form.get('idestado_id')?.setValue(matchEstado.idestado.toString(), { emitEvent: false });
        this.form.get('idcondado_id')?.enable({ emitEvent: false });
      }
      if (matchCondado) {
        const filtCiudades = allCiudades.filter(c => c.condado === matchCondado.condado);
        this.ciudades.set(filtCiudades);
        this.form.get('idcondado_id')?.setValue(matchCondado.idcondado.toString(), { emitEvent: false });
        this.form.get('idciudad_id')?.enable({ emitEvent: false });
      }
      if (matchCiudad) {
        const filtCalles = allCalles.filter(c => c.ciudad === matchCiudad.ciudad);
        this.calles.set(filtCalles);
        this.form.get('idciudad_id')?.setValue(matchCiudad.idciudad.toString(), { emitEvent: false });
        this.form.get('idcalle_id')?.enable({ emitEvent: false });
      }
      if (matchCalle) {
        this.form.get('idcalle_id')?.setValue(matchCalle.idcalle.toString(), { emitEvent: false });
        this.estadoResolucion.set('¡Ubicación cargada correctamente!');
      }

      setTimeout(() => this.resolviendoDireccion.set(false), 1200);
    }).catch(() => {
      this.resolviendoDireccion.set(false);
      // Fallback a geocodificación inversa
      if (detalle.latitudinicio && detalle.longitudinicio) {
        this.resolverUbicacionCascada(detalle.latitudinicio, detalle.longitudinicio);
      }
    });
  }

  onCancelar(): void {
    this.cancelar.emit();
    this.router.navigate(['/']);
  }

  isInvalid(field: string): boolean {
    const ctrl = this.form.get(field);
    return !!(ctrl?.invalid && ctrl?.touched);
  }

  getError(field: string): string {
    const ctrl = this.form.get(field);
    if (!ctrl?.errors) return '';
    if (ctrl.errors['required']) return 'Este campo es requerido';
    if (ctrl.errors['min']) return `Valor mínimo: ${ctrl.errors['min'].min}`;
    if (ctrl.errors['max']) return `Valor máximo: ${ctrl.errors['max'].max}`;
    if (ctrl.errors['minlength']) return `Mínimo ${ctrl.errors['minlength'].requiredLength} caracteres`;
    return 'Valor inválido';
  }

  // --- MAP MODAL & REVERSE GEOCODING METHODS ---
  abrirMapaModal(): void {
    this.mostrarMapaModal.set(true);
    this.seleccionadoModalCoords.set(null);
    setTimeout(() => {
      this.initModalMap();
    }, 100);
  }

  cerrarMapaModal(): void {
    if (this.modalMap) {
      this.modalMap.remove();
      this.modalMap = null;
    }
    this.modalMarker = null;
    this.mostrarMapaModal.set(false);
  }

  initModalMap(): void {
    const currentLat = Number(this.form.get('latitudinicio')?.value);
    const currentLng = Number(this.form.get('longitudinicio')?.value);
    const center: [number, number] = (currentLat && currentLng) 
      ? [currentLat, currentLng] 
      : [-1.8312, -78.1834];
    const initialZoom = (currentLat && currentLng) ? 14 : 7;

    this.modalMap = L.map('modal-map-container', {
      center: center,
      zoom: initialZoom,
      zoomControl: true,
      attributionControl: false
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19
    }).addTo(this.modalMap);

    if (currentLat && currentLng) {
      this.setModalLocationMarker(currentLat, currentLng);
      this.seleccionadoModalCoords.set({ lat: currentLat, lng: currentLng });
    }

    this.modalMap.on('click', (e: any) => {
      const { lat, lng } = e.latlng;
      this.setModalLocationMarker(lat, lng);
      this.seleccionadoModalCoords.set({ lat, lng });
    });
  }

  private setModalLocationMarker(lat: number, lng: number): void {
    if (this.modalMarker) {
      this.modalMap.removeLayer(this.modalMarker);
    }
    const icon = L.divIcon({
      className: '',
      html: `<div style="
        width:24px;height:24px;
        background:#3B82F6;
        border:3px solid white;
        border-radius:50%;
        box-shadow:0 0 20px rgba(59,130,246,0.8);
        transform:translate(-50%,-50%);
      "></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });
    this.modalMarker = L.marker([lat, lng], { icon }).addTo(this.modalMap);
  }

  confirmarUbicacionModal(): void {
    const coords = this.seleccionadoModalCoords();
    if (!coords) return;

    this.form.patchValue({
      latitudinicio: coords.lat.toFixed(6),
      longitudinicio: coords.lng.toFixed(6)
    });

    this.cerrarMapaModal();
    this.resolverUbicacionCascada(coords.lat, coords.lng);
  }

  resolverUbicacionCascada(lat: number, lng: number): void {
    this.resolviendoDireccion.set(true);
    this.estadoResolucion.set('Identificando coordenadas...');

    const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`;
    
    fetch(url, {
      headers: {
        'Accept-Language': 'es'
      }
    })
      .then(res => res.json())
      .then(data => {
        if (data && data.address) {
          this.autocompletarCascada(data.address);
        } else {
          this.finalizarResolucion('No se pudo geolocalizar la dirección exacta.');
        }
      })
      .catch(err => {
        console.error(err);
        this.finalizarResolucion('Error en el servicio de geolocalización.');
      });
  }

  async autocompletarCascada(address: any): Promise<void> {
    try {
      const paisName = address.country || '';
      const estadoName = address.state || '';
      const condadoName = address.county || address.state_district || '';
      const ciudadName = address.city || address.town || address.village || address.suburb || '';
      const calleName = address.road || address.pedestrian || '';
      const codigoPostal = address.postcode || '';

      if (codigoPostal) {
        this.form.patchValue({ codigopostal: codigoPostal });
      }

      this.estadoResolucion.set('Cargando base de datos cartográfica local...');
      
      // Load all references concurrently to execute bottom-up matching in-memory
      const [allPaises, allEstados, allCondados, allCiudades, allCalles] = await Promise.all([
        firstValueFrom(this.accidenteService.getPaises()),
        firstValueFrom(this.accidenteService.getEstados()),
        firstValueFrom(this.accidenteService.getCondados()),
        firstValueFrom(this.accidenteService.getCiudades()),
        firstValueFrom(this.accidenteService.getCalles())
      ]);

      let matchedPais: any = null;
      let matchedEstado: any = null;
      let matchedCondado: any = null;
      let matchedCiudad: any = null;
      let matchedCalle: any = null;

      // --- BOTTOM-UP RESOLUTION CHAINS ---

      // 1. Try starting from Calle (Street)
      if (calleName) {
        matchedCalle = allCalles.find(c => this.stringsMatch(c.calle, calleName)) ||
                       allCalles.find(c => this.stringsPartialMatch(c.calle, calleName));

        if (matchedCalle) {
          this.estadoResolucion.set('Identificada calle: ' + matchedCalle.calle + '. Vinculando...');
          matchedCiudad = allCiudades.find(c => this.stringsMatch(c.ciudad, matchedCalle.ciudad));
          if (matchedCiudad) {
            matchedCondado = allCondados.find(c => this.stringsMatch(c.condado, matchedCiudad.condado));
          }
          if (matchedCondado) {
            matchedEstado = allEstados.find(e => this.stringsMatch(e.estado, matchedCondado.estado));
          }
          if (matchedEstado) {
            matchedPais = allPaises.find(p => this.stringsMatch(p.pais, matchedEstado.pais));
          }
        }
      }

      // 2. Fallback to City (Ciudad) if Street not matched
      if (!matchedCiudad && ciudadName) {
        matchedCiudad = allCiudades.find(c => this.stringsMatch(c.ciudad, ciudadName)) ||
                        allCiudades.find(c => this.stringsPartialMatch(c.ciudad, ciudadName));

        if (matchedCiudad) {
          this.estadoResolucion.set('Identificada ciudad: ' + matchedCiudad.ciudad + '. Vinculando...');
          matchedCondado = allCondados.find(c => this.stringsMatch(c.condado, matchedCiudad.condado));
          if (matchedCondado) {
            matchedEstado = allEstados.find(e => this.stringsMatch(e.estado, matchedCondado.estado));
          }
          if (matchedEstado) {
            matchedPais = allPaises.find(p => this.stringsMatch(p.pais, matchedEstado.pais));
          }
        }
      }

      // 3. Fallback to County (Condado) if City not matched
      if (!matchedCondado && condadoName) {
        matchedCondado = allCondados.find(c => this.stringsMatch(c.condado, condadoName)) ||
                         allCondados.find(c => this.stringsPartialMatch(c.condado, condadoName));

        if (matchedCondado) {
          this.estadoResolucion.set('Identificado condado: ' + matchedCondado.condado + '. Vinculando...');
          matchedEstado = allEstados.find(e => this.stringsMatch(e.estado, matchedCondado.estado));
          if (matchedEstado) {
            matchedPais = allPaises.find(p => this.stringsMatch(p.pais, matchedEstado.pais));
          }
        }
      }

      // 4. Fallback to State (Estado) if County not matched
      if (!matchedEstado && estadoName) {
        matchedEstado = allEstados.find(e => this.stringsMatch(e.estado, estadoName)) ||
                        allEstados.find(e => this.stringsPartialMatch(e.estado, estadoName));

        if (matchedEstado) {
          this.estadoResolucion.set('Identificado estado: ' + matchedEstado.estado + '. Vinculando...');
          matchedPais = allPaises.find(p => this.stringsMatch(p.pais, matchedEstado.pais));
        }
      }

      // 5. Fallback to Country (País) if State not matched
      if (!matchedPais && paisName) {
        matchedPais = allPaises.find(p => this.stringsMatch(p.pais, paisName)) ||
                      allPaises.find(p => this.stringsPartialMatch(p.pais, paisName));
      }

      // --- POPULATE RESOLVED DATA AND SIGNALS ---
      this.paises.set(allPaises);

      if (matchedPais) {
        const filteredStates = allEstados.filter(e => e.pais === matchedPais.pais);
        this.estados.set(filteredStates);
        this.form.get('idpais_id')?.setValue(matchedPais.idpais.toString(), { emitEvent: false });
        this.form.get('idestado_id')?.enable({ emitEvent: false });
      }

      if (matchedEstado) {
        const filteredCondados = allCondados.filter(c => c.estado === matchedEstado.estado);
        this.condados.set(filteredCondados);
        this.form.get('idestado_id')?.setValue(matchedEstado.idestado.toString(), { emitEvent: false });
        this.form.get('idcondado_id')?.enable({ emitEvent: false });
      } else {
        this.resetLocationCascades(1);
      }

      if (matchedCondado) {
        const filteredCiudades = allCiudades.filter(c => c.condado === matchedCondado.condado);
        this.ciudades.set(filteredCiudades);
        this.form.get('idcondado_id')?.setValue(matchedCondado.idcondado.toString(), { emitEvent: false });
        this.form.get('idciudad_id')?.enable({ emitEvent: false });
      } else {
        this.resetLocationCascades(2);
      }

      if (matchedCiudad) {
        const filteredCalles = allCalles.filter(c => c.ciudad === matchedCiudad.ciudad);
        this.calles.set(filteredCalles);
        this.form.get('idciudad_id')?.setValue(matchedCiudad.idciudad.toString(), { emitEvent: false });
        this.form.get('idcalle_id')?.enable({ emitEvent: false });
      } else {
        this.resetLocationCascades(3);
      }

      if (matchedCalle) {
        this.form.get('idcalle_id')?.setValue(matchedCalle.idcalle.toString(), { emitEvent: false });
        this.estadoResolucion.set('¡Ubicación resuelta con éxito hasta nivel calle!');
      } else if (matchedPais) {
        this.estadoResolucion.set('Ubicación resuelta parcialmente. Complete manualmente.');
      } else {
        this.estadoResolucion.set('Ubicación no encontrada en los catálogos.');
      }

      setTimeout(() => {
        this.resolviendoDireccion.set(false);
      }, 1500);

    } catch (error) {
      console.error(error);
      this.finalizarResolucion('Error al resolver la cascada de ubicación.');
    }
  }

  private stringsMatch(str1: string, str2: string): boolean {
    if (!str1 || !str2) return false;
    const norm = (s: string) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
    return norm(str1) === norm(str2);
  }

  private stringsPartialMatch(str1: string, str2: string): boolean {
    if (!str1 || !str2) return false;
    const norm = (s: string) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
    const n1 = norm(str1);
    const n2 = norm(str2);
    return n1.includes(n2) || n2.includes(n1);
  }

  private finalizarResolucion(msg: string): void {
    this.estadoResolucion.set(msg);
    setTimeout(() => {
      this.resolviendoDireccion.set(false);
    }, 2500);
  }
}

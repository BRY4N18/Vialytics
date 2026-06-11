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
  FormArray,
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
  readonly registrarDetallesVehiculos = signal(false);

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
  readonly mostrarModalRevision = signal(false);

  private modalMap: any = null;
  private modalMarker: any = null;

  readonly severidadCalculada = computed(() => {
    const h = Number(this.formValues().numheridos) || 0;
    const f = Number(this.formValues().numfallecidos) || 0;
    const v = Number(this.formValues().numvehiculos) || 1;

    if (f > 0) return 4;
    if (h >= 3 || v >= 4) return 3;
    if (h >= 1 || v >= 2) return 2;
    return 1;
  });

  readonly severidadFinal = computed(() => {
    return this.modoManualSeveridad() && this.severidadManual() !== null
      ? this.severidadManual()!
      : this.severidadCalculada();
  });

  ngOnInit(): void {
    this.buildForm();

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
      this.ajustarFormArrayVehiculos();
    });

    this.loadInitialCatalogs();
    this.setupCascades();

    this.route.queryParams.subscribe((params) => {
      const editId = params['edit'];
      if (editId) {
        this.editId = editId;
        this.modoEdicion.set(true);
        this.cargarDatosEdicion(editId);
      }
    });
  }

  get vehiculosDetalles(): FormArray {
    return this.form.get('vehiculos_detalles') as FormArray;
  }

  toggleRegistrarDetallesVehiculos(): void {
    this.registrarDetallesVehiculos.set(!this.registrarDetallesVehiculos());
    this.ajustarFormArrayVehiculos();
  }

  crearVehiculoFormGroup(detalle?: any): FormGroup {
    return this.fb.group({
      tipovehiculo: [detalle?.tipovehiculo ?? 'Automóvil', Validators.required],
      modelovehiculo: [detalle?.modelovehiculo ?? '', Validators.required],
      categoriausovehiculo: [detalle?.categoriausovehiculo ?? 'Particular', Validators.required],
      mercanciapeligrosa: [detalle?.mercanciapeligrosa ?? false],
      ejes: [detalle?.ejes ?? 2, [Validators.required, Validators.min(1), Validators.max(20)]],
      nombres: [detalle?.nombres ?? '', Validators.required],
      apellidos: [detalle?.apellidos ?? '', Validators.required],
      identificacion: [detalle?.identificacion ?? ''],
      genero: [detalle?.genero ?? 'M', Validators.required],
      tipolicencia: [detalle?.tipolicencia ?? 'B', Validators.required],
      estadolicencia: [detalle?.estadolicencia ?? 'Vigente', Validators.required],
      ciudadresidencia: [detalle?.ciudadresidencia ?? 'Quito', Validators.required],
      aniosexperiencia: [detalle?.aniosexperiencia ?? 0, [Validators.required, Validators.min(0), Validators.max(80)]],
      estadosobriedad: [detalle?.estadosobriedad ?? true],
      nivelatencion: [detalle?.nivelatencion ?? true],
      condicionfisica: [detalle?.condicionfisica ?? true],
      usoseguridad: [detalle?.usoseguridad ?? true]
    });
  }

  ajustarFormArrayVehiculos(): void {
    const count = Number(this.form.get('numvehiculos')?.value) || 1;
    const currentCount = this.vehiculosDetalles.length;

    if (this.registrarDetallesVehiculos()) {
      if (currentCount < count) {
        for (let i = currentCount; i < count; i++) {
          this.vehiculosDetalles.push(this.crearVehiculoFormGroup());
        }
      } else if (currentCount > count) {
        for (let i = currentCount - 1; i >= count; i--) {
          this.vehiculosDetalles.removeAt(i);
        }
      }
    } else {
      this.vehiculosDetalles.clear();
    }
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
      idpais_id: ['', Validators.required],
      idestado_id: [{ value: '', disabled: true }, Validators.required],
      idcondado_id: [{ value: '', disabled: true }, Validators.required],
      idciudad_id: [{ value: '', disabled: true }, Validators.required],
      idcalle_id: [{ value: '', disabled: true }, Validators.required],
      idperiododia_id: ['1'],
      idestadoclima_id: ['1'],
      idelementofisico_id: ['1'],
      idtiporeportado_id: ['', Validators.required],
      codigopostal: [''],
      nota_inicial: [''],
      condicion_clima: ['Despejado', Validators.required],
      temperatura_f: [72, [Validators.required, Validators.min(-100), Validators.max(150)]],
      humedad_porcentaje: [50, [Validators.required, Validators.min(0), Validators.max(100)]],
      visibilidad_millas: [10, [Validators.required, Validators.min(0), Validators.max(100)]],
      velocidad_viento_mph: [0, [Validators.required, Validators.min(0), Validators.max(200)]],
      estadosobriedad: [true],
      nivelatencion: [true],
      condicionfisica: [true],
      usoseguridad: [true],
      cerca_cruce: [false],
      cerca_semaforo: [false],
      cerca_parada: [false],
      cerca_estacion: [false],
      cerca_bache: [false],
      cerca_viatren: [false],
      amaneceranochecer: ['Day', Validators.required],
      crepusculocivil: ['Day', Validators.required],
      crepusculonautico: ['Day', Validators.required],
      crepusculoastronomico: ['Day', Validators.required],
      codigoaeropuerto: ['KJFK'],
      zonahoraria: ['US/Eastern'],
      vehiculos_detalles: this.fb.array([])
    });

    if (loc) {
      this.form.patchValue({
        latitudinicio: loc.lat,
        longitudinicio: loc.lng,
      });
    }
  }

  // Step wizard
  readonly pasoActual = signal(1);
  readonly totalPasos = 5;
  readonly pasos = signal(['Ubicación', 'Impacto', 'Vehículos', 'Entorno', 'Revisión']);
  readonly esUltimoPaso = computed(() => this.pasoActual() === this.totalPasos);

  avanzarPaso(): void {
    this.marcarStepTocado();
    if (!this.validateCurrentStep()) return;
    if (this.esUltimoPaso()) {
      this.submit();
    } else {
      this.pasoActual.update(p => p + 1);
    }
  }

  retrocederPaso(): void {
    if (this.pasoActual() > 1) {
      this.pasoActual.update(p => p - 1);
    }
  }

  irAPaso(n: number): void {
    if (n < this.pasoActual()) {
      this.pasoActual.set(n);
      return;
    }
    if (n === this.pasoActual()) return;
    this.marcarStepTocado();
    if (this.validateCurrentStep()) {
      this.pasoActual.set(n);
    }
  }

  private validateCurrentStep(): boolean {
    switch (this.pasoActual()) {
      case 1:
        return !!(
          this.form.get('latitudinicio')?.valid &&
          this.form.get('longitudinicio')?.valid &&
          this.form.get('idpais_id')?.valid &&
          this.form.get('idestado_id')?.valid &&
          this.form.get('idcondado_id')?.valid &&
          this.form.get('idciudad_id')?.valid &&
          this.form.get('idcalle_id')?.valid
        );
      case 2:
        return !!(
          this.form.get('numvehiculos')?.valid &&
          this.form.get('numheridos')?.valid &&
          this.form.get('numfallecidos')?.valid
        );
      case 3:
        if (this.registrarDetallesVehiculos()) {
          return this.vehiculosDetalles.controls.every(ctrl =>
            Object.values((ctrl as FormGroup).controls).every(c => c.valid)
          );
        }
        return true;
      case 4:
        return !!(
          this.form.get('condicion_clima')?.valid &&
          this.form.get('temperatura_f')?.valid &&
          this.form.get('humedad_porcentaje')?.valid &&
          this.form.get('visibilidad_millas')?.valid &&
          this.form.get('velocidad_viento_mph')?.valid &&
          this.form.get('idtiporeportado_id')?.valid &&
          this.form.get('amaneceranochecer')?.valid &&
          this.form.get('crepusculocivil')?.valid &&
          this.form.get('crepusculonautico')?.valid &&
          this.form.get('crepusculoastronomico')?.valid
        );
      case 5:
        return !!this.form.get('descripcion')?.valid;
      default:
        return true;
    }
  }

  private marcarStepTocado(): void {
    switch (this.pasoActual()) {
      case 1:
        ['latitudinicio', 'longitudinicio', 'idpais_id', 'idestado_id', 'idcondado_id', 'idciudad_id', 'idcalle_id'].forEach(f => this.form.get(f)?.markAsTouched());
        break;
      case 2:
        ['numvehiculos', 'numheridos', 'numfallecidos'].forEach(f => this.form.get(f)?.markAsTouched());
        break;
      case 3:
        if (this.registrarDetallesVehiculos()) {
          this.vehiculosDetalles.controls.forEach(g => {
            Object.keys((g as FormGroup).controls).forEach(k => (g as FormGroup).get(k)?.markAsTouched());
          });
        }
        break;
      case 4:
        ['condicion_clima', 'temperatura_f', 'humedad_porcentaje', 'visibilidad_millas', 'velocidad_viento_mph', 'idtiporeportado_id', 'amaneceranochecer', 'crepusculocivil', 'crepusculonautico', 'crepusculoastronomico'].forEach(f => this.form.get(f)?.markAsTouched());
        break;
      case 5:
        this.form.get('descripcion')?.markAsTouched();
        break;
    }
  }

  onCancelar(): void {
    if (this.form.dirty) {
      const confirmed = confirm('¿Está seguro de cancelar el registro? Se perderán los datos ingresados.');
      if (!confirmed) return;
    }
    this.cancelar.emit();
    this.router.navigate(['/']);
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

  private matchElementoFisicoId(raw: any): number {
    const booleans = {
      cercacruce: !!raw.cerca_cruce,
      cercasemaforo: !!raw.cerca_semaforo,
      cercaparada: !!raw.cerca_parada,
      cercaestacion: !!raw.cerca_estacion,
      cercabache: !!raw.cerca_bache,
      cercaviatren: !!raw.cerca_viatren,
    };
    const match = this.elementosFisicos().find(ef =>
      ef.cercacruce === booleans.cercacruce &&
      ef.cercasemaforo === booleans.cercasemaforo &&
      ef.cercaparada === booleans.cercaparada &&
      ef.cercaestacion === booleans.cercaestacion &&
      ef.cercabache === booleans.cercabache &&
      ef.cercaviatren === booleans.cercaviatren
    );
    return match?.idelementofisico ?? 1;
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
      idestadoclima_id: Number(raw.idestadoclima_id) || 1,
      idelementofisico_id: this.matchElementoFisicoId(raw),
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
      vehiculos_detalles: this.registrarDetallesVehiculos() ? raw.vehiculos_detalles : undefined,
    };
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const payload = this.buildPayload();

    if (this.modoEdicion() && this.editId) {
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
        this.form.patchValue({
          latitudinicio: detalle.latitudinicio,
          longitudinicio: detalle.longitudinicio,
          numvehiculos: detalle.numvehiculos ?? 1,
          numheridos: detalle.numheridos ?? 0,
          numfallecidos: detalle.numfallecidos ?? 0,
          descripcion: detalle.descripcion ?? '',
          codigopostal: detalle.codigopostal ?? '',
        });

        const sevNivel = detalle.idseveridad_id ?? detalle.severidad_nivel;
        if (sevNivel) {
          this.modoManualSeveridad.set(true);
          this.severidadManual.set(sevNivel);
        }

        this.form.patchValue({
          condicion_clima: detalle.condicion_clima ?? 'Despejado',
          temperatura_f: detalle.temperatura_f ?? 72,
          humedad_porcentaje: detalle.humedad_porcentaje ?? 50,
          visibilidad_millas: detalle.visibilidad_millas ?? 10,
          velocidad_viento_mph: detalle.velocidad_viento_mph ?? 0,
        });

        this.form.patchValue({
          amaneceranochecer: detalle.amaneceranochecer ?? 'Day',
          crepusculocivil: detalle.crepusculocivil ?? 'Day',
          crepusculonautico: detalle.crepusculonautico ?? 'Day',
          crepusculoastronomico: detalle.crepusculoastronomico ?? 'Day',
        });
        if (detalle.idperiododia_id) {
          this.form.patchValue({ idperiododia_id: detalle.idperiododia_id.toString() });
        }

        this.form.patchValue({
          cerca_cruce: detalle.cerca_cruce ?? false,
          cerca_semaforo: detalle.cerca_semaforo ?? false,
          cerca_parada: detalle.cerca_parada ?? false,
          cerca_estacion: detalle.cerca_estacion ?? false,
          cerca_bache: detalle.cerca_bache ?? false,
          cerca_viatren: detalle.cerca_viatren ?? false,
        });

        if (detalle.idelementofisico_id) {
          this.form.patchValue({ idelementofisico_id: detalle.idelementofisico_id.toString() });
        }

        if (detalle.idestadoclima_id) {
          this.form.patchValue({ idestadoclima_id: detalle.idestadoclima_id.toString() });
        }

        this.form.patchValue({
          estadosobriedad: detalle.estadosobriedad ?? true,
          nivelatencion: detalle.nivelatencion ?? true,
          condicionfisica: detalle.condicionfisica ?? true,
          usoseguridad: detalle.usoseguridad ?? true,
        });

        this.form.patchValue({
          codigoaeropuerto: detalle.codigoaeropuerto ?? 'KJFK',
          zonahoraria: detalle.zonahoraria ?? 'US/Eastern',
        });

        if (detalle.idtiporeportado_id) {
          this.form.patchValue({ idtiporeportado_id: detalle.idtiporeportado_id.toString() });
        }

        const hasDirIds = detalle.idpais_id && detalle.idestado_id &&
                          detalle.idcondado_id && detalle.idciudad_id && detalle.idcalle_id;
        if (hasDirIds) {
          this.poblarCascadaConIds(detalle);
        } else if (detalle.latitudinicio && detalle.longitudinicio) {
          this.resolverUbicacionCascada(detalle.latitudinicio, detalle.longitudinicio);
        }

        if (detalle.vehiculos_detalles && detalle.vehiculos_detalles.length > 0) {
          this.registrarDetallesVehiculos.set(true);
          this.vehiculosDetalles.clear();
          detalle.vehiculos_detalles.forEach((v: any) => {
            this.vehiculosDetalles.push(this.crearVehiculoFormGroup(v));
          });
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

  private async poblarCascadaConIds(detalle: any): Promise<void> {
    this.resolviendoDireccion.set(true);
    this.estadoResolucion.set('Cargando datos de ubicación guardados...');

    const pid = (v: any): number | null => {
      const n = Number(v);
      return !isNaN(n) && v !== null && v !== '' && v !== undefined ? n : null;
    };

    try {
      const paisId = pid(detalle.idpais_id);
      const estadoId = pid(detalle.idestado_id);
      const condadoId = pid(detalle.idcondado_id);
      const ciudadId = pid(detalle.idciudad_id);
      const calleId = pid(detalle.idcalle_id);

      // 1. Paises
      const allPaises = await firstValueFrom(this.accidenteService.getPaises());
      this.paises.set(allPaises);

      let matchPais = paisId !== null ? allPaises.find(p => p.idpais === paisId) : undefined;
      if (!matchPais && allPaises.length > 0) {
        matchPais = allPaises[0];
      }

      if (matchPais) {
        this.form.get('idpais_id')?.setValue(matchPais.idpais.toString(), { emitEvent: false });

        // 2. Estados
        const filtEstados = await firstValueFrom(this.accidenteService.getEstados(matchPais.pais));
        this.estados.set(filtEstados);
        this.form.get('idestado_id')?.enable({ emitEvent: false });

        let matchEstado = estadoId !== null ? filtEstados.find(e => e.idestado === estadoId) : undefined;
        if (matchEstado) {
          this.form.get('idestado_id')?.setValue(matchEstado.idestado.toString(), { emitEvent: false });

          // 3. Condados
          const filtCondados = await firstValueFrom(this.accidenteService.getCondados(matchEstado.estado));
          this.condados.set(filtCondados);
          this.form.get('idcondado_id')?.enable({ emitEvent: false });

          let matchCondado = condadoId !== null ? filtCondados.find(c => c.idcondado === condadoId) : undefined;
          if (matchCondado) {
            this.form.get('idcondado_id')?.setValue(matchCondado.idcondado.toString(), { emitEvent: false });

            // 4. Ciudades
            const filtCiudades = await firstValueFrom(this.accidenteService.getCiudades(matchCondado.condado));
            this.ciudades.set(filtCiudades);
            this.form.get('idciudad_id')?.enable({ emitEvent: false });

            let matchCiudad = ciudadId !== null ? filtCiudades.find(c => c.idciudad === ciudadId) : undefined;
            if (matchCiudad) {
              this.form.get('idciudad_id')?.setValue(matchCiudad.idciudad.toString(), { emitEvent: false });

              // 5. Calles
              const filtCalles = await firstValueFrom(this.accidenteService.getCalles(matchCiudad.ciudad));
              this.calles.set(filtCalles);
              this.form.get('idcalle_id')?.enable({ emitEvent: false });

              let matchCalle = calleId !== null ? filtCalles.find(c => c.idcalle === calleId) : undefined;
              if (matchCalle) {
                this.form.get('idcalle_id')?.setValue(matchCalle.idcalle.toString(), { emitEvent: false });
              }
            }
          }
        }
      }

      this.estadoResolucion.set('¡Ubicación cargada correctamente!');
      setTimeout(() => this.resolviendoDireccion.set(false), 1200);

    } catch (error) {
      console.error(error);
      this.resolviendoDireccion.set(false);
      if (detalle.latitudinicio && detalle.longitudinicio) {
        this.resolverUbicacionCascada(detalle.latitudinicio, detalle.longitudinicio);
      }
    }
  }

  numVal(field: string): number {
    return Number(this.form.get(field)?.value) || 0;
  }

  getPeriodLabel(): string {
    const v = this.form.get('amaneceranochecer')?.value;
    if (v === 'Day') return 'Día';
    if (v === 'Night') return 'Noche';
    return '—';
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

  abrirModalRevision(): void {
    this.marcarStepTocado();
    if (!this.validateCurrentStep()) return;
    this.mostrarModalRevision.set(true);
  }

  cerrarModalRevision(): void {
    this.mostrarModalRevision.set(false);
  }

  confirmarYEnviar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.mostrarModalRevision.set(false);
    this.submit();
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
      const countryCode = (address.country_code || '').toUpperCase();
      const paisName = address.country || '';
      const estadoName = address.state || '';
      const condadoName = address.county || address.state_district || '';
      const ciudadName = address.city || address.town || address.village || address.suburb || '';
      const calleName = address.road || address.pedestrian || '';
      const codigoPostal = address.postcode || '';

      if (codigoPostal) {
        this.form.patchValue({ codigopostal: codigoPostal });
      }

      this.estadoResolucion.set('Cargando base de datos de países...');

      // 1. Resolve Pais
      const allPaises = await firstValueFrom(this.accidenteService.getPaises());
      this.paises.set(allPaises);

      let matchedPais = allPaises.find(p => p.pais === countryCode || this.stringsMatchSmart(p.pais, paisName));
      if (!matchedPais && countryCode) {
        matchedPais = allPaises.find(p => this.stringsMatchSmart(p.pais, countryCode));
      }
      if (!matchedPais && allPaises.length > 0) {
        matchedPais = allPaises[0];
      }

      if (!matchedPais) {
        this.estadoResolucion.set('País no encontrado en el catálogo.');
        setTimeout(() => this.resolviendoDireccion.set(false), 1500);
        return;
      }

      this.form.get('idpais_id')?.setValue(matchedPais.idpais.toString(), { emitEvent: false });
      this.estadoResolucion.set(`País identificado: ${matchedPais.pais}. Buscando estado...`);

      // 2. Resolve Estado
      const filtEstados = await firstValueFrom(this.accidenteService.getEstados(matchedPais.pais));
      this.estados.set(filtEstados);

      const mappedEstadoQuery = this.mapStateName(estadoName);
      let matchedEstado = filtEstados.find(e => this.stringsMatchSmart(e.estado, mappedEstadoQuery) || this.stringsMatchSmart(e.estado, estadoName));

      if (!matchedEstado) {
        this.resetLocationCascades(1);
        this.estadoResolucion.set('Estado no encontrado. Complete manualmente.');
        setTimeout(() => this.resolviendoDireccion.set(false), 1500);
        return;
      }

      this.form.get('idestado_id')?.setValue(matchedEstado.idestado.toString(), { emitEvent: false });
      this.form.get('idestado_id')?.enable({ emitEvent: false });
      this.estadoResolucion.set(`Estado identificado: ${matchedEstado.estado}. Buscando condado...`);

      // 3. Resolve Condado
      const filtCondados = await firstValueFrom(this.accidenteService.getCondados(matchedEstado.estado));
      this.condados.set(filtCondados);

      let matchedCondado = filtCondados.find(c => this.stringsMatchSmart(c.condado, condadoName));
      if (!matchedCondado && !condadoName && filtCondados.length > 0) {
        matchedCondado = filtCondados[0];
      }

      if (!matchedCondado) {
        this.resetLocationCascades(2);
        this.estadoResolucion.set('Condado no encontrado. Complete manualmente.');
        setTimeout(() => this.resolviendoDireccion.set(false), 1500);
        return;
      }

      this.form.get('idcondado_id')?.setValue(matchedCondado.idcondado.toString(), { emitEvent: false });
      this.form.get('idcondado_id')?.enable({ emitEvent: false });
      this.estadoResolucion.set(`Condado identificado: ${matchedCondado.condado}. Buscando ciudad...`);

      // 4. Resolve Ciudad
      const filtCiudades = await firstValueFrom(this.accidenteService.getCiudades(matchedCondado.condado));
      this.ciudades.set(filtCiudades);

      let matchedCiudad = filtCiudades.find(c => this.stringsMatchSmart(c.ciudad, ciudadName));
      if (!matchedCiudad && !ciudadName && filtCiudades.length > 0) {
        matchedCiudad = filtCiudades[0];
      }

      if (!matchedCiudad) {
        this.resetLocationCascades(3);
        this.estadoResolucion.set('Ciudad no encontrada. Complete manualmente.');
        setTimeout(() => this.resolviendoDireccion.set(false), 1500);
        return;
      }

      this.form.get('idciudad_id')?.setValue(matchedCiudad.idciudad.toString(), { emitEvent: false });
      this.form.get('idciudad_id')?.enable({ emitEvent: false });
      this.estadoResolucion.set(`Ciudad identificada: ${matchedCiudad.ciudad}. Buscando calle...`);

      // 5. Resolve Calle
      const filtCalles = await firstValueFrom(this.accidenteService.getCalles(matchedCiudad.ciudad));
      this.calles.set(filtCalles);

      let matchedCalle = filtCalles.find(c => this.stringsMatchSmart(c.calle, calleName));

      if (matchedCalle) {
        this.form.get('idcalle_id')?.setValue(matchedCalle.idcalle.toString(), { emitEvent: false });
        this.form.get('idcalle_id')?.enable({ emitEvent: false });
        this.estadoResolucion.set('¡Ubicación resuelta con éxito hasta nivel calle!');
      } else {
        this.form.get('idcalle_id')?.setValue('', { emitEvent: false });
        this.form.get('idcalle_id')?.enable({ emitEvent: false });
        this.estadoResolucion.set('Calle no encontrada. Seleccione una calle del listado.');
      }

      setTimeout(() => {
        this.resolviendoDireccion.set(false);
      }, 1500);

    } catch (error) {
      console.error(error);
      this.finalizarResolucion('Error al resolver la cascada de ubicación.');
    }
  }

  private mapStateName(stateName: string): string {
    if (!stateName) return '';
    const norm = stateName.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
    const STATE_MAP: Record<string, string> = {
      'pichincha': 'PI',
      'provincia de pichincha': 'PI',
      'guayas': 'GY',
      'provincia del guayas': 'GY',
      'texas': 'TX',
      'alabama': 'AL',
      'minnesota': 'MN',
      'virginia': 'VA',
      'georgia': 'GA',
      'south carolina': 'SC',
      'carolina del sur': 'SC'
    };
    return STATE_MAP[norm] || stateName;
  }

  private stringsMatchSmart(dbStr: string, geoStr: string): boolean {
    if (!dbStr || !geoStr) return false;
    const clean = (s: string) => s.normalize("NFD")
                                   .replace(/[\u0300-\u036f]/g, "")
                                   .toLowerCase()
                                   .replace(/[^a-z0-9\s]/g, "")
                                   .replace(/\b(canton|distrito|metropolitano|provincia|estado|de|del|la|el|los|las)\b/g, "")
                                   .trim();
    const c1 = clean(dbStr);
    const c2 = clean(geoStr);
    if (!c1 || !c2) return false;
    if (c1 === c2 || c1.includes(c2) || c2.includes(c1)) return true;
    const tokens1 = c1.split(/\s+/).filter(t => t.length >= 3);
    const tokens2 = c2.split(/\s+/).filter(t => t.length >= 3);
    return tokens1.some(t => tokens2.includes(t));
  }

  private finalizarResolucion(msg: string): void {
    this.estadoResolucion.set(msg);
    setTimeout(() => {
      this.resolviendoDireccion.set(false);
    }, 2500);
  }
}

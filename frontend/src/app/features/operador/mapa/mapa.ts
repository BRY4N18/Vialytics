import {
  Component,
  OnInit,
  OnDestroy,
  AfterViewInit,
  input,
  output,
  effect,
  signal,
  inject,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { AccidenteService } from '../../../core/services/accidente.service';
import { AccidenteMapa } from '../../../core/models/accidente.model';
import { AuthService } from '../../../core/services/auth.service';

declare const L: any;

@Component({
  selector: 'app-mapa',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './mapa.html',
  styleUrl: './mapa.css',
})
export class MapaComponent implements OnInit, AfterViewInit, OnDestroy {
  refrescarTrigger = input<number>(0);
  filtros = input<{
    severidad?: number;
    estado?: string;
    fecha_inicio?: string;
    fecha_fin?: string;
  }>({});
  modoRegistro = input<boolean>(false);
  selectedAccidenteId = input<string | null>(null);

  // Outputs
  accidenteSeleccionado = output<AccidenteMapa>();
  ubicacionSeleccionada = output<{ lat: number; lng: number }>();

  private readonly accidenteService = inject(AccidenteService);
  private readonly authService = inject(AuthService);

  private map: any = null;
  private markersLayer: any = null;
  private locationMarker: any = null;
  private initialBoundsSet = false;
  private renderedMarkers: Record<string, any> = {};

  readonly cargando = signal(false);
  readonly error = signal<string | null>(null);
  readonly totalAccidentes = signal(0);
  readonly modoUbicacion = signal(false);

  private readonly SEVERITY_COLORS: Record<number, string> = {
    1: '#10B981',
    2: '#F59E0B',
    3: '#EF4444',
    4: '#7C3AED',
  };

  constructor() {
    // React to refrescarTrigger changes
    effect(() => {
      const trigger = this.refrescarTrigger();
      if (this.map && trigger >= 0) {
        this.cargarAccidentes();
      }
    });


    // React to filtros changes
    effect(() => {
      const f = this.filtros();
      if (this.map) {
        this.initialBoundsSet = false;
        this.cargarAccidentes();
      }
    });

    // React to modoRegistro changes
    effect(() => {
      const modo = this.modoRegistro();
      if (!modo) {
        this.modoUbicacion.set(false);
        this.removeLocationMarker();
      }
    });

    // React to selectedAccidenteId changes to focus Leaflet camera
    effect(() => {
      const id = this.selectedAccidenteId();
      if (this.map && id) {
        this.enfocarAccidente(id);
      }
    });
  }

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    this.initMap();
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
  }

  private initMap(): void {
    if (!this.isLeafletAvailable()) {
      console.error('Leaflet no está disponible. Verifica que el CDN esté cargado.');
      this.error.set('Error: Librería de mapas no disponible');
      return;
    }

    this.map = L.map('mapa-principal', {
      center: [-1.8312, -78.1834],
      zoom: 7,
      zoomControl: false,
      attributionControl: false,
    });

    // Dark tile layer
    L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      {
        attribution: '© OpenStreetMap © CARTO',
        subdomains: 'abcd',
        maxZoom: 19,
      }
    ).addTo(this.map);

    // Custom zoom control
    L.control.zoom({ position: 'bottomright' }).addTo(this.map);

    // Attribution
    L.control.attribution({ position: 'bottomleft', prefix: 'SGA © 2025' }).addTo(this.map);

    // Markers layer group
    this.markersLayer = L.layerGroup().addTo(this.map);

    // Click handler for location selection
    this.map.on('click', (e: any) => {
      if (this.modoUbicacion()) {
        const { lat, lng } = e.latlng;
        this.setLocationMarker(lat, lng);
        this.ubicacionSeleccionada.emit({ lat, lng });
      }
    });

    this.cargarAccidentes();
  }

  private isLeafletAvailable(): boolean {
    try {
      return typeof L !== 'undefined';
    } catch {
      return false;
    }
  }

  cargarAccidentes(): void {
    if (!this.map) return;
    this.cargando.set(true);
    this.error.set(null);

    const params = {
      ...this.filtros(),
      solo_ultima_semana: !this.authService.isLoggedIn()
    };

    this.accidenteService.getAccidentesMapa(params).subscribe({
      next: (accidentes) => {
        this.renderMarkers(accidentes);
        this.totalAccidentes.set(accidentes.length);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err.message || 'Error cargando accidentes');
        this.cargando.set(false);
      },
    });
  }

  private renderMarkers(accidentes: AccidenteMapa[]): void {
    if (!this.markersLayer) return;
    this.markersLayer.clearLayers();
    this.renderedMarkers = {};

    if (accidentes.length > 0 && !this.initialBoundsSet) {
      const bounds = L.latLngBounds(accidentes.map((acc) => [acc.latitudinicio, acc.longitudinicio]));
      this.map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
      this.initialBoundsSet = true;
    }

    accidentes.forEach((acc) => {
      const color = this.SEVERITY_COLORS[acc.severidad_nivel] || '#6B7280';

      const circleMarker = L.circleMarker(
        [acc.latitudinicio, acc.longitudinicio],
        {
          radius: 10 + acc.numheridos * 0.5,
          fillColor: color,
          color: '#ffffff',
          weight: 2,
          opacity: 0.9,
          fillOpacity: 0.85,
        }
      );

      // Popup
      const popupContent = `
        <div class="sga-popup">
          <div class="sga-popup-header" style="border-left: 4px solid ${color};">
            <strong>${(acc.calle_nombre && acc.calle_nombre !== 'Ubicación Registrada') ? acc.calle_nombre : 'Sin registrar'}</strong>
            <span class="sga-popup-ciudad">${(acc.ciudad_nombre && acc.ciudad_nombre !== 'Ubicación Registrada') ? acc.ciudad_nombre : ''}</span>
          </div>
          <div class="sga-popup-body">
            <div class="sga-popup-row">
              <span>Estado:</span><strong>${acc.estado_actual}</strong>
            </div>
            <div class="sga-popup-row">
              <span>Heridos:</span><strong style="color:#F59E0B">${acc.numheridos}</strong>
            </div>
            <div class="sga-popup-row">
              <span>Fallecidos:</span><strong style="color:#EF4444">${acc.numfallecidos}</strong>
            </div>
          </div>
          <div class="sga-popup-footer">${acc.descripcion?.substring(0, 80) || ''}...</div>
        </div>
      `;

      circleMarker.bindPopup(popupContent, { maxWidth: 260 });

      circleMarker.on('click', () => {
        if (!this.modoUbicacion()) {
          this.accidenteSeleccionado.emit(acc);
        }
      });

      // Pulse animation for active accidents
      if (acc.estado_actual === 'ACTIVO' || acc.estado_actual === 'EN_ATENCION') {
        const pulseMarker = L.circleMarker(
          [acc.latitudinicio, acc.longitudinicio],
          {
            radius: 18,
            fillColor: color,
            color: color,
            weight: 1,
            opacity: 0.3,
            fillOpacity: 0.1,
          }
        );
        this.markersLayer.addLayer(pulseMarker);
      }

      this.markersLayer.addLayer(circleMarker);
      this.renderedMarkers[acc.idaccidente] = circleMarker;
    });
  }

  private enfocarAccidente(id: string): void {
    const marker = this.renderedMarkers[id];
    if (marker) {
      const latlng = marker.getLatLng();
      this.map.flyTo(latlng, 15, { animate: true, duration: 1.5 });
      setTimeout(() => marker.openPopup(), 600);
    } else {
      // Si no está renderizado en el mapa actual (por límites o filtros), consultamos detalles para enfocar temporalmente
      this.accidenteService.getAccidenteDetalle(id).subscribe({
        next: (acc) => {
          if (acc && this.map) {
            const latlng = [acc.latitudinicio, acc.longitudinicio];
            this.map.flyTo(latlng, 15, { animate: true, duration: 1.5 });

            const color = this.SEVERITY_COLORS[acc.severidad_nivel] || '#6B7280';
            const tempMarker = L.circleMarker(latlng, {
              radius: 12,
              fillColor: color,
              color: '#ffffff',
              weight: 3,
              opacity: 0.95,
              fillOpacity: 0.9,
            }).addTo(this.markersLayer);

            const popupContent = `
              <div class="sga-popup">
                <div class="sga-popup-header" style="border-left: 4px solid ${color};">
                  <strong>${(acc.calle_nombre && acc.calle_nombre !== 'Ubicación Registrada') ? acc.calle_nombre : 'Sin registrar'}</strong>
                  <span class="sga-popup-ciudad">${(acc.ciudad_nombre && acc.ciudad_nombre !== 'Ubicación Registrada') ? acc.ciudad_nombre : ''}</span>
                </div>
                <div class="sga-popup-body">
                  <div class="sga-popup-row">
                    <span>Estado:</span><strong>${acc.estado_actual}</strong>
                  </div>
                  <div class="sga-popup-row">
                    <span>Heridos:</span><strong style="color:#F59E0B">${acc.numheridos}</strong>
                  </div>
                  <div class="sga-popup-row">
                    <span>Fallecidos:</span><strong style="color:#EF4444">${acc.numfallecidos}</strong>
                  </div>
                </div>
                <div class="sga-popup-footer">${acc.descripcion?.substring(0, 80) || ''}...</div>
              </div>
            `;
            tempMarker.bindPopup(popupContent, { maxWidth: 260 });
            this.renderedMarkers[id] = tempMarker;
            
            setTimeout(() => tempMarker.openPopup(), 600);
          }
        }
      });
    }
  }

  toggleModoUbicacion(): void {
    const current = this.modoUbicacion();
    this.modoUbicacion.set(!current);
    if (current) {
      this.removeLocationMarker();
    }
    if (this.map) {
      this.map.getContainer().style.cursor = !current ? 'crosshair' : '';
    }
  }

  private setLocationMarker(lat: number, lng: number): void {
    this.removeLocationMarker();
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
      iconAnchor: [12, 12],
    });
    this.locationMarker = L.marker([lat, lng], { icon }).addTo(this.map);
  }

  private removeLocationMarker(): void {
    if (this.locationMarker && this.map) {
      this.map.removeLayer(this.locationMarker);
      this.locationMarker = null;
    }
    if (this.map) {
      this.map.getContainer().style.cursor = '';
    }
  }
}

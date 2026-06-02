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
import { AccidenteService } from '../../../../core/services/accidente.service';
import { AccidenteMapa } from '../../../../core/models/accidente.model';
import { AuthService } from '../../../../core/services/auth.service';

declare const L: any;

@Component({
  selector: 'app-mapa',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './mapa.html',
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

  accidenteSeleccionado = output<AccidenteMapa>();
  ubicacionSeleccionada = output<{ lat: number; lng: number }>();

  private readonly accidenteService = inject(AccidenteService);
  private readonly authService = inject(AuthService);

  private map: any = null;
  private markersLayer: any = null;
  private clusterGroup: any = null;
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

  private readonly SEVERITY_LABELS: Record<number, string> = {
    1: 'Leve',
    2: 'Moderado',
    3: 'Grave',
    4: 'Fatal',
  };

  private readonly ESTADO_LABELS: Record<string, string> = {
    ACTIVO: 'Reportado',
    EN_ATENCION: 'En Atención',
    EN_TRASLADO: 'En Traslado',
    CONTROLADO: 'Despejado',
    ARCHIVADO: 'Archivado',
    Reportado: 'Reportado',
    Asignado: 'Asignado',
    'En Escena': 'En Escena',
    Despejado: 'Despejado',
  };

  private formatearFecha(iso: string): string {
    if (!iso) return '';
    try {
      const d = new Date(iso);
      return d.toLocaleDateString('es-EC', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      });
    } catch {
      return iso;
    }
  }

  constructor() {
    effect(() => {
      const trigger = this.refrescarTrigger();
      if (this.map && trigger >= 0) {
        this.cargarAccidentes();
      }
    });

    effect(() => {
      const f = this.filtros();
      if (this.map) {
        this.initialBoundsSet = false;
        this.cargarAccidentes();
      }
    });

    effect(() => {
      const modo = this.modoRegistro();
      if (!modo) {
        this.modoUbicacion.set(false);
        this.removeLocationMarker();
      }
    });

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
      console.error('Leaflet no está disponible.');
      this.error.set('Error: Librería de mapas no disponible');
      return;
    }

    this.map = L.map('mapa-principal', {
      center: [-1.8312, -78.1834],
      zoom: 7,
      zoomControl: false,
      attributionControl: false,
    });

    L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      {
        attribution: '© OpenStreetMap © CARTO',
        subdomains: 'abcd',
        maxZoom: 19,
      }
    ).addTo(this.map);

    L.control.zoom({ position: 'bottomright' }).addTo(this.map);
    L.control.attribution({ position: 'bottomleft', prefix: 'AnalyticsVial © 2026' }).addTo(this.map);

    this.clusterGroup = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 60,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 16,
      iconCreateFunction: (cluster: any) => this.createClusterIcon(cluster),
    });
    this.map.addLayer(this.clusterGroup);

    this.markersLayer = L.layerGroup();

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
      return typeof L !== 'undefined' && typeof L.markerClusterGroup !== 'undefined';
    } catch {
      return false;
    }
  }

  cargarAccidentes(): void {
    if (!this.map) return;
    this.cargando.set(true);
    this.error.set(null);

    const isPublic = !this.authService.isLoggedIn();
    const params = {
      ...this.filtros(),
      solo_ultima_semana: isPublic,
      public: isPublic
    };

    const obs = isPublic
      ? this.accidenteService.getMapaPublico(params)
      : this.accidenteService.getAccidentesMapa(params);

    obs.subscribe({
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
    if (!this.clusterGroup) return;
    this.clusterGroup.clearLayers();
    this.markersLayer.clearLayers();
    this.renderedMarkers = {};

    if (accidentes.length > 0 && !this.initialBoundsSet) {
      const bounds = L.latLngBounds(accidentes.map((acc) => [acc.latitudinicio, acc.longitudinicio]));
      this.map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
      this.initialBoundsSet = true;
    }

    accidentes.forEach((acc) => {
      const color = this.SEVERITY_COLORS[acc.severidad_nivel] || '#6B7280';
      const severity = acc.severidad_nivel || 1;
      const size = this.getMarkerSize(acc);

      const icon = this.createSeverityIcon(severity, color, size);
      const marker = L.marker([acc.latitudinicio, acc.longitudinicio], { icon });
      (marker as any).__severidad = severity;

      const isActive = acc.estado_actual === 'Reportado' ||
        acc.estado_actual === 'Asignado' ||
        acc.estado_actual === 'En Escena' ||
        acc.estado_actual === 'ACTIVO' ||
        acc.estado_actual === 'EN_ATENCION';

      if (isActive) {
        (marker as any).__isActive = true;
      }

      const popupContent = this.buildPopupContent(acc, color);
      marker.bindPopup(popupContent, {
        maxWidth: 300,
        className: 'sga-popup-wrapper',
        closeButton: true,
      });

      marker.on('click', () => {
        if (!this.modoUbicacion()) {
          this.accidenteSeleccionado.emit(acc);
        }
      });

      if (isActive) {
        const pulse = L.circleMarker([acc.latitudinicio, acc.longitudinicio], {
          radius: size * 2.2,
          fillColor: color,
          color: color,
          weight: 1.5,
          opacity: 0.4,
          fillOpacity: 0.08,
          className: 'sga-pulse-ring',
        });
        (pulse as any)._pulseTime = Date.now();
        (pulse as any)._pulseColor = color;
        this.markersLayer.addLayer(pulse);
      }

      marker.on('mouseover', () => {
        const el = marker.getElement();
        if (el) {
          const pin = el.querySelector('.sga-marker-pin') as HTMLElement;
          if (pin) {
            pin.style.transform = 'scale(1.25)';
            pin.style.filter = `drop-shadow(0 0 12px ${color}88)`;
          }
        }
      });

      marker.on('mouseout', () => {
        const el = marker.getElement();
        if (el) {
          const pin = el.querySelector('.sga-marker-pin') as HTMLElement;
          if (pin) {
            pin.style.transform = '';
            pin.style.filter = '';
          }
        }
      });

      this.clusterGroup.addLayer(marker);
      this.renderedMarkers[acc.idaccidente] = marker;
    });

    if (this.markersLayer) {
      this.map.addLayer(this.markersLayer);
    }

    this.startPulseAnimation();
  }

  private getMarkerSize(acc: AccidenteMapa): number {
    const h = acc.numheridos || 0;
    const f = acc.numfallecidos || 0;
    const base = 28;
    const extra = Math.min(h + f * 2, 30);
    return base + extra;
  }

  private createSeverityIcon(severity: number, color: string, size: number): any {
    const num = severity;
    const scale = size / 28;
    const w = 40;
    const h = 48;
    const sw = Math.round(w * scale);
    const sh = Math.round(h * scale);

    const html = `
      <div class="sga-marker-pin" style="width:${sw}px;height:${sh}px;">
        <svg viewBox="0 0 ${w} ${h}" width="${sw}" height="${sh}" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <filter id="shadow-${num}" x="-10%" y="-10%" width="130%" height="140%">
              <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.35"/>
            </filter>
            <linearGradient id="grad-${num}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="${this.lightenColor(color, 15)}"/>
              <stop offset="100%" stop-color="${color}"/>
            </linearGradient>
          </defs>
          <path d="M20 0C9 0 0 9 0 20c0 11 20 28 20 28s20-17 20-28C40 9 31 0 20 0z"
                fill="url(#grad-${num})" filter="url(#shadow-${num})"/>
        </svg>
      </div>`;

    return L.divIcon({
      className: 'sga-divicon',
      html,
      iconSize: [sw, sh],
      iconAnchor: [sw / 2, sh],
      popupAnchor: [0, -sh],
    });
  }

  private createClusterIcon(cluster: any): any {
    const markers = cluster.getAllChildMarkers();
    const count = markers.length;

    const severityScores: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 0 };
    markers.forEach((m: any) => {
      const sev = (m as any).__severidad || 1;
      severityScores[sev] = (severityScores[sev] || 0) + 1;
    });

    let dominantSeverity = 1;
    let maxCount = 0;
    for (const [sev, cnt] of Object.entries(severityScores)) {
      if (cnt > maxCount) {
        maxCount = cnt;
        dominantSeverity = Number(sev);
      }
    }

    const color = this.SEVERITY_COLORS[dominantSeverity] || '#6B7280';
    const size = Math.min(50 + count * 3, 80);

    const html = `
      <div class="sga-cluster-icon" style="
        width:${size}px;height:${size}px;
        background:${color};
        box-shadow:0 0 0 4px ${color}22, 0 4px 16px ${color}44;
      ">
        <span>${count}</span>
      </div>`;

    return L.divIcon({
      className: 'sga-cluster-divicon',
      html,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
    });
  }

  private buildPopupContent(acc: AccidenteMapa, color: string): string {
    const isPublic = !this.authService.isLoggedIn();
    const sevLabel = this.SEVERITY_LABELS[acc.severidad_nivel] || '';
    const fechaStr = this.formatearFecha(acc.fecha_actualizacion);
    const estadoLabel = this.ESTADO_LABELS[acc.estado_actual] || acc.estado_actual;
    const calle = (acc.calle_nombre && acc.calle_nombre !== 'Ubicación Registrada') ? acc.calle_nombre : 'Sin registrar';
    const ciudad = (acc.ciudad_nombre && acc.ciudad_nombre !== 'Ubicación Registrada') ? acc.ciudad_nombre : '';

    const estadoColor = acc.estado_actual === 'Despejado' || acc.estado_actual === 'CONTROLADO' || acc.estado_actual === 'ARCHIVADO'
      ? '#10B981'
      : acc.estado_actual === 'ACTIVO' || acc.estado_actual === 'Reportado' || acc.estado_actual === 'En Escena' || acc.estado_actual === 'EN_ATENCION'
      ? '#EF4444'
      : '#F59E0B';

    return `
      <div class="sga-popup-v2">
        <div class="sga-popup-v2-header" style="background:${color}">
          <div class="sga-popup-v2-header-content">
            <div class="sga-popup-v2-sev-badge">${sevLabel}</div>
            <div class="sga-popup-v2-estado" style="background:${estadoColor}22; color:${estadoColor}">${estadoLabel}</div>
          </div>
        </div>
        <div class="sga-popup-v2-body">
          <div class="sga-popup-v2-location">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            <span><strong>${calle}</strong>${ciudad ? ', ' + ciudad : ''}</span>
          </div>
          ${fechaStr ? `
          <div class="sga-popup-v2-row">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
            <span>${fechaStr}</span>
          </div>` : ''}
          ${!isPublic ? `
          <div class="sga-popup-v2-stats">
            <div class="sga-popup-v2-stat" style="color:#F59E0B">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
              </svg>
              <span>${acc.numheridos}</span>
            </div>
            <div class="sga-popup-v2-stat" style="color:#EF4444">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>${acc.numfallecidos}</span>
            </div>
          </div>
          ${acc.descripcion ? `<div class="sga-popup-v2-desc">${acc.descripcion.substring(0, 100)}${acc.descripcion.length > 100 ? '...' : ''}</div>` : ''}
          ` : ''}
        </div>
        ${!isPublic ? `
        <div class="sga-popup-v2-footer" style="border-top-color:${color}22">
          <span>ID: ${acc.idaccidente.substring(0, 8)}</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </div>` : ''}
      </div>`;
  }

  private startPulseAnimation(): void {
    if (!this.markersLayer) return;
    this.markersLayer.eachLayer((layer: any) => {
      if (layer._pulseTime !== undefined) {
        const el = layer.getElement();
        if (el) {
          el.style.animation = 'sgaPulse 2s ease-in-out infinite';
        }
      }
    });
  }

  private enfocarAccidente(id: string): void {
    const marker = this.renderedMarkers[id];
    if (marker) {
      const latlng = marker.getLatLng();
      this.map.flyTo(latlng, 16, { animate: true, duration: 1.2 });
      setTimeout(() => marker.openPopup(), 600);

      const el = marker.getElement();
      if (el) {
        el.style.filter = `drop-shadow(0 0 20px ${this.SEVERITY_COLORS[1]}88)`;
        el.style.transition = 'filter 0.3s ease';
        el.style.zIndex = '10000';
        setTimeout(() => {
          el.style.filter = '';
          el.style.zIndex = '';
        }, 3000);
      }
    } else {
      this.accidenteService.getAccidenteDetalle(id).subscribe({
        next: (acc) => {
          if (acc && this.map) {
            const latlng: [number, number] = [acc.latitudinicio, acc.longitudinicio];
            this.map.flyTo(latlng, 16, { animate: true, duration: 1.2 });

            const color = this.SEVERITY_COLORS[acc.severidad_nivel] || '#6B7280';
            const severity = acc.severidad_nivel || 1;
            const size = this.getMarkerSize(acc);
            const icon = this.createSeverityIcon(severity, color, size);

            const tempMarker = L.marker(latlng, { icon }).addTo(this.markersLayer);
            const popupContent = this.buildPopupContent(acc, color);
            tempMarker.bindPopup(popupContent, {
              maxWidth: 300,
              className: 'sga-popup-wrapper',
            });

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

  private lightenColor(hex: string, percent: number): string {
    const num = parseInt(hex.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = Math.min(255, (num >> 16) + amt);
    const G = Math.min(255, ((num >> 8) & 0x00FF) + amt);
    const B = Math.min(255, (num & 0x0000FF) + amt);
    return `#${(1 << 24 | R << 16 | G << 8 | B).toString(16).slice(1)}`;
  }
}

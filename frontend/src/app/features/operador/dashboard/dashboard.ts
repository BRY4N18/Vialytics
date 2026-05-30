import { Component, OnInit, inject, signal, ElementRef, viewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AccidenteService } from '../../../core/services/accidente.service';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit {
  private readonly accidenteService = inject(AccidenteService);

  readonly trendCanvas = viewChild<ElementRef<HTMLCanvasElement>>('trendCanvas');
  readonly severityCanvas = viewChild<ElementRef<HTMLCanvasElement>>('severityCanvas');
  readonly statesCanvas = viewChild<ElementRef<HTMLCanvasElement>>('statesCanvas');
  readonly hourlyCanvas = viewChild<ElementRef<HTMLCanvasElement>>('hourlyCanvas');
  readonly weatherCanvas = viewChild<ElementRef<HTMLCanvasElement>>('weatherCanvas');

  readonly totalAccidentes = signal<string>('0');
  readonly severidadCritica = signal<string>('0');
  readonly distanciaPromedio = signal<string>('0.00 mi');
  readonly callesAfectadas = signal<string>('0');

  readonly cargando = signal<boolean>(true);
  readonly error = signal<string | null>(null);
  readonly ultimaActualizacion = signal<string>('');

  private charts: Chart[] = [];

  ngOnInit(): void {
    this.cargarEstadisticas();
  }

  private formatNumber(num: number): string {
    return new Intl.NumberFormat('de-DE').format(num);
  }

  cargarEstadisticas(): void {
    this.cargando.set(true);
    this.error.set(null);

    this.accidenteService.getDashboardStats().subscribe({
      next: (data) => {
        this.totalAccidentes.set(this.formatNumber(data.kpis.total_accidentes));
        this.severidadCritica.set(this.formatNumber(data.kpis.severidad_critica));
        this.distanciaPromedio.set(`${data.kpis.distancia_promedio} mi`);
        this.callesAfectadas.set(this.formatNumber(data.kpis.calles_afectadas));

        this.cargando.set(false);
        this.ultimaActualizacion.set(new Date().toLocaleString('es-EC', { dateStyle: 'medium', timeStyle: 'short' }));

        setTimeout(() => {
          this.destroyCharts();
          this.initCharts(data);
        }, 50);
      },
      error: (err) => {
        console.error(err);
        this.error.set('No se pudieron cargar las analíticas en tiempo real.');
        this.cargando.set(false);
      }
    });
  }

  refrescar(): void {
    this.cargarEstadisticas();
  }

  private destroyCharts(): void {
    this.charts.forEach(c => c.destroy());
    this.charts = [];
  }

  private initCharts(data: any): void {
    const trendCtx = this.trendCanvas()?.nativeElement.getContext('2d');
    if (trendCtx) {
      const trendGrad = trendCtx.createLinearGradient(0, 0, 0, 300);
      trendGrad.addColorStop(0, 'rgba(239, 68, 68, 0.2)');
      trendGrad.addColorStop(1, 'rgba(239, 68, 68, 0.00)');

      const labels = data.monthly_trend.map((d: any) => d.month);
      const counts = data.monthly_trend.map((d: any) => d.count);

      this.charts.push(new Chart(trendCtx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Incidentes',
            data: counts,
            borderColor: '#F43F5E',
            borderWidth: 3,
            backgroundColor: trendGrad,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#F43F5E',
            pointBorderColor: '#0b0f19',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: '#94A3B8', font: { size: 9 } }
            },
            y: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94A3B8', font: { size: 9 } }
            }
          }
        }
      }));
    }

    const severityCtx = this.severityCanvas()?.nativeElement.getContext('2d');
    if (severityCtx) {
      const sevNames = data.severity_distribution.map((d: any) => d.name);
      const sevCounts = data.severity_distribution.map((d: any) => d.count);

      this.charts.push(new Chart(severityCtx, {
        type: 'doughnut',
        data: {
          labels: sevNames,
          datasets: [{
            data: sevCounts,
            backgroundColor: [
              '#3B82F6',
              '#FBBF24',
              '#F59E0B',
              '#EF4444'
            ],
            borderWidth: 2,
            borderColor: '#111827'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                boxWidth: 10,
                color: '#CBD5E1',
                font: { size: 10, weight: 'bold' },
                padding: 14
              }
            }
          },
          cutout: '72%'
        }
      }));
    }

    const statesCtx = this.statesCanvas()?.nativeElement.getContext('2d');
    if (statesCtx) {
      const stateNames = data.top_states.map((d: any) => d.state);
      const stateCounts = data.top_states.map((d: any) => d.count);

      const colors = [
        '#E11D48', '#BE123C', '#D946EF', '#EC4899', '#FB7185',
        '#10B981', '#059669', '#3B82F6', '#6366F1', '#8B5CF6'
      ];

      this.charts.push(new Chart(statesCtx, {
        type: 'bar',
        data: {
          labels: stateNames,
          datasets: [{
            data: stateCounts,
            backgroundColor: colors,
            borderRadius: 6,
            barThickness: 16
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { display: true, color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94A3B8', font: { size: 9 } }
            },
            y: {
              grid: { display: false },
              ticks: { color: '#E2E8F0', font: { size: 10, weight: 'bold' } }
            }
          }
        }
      }));
    }

    const hourlyCtx = this.hourlyCanvas()?.nativeElement.getContext('2d');
    if (hourlyCtx) {
      const hourlyGrad = hourlyCtx.createLinearGradient(0, 0, 0, 200);
      hourlyGrad.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
      hourlyGrad.addColorStop(1, 'rgba(59, 130, 246, 0.00)');

      const hoursLabels = Array.from({ length: 24 }, (_, i) => `${i}:00`);

      this.charts.push(new Chart(hourlyCtx, {
        type: 'line',
        data: {
          labels: hoursLabels,
          datasets: [{
            label: 'Incidentes',
            data: data.hourly_distribution,
            borderColor: '#60A5FA',
            borderWidth: 2.5,
            backgroundColor: hourlyGrad,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: '#94A3B8', font: { size: 8 } }
            },
            y: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94A3B8', font: { size: 8 } }
            }
          }
        }
      }));
    }

    const weatherCtx = this.weatherCanvas()?.nativeElement.getContext('2d');
    if (weatherCtx) {
      const weatherNames = data.weather_distribution.map((d: any) => d.weather);
      const weatherCounts = data.weather_distribution.map((d: any) => d.count);

      const barColors = [
        '#0284C7', '#6366F1', '#8B5CF6', '#EC4899', '#F43F5E',
        '#F97316', '#EAB308', '#10B981', '#14B8A6'
      ];

      this.charts.push(new Chart(weatherCtx, {
        type: 'bar',
        data: {
          labels: weatherNames,
          datasets: [{
            data: weatherCounts,
            backgroundColor: barColors,
            borderRadius: 6,
            barThickness: 24
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: '#E2E8F0', font: { size: 8, weight: 'bold' } }
            },
            y: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94A3B8', font: { size: 8 } }
            }
          }
        }
      }));
    }
  }
}

import { Injectable, signal, computed, inject } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

const STORAGE_KEY_TOKEN = 'sga_token';
const STORAGE_KEY_REFRESH = 'sga_refresh';
const STORAGE_KEY_USER = 'sga_user';
const API_BASE = 'http://localhost:8080/api/v1';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly router = inject(Router);
  private readonly http = inject(HttpClient);

  readonly isLoggedIn = signal<boolean>(false);
  readonly showLoginModal = signal<boolean>(false);
  readonly userRole = signal<string>('Operador');
  readonly userFullName = signal<string>('Laura Mendoza');

  readonly userInitials = computed(() => {
    const names = this.userFullName().trim().split(/\s+/);
    if (names.length === 0 || !names[0]) return 'OP';
    if (names.length === 1) return names[0].substring(0, 2).toUpperCase();
    return (names[0][0] + names[names.length - 1][0]).toUpperCase();
  });

  constructor() {
    this.restoreSession();
  }

  async login(usuario: string, password: string): Promise<void> {
    const res = await firstValueFrom(
      this.http.post<any>(`${API_BASE}/auth/login/`, { usuario, password })
    );

    localStorage.setItem(STORAGE_KEY_TOKEN, res.access);
    if (res.refresh) {
      localStorage.setItem(STORAGE_KEY_REFRESH, res.refresh);
    }
    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify({
      usuario: res.usuario,
      nombre: res.nombre,
      rol: res.rol,
    }));

    this.userRole.set(res.rol);
    this.userFullName.set(res.nombre);
    this.isLoggedIn.set(true);
    this.showLoginModal.set(false);
    this.router.navigate(['/dashboard']);
  }

  logout(): void {
    localStorage.removeItem(STORAGE_KEY_TOKEN);
    localStorage.removeItem(STORAGE_KEY_REFRESH);
    localStorage.removeItem(STORAGE_KEY_USER);
    this.isLoggedIn.set(false);
    this.showLoginModal.set(false);
    this.userRole.set('Operador');
    this.userFullName.set('Laura Mendoza');
    this.router.navigate(['/mapa']);
  }

  getToken(): string | null {
    return localStorage.getItem(STORAGE_KEY_TOKEN);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(STORAGE_KEY_REFRESH);
  }

  async refreshToken(): Promise<string | null> {
    const refresh = this.getRefreshToken();
    if (!refresh) return null;
    try {
      const res = await firstValueFrom(
        this.http.post<any>(`${API_BASE}/auth/refresh/`, { refresh })
      );
      localStorage.setItem(STORAGE_KEY_TOKEN, res.access);
      return res.access;
    } catch {
      this.logout();
      return null;
    }
  }

  private restoreSession(): void {
    const token = localStorage.getItem(STORAGE_KEY_TOKEN);
    const userData = localStorage.getItem(STORAGE_KEY_USER);

    if (token && userData) {
      try {
        const user = JSON.parse(userData);
        this.userRole.set(user.rol || 'Operador');
        this.userFullName.set(user.nombre || 'Laura Mendoza');
        this.isLoggedIn.set(true);

        this.verifyToken(token).catch(() => this.logout());
      } catch {
        this.logout();
      }
    }
  }

  private async verifyToken(token: string): Promise<void> {
    await firstValueFrom(
      this.http.get<any>(`${API_BASE}/auth/verify/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
    );
  }
}

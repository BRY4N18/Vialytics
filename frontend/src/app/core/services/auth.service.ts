import { Injectable, signal, computed, inject } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly router = inject(Router);

  // By default, the citizen is anonymous and NOT logged in.
  readonly isLoggedIn = signal<boolean>(false);

  // Control visibility of high-fidelity glassmorphism login modal
  readonly showLoginModal = signal<boolean>(false);

  // Simulated active operator state
  readonly userRole = signal<string>('Operador');
  readonly userFullName = signal<string>('Laura Mendoza');

  // Compute initials dynamically (e.g. "Laura Mendoza" -> "LM")
  readonly userInitials = computed(() => {
    const names = this.userFullName().trim().split(/\s+/);
    if (names.length === 0 || !names[0]) return 'OP';
    if (names.length === 1) return names[0].substring(0, 2).toUpperCase();
    return (names[0][0] + names[names.length - 1][0]).toUpperCase();
  });

  login(customRole?: string, customFullName?: string): void {
    // If customized details are passed, populate them
    if (customRole) {
      this.userRole.set(customRole);
    } else {
      this.userRole.set('Operador');
    }

    if (customFullName) {
      this.userFullName.set(customFullName);
    } else {
      this.userFullName.set('Laura Mendoza');
    }

    this.isLoggedIn.set(true);
    this.showLoginModal.set(false);
    this.router.navigate(['/dashboard']);
  }

  logout(): void {
    this.isLoggedIn.set(false);
    this.showLoginModal.set(false);
    this.router.navigate(['/mapa']);
  }
}

import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const analistaGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn() && authService.userRole() === 'Consumidor Analítico') {
    return true;
  }

  if (authService.isLoggedIn()) {
    router.navigate(['/dashboard']);
  } else {
    router.navigate(['/mapa']);
  }
  return false;
};

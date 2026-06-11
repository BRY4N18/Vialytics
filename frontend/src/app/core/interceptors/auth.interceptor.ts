import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { throwError, catchError, switchMap, from } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  const token = localStorage.getItem('sga_token');
  let clonedReq = req;

  if (token) {
    clonedReq = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }

  return next(clonedReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && token && !req.url.includes('auth/refresh')) {
        const refresh = localStorage.getItem('sga_refresh');
        if (refresh) {
          return from(
            fetch('http://localhost:8080/api/v1/auth/refresh/', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ refresh })
            }).then(res => res.json())
          ).pipe(
            switchMap((data: any) => {
              if (data.access) {
                localStorage.setItem('sga_token', data.access);
                const retryReq = req.clone({
                  setHeaders: { Authorization: `Bearer ${data.access}` }
                });
                return next(retryReq);
              }
              localStorage.clear();
              router.navigate(['/mapa']);
              return throwError(() => new Error('Sesión expirada'));
            }),
            catchError(() => {
              localStorage.clear();
              router.navigate(['/mapa']);
              return throwError(() => new Error('Sesión expirada'));
            })
          );
        }
        localStorage.clear();
        router.navigate(['/mapa']);
      }
      return throwError(() => error);
    })
  );
};

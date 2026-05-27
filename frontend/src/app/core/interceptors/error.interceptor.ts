import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { throwError, catchError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'Error desconocido';
      if (error.error instanceof ErrorEvent) {
        errorMessage = `Error de red: ${error.error.message}`;
      } else {
        switch (error.status) {
          case 400:
            errorMessage = 'Solicitud inválida';
            break;
          case 401:
            errorMessage = 'No autorizado';
            break;
          case 403:
            errorMessage = 'Acceso denegado';
            break;
          case 404:
            errorMessage = 'Recurso no encontrado';
            break;
          case 500:
            errorMessage = 'Error interno del servidor';
            break;
          default:
            errorMessage = `Error ${error.status}: ${error.statusText}`;
        }
      }
      console.error('[ErrorInterceptor]', errorMessage, error);
      return throwError(() => new Error(errorMessage));
    })
  );
};

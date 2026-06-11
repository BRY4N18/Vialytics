import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { of, tap } from 'rxjs';

interface CacheEntry {
  response: HttpResponse<unknown>;
  timestamp: number;
}

const CATALOG_PATTERNS = [
  '/tipos-reportado/',
  '/severidades/',
  '/tipos-estado/',
  '/paises/',
  '/estados/',
  '/condados/',
  '/ciudades/',
  '/calles/',
  '/climas/',
  '/elementos-fisicos/',
  '/periodos-dias/',
];

const CATALOG_TTL = 300_000;

const cache = new Map<string, CacheEntry>();

function isCatalogUrl(url: string): boolean {
  return CATALOG_PATTERNS.some(pattern => url.includes(pattern));
}

export const cacheInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.method !== 'GET' || !isCatalogUrl(req.url)) {
    return next(req);
  }

  const cached = cache.get(req.url);
  if (cached && Date.now() - cached.timestamp < CATALOG_TTL) {
    return of(cached.response.clone());
  }

  return next(req).pipe(
    tap(event => {
      if (event instanceof HttpResponse) {
        cache.set(req.url, {
          response: event.clone(),
          timestamp: Date.now(),
        });
      }
    })
  );
};

import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();

  let clonedRequest = req;

  // Clone the request to add the authentication header
  if (token) {
    clonedRequest = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  // Pass it on to the next interceptor in the chain
  return next(clonedRequest).pipe(
    catchError((error) => {
      // Handle 401 Unauthorized globally
      if (error.status === 401) {
        authService.logout();
      }
      return throwError(() => error);
    })
  );
};

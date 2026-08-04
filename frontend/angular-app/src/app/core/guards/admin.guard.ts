import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { jwtDecode } from 'jwt-decode';

export const adminGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  const token = authService.getToken();
  if (!token) {
    return router.parseUrl('/login');
  }

  try {
    const payload: any = jwtDecode(token);
    if (payload.role === 'admin') {
      return true;
    }
  } catch (e) {
    console.error('Invalid token', e);
  }

  return router.parseUrl('/profile'); // Redirect to profile if not admin
};

import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login.component';
import { RegisterComponent } from './features/auth/register/register.component';
import { VerifyEmailComponent } from './features/auth/verify-email/verify-email.component';
import { ChatComponent } from './features/chat/chat.component';

import { OnboardingComponent } from './features/onboarding/onboarding.component';
import { ProfileComponent } from './features/profile/profile.component';
import { inject } from '@angular/core';
import { AuthService } from './core/services/auth.service';
import { Router } from '@angular/router';
import { adminGuard } from './core/guards/admin.guard';

// Auth Guard (functional approach for Angular 15+)
const authGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.getToken()) {
    return true;
  }
  return router.parseUrl('/login');
};

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'verify-email', component: VerifyEmailComponent },
  { path: 'onboarding', component: OnboardingComponent, canActivate: [authGuard] },

  { path: 'profile', component: ProfileComponent, canActivate: [authGuard] },
  { path: 'chat', component: ChatComponent, canActivate: [authGuard] },
  { 
    path: 'admin', 
    loadComponent: () => import('./features/admin/admin.component').then(m => m.AdminComponent),
    canActivate: [adminGuard] 
  },
  { path: '**', redirectTo: '/login' }
];

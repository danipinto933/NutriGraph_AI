import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Router } from '@angular/router';

export interface User {
  email: string;
  first_name: string;
  sex?: string;
  weight_kg?: number;
  height_cm?: number;
  age_years?: number;
  activity_factor?: number;
  intolerances?: string[];
  bmi?: number;
  bmr?: number;
  tdee?: number;
  diet_type?: string;
  role?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly apiUrl = `${environment.apiUrl}/users`;
  
  // Signals for reactive state
  public currentUser = signal<User | null>(null);
  public isLoading = signal<boolean>(false);
  public error = signal<string | null>(null);
  
  // Computed signal to check if authenticated
  public isAuthenticated = computed(() => this.currentUser() !== null);
  public isAdmin = computed(() => this.currentUser()?.role === 'admin');

  constructor(private http: HttpClient, private router: Router) {
    this.loadUserFromToken();
  }

  // --- Login ---
  login(credentials: any): Observable<TokenResponse> {
    this.isLoading.set(true);
    this.error.set(null);
    
    const payload = {
      email: credentials.email,
      password: credentials.password
    };
    
    return this.http.post<TokenResponse>(`${this.apiUrl}/login`, payload).pipe(
      tap(response => {
        this.setToken(response.access_token);
        this.fetchCurrentUser().subscribe();
        this.isLoading.set(false);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.error || err.error?.detail || err.error?.message || 'Login failed');
        return throwError(() => err);
      })
    );
  }

  // --- Register ---
  register(userData: any): Observable<any> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.post(`${this.apiUrl}/register`, userData).pipe(
      tap(() => this.isLoading.set(false)),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.error || err.error?.detail || 'Error en el registro');
        throw err;
      })
    );
  }

  submitOnboarding(data: any): Observable<any> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.post(`${this.apiUrl}/onboarding`, data).pipe(
      tap(() => {
        this.isLoading.set(false);
        // Refresh the current user state after onboarding
        this.fetchCurrentUser().subscribe();
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al guardar datos de onboarding');
        throw err;
      })
    );
  }

  updateProfile(data: any): Observable<any> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.put(`${this.apiUrl}/profile`, data).pipe(
      tap(() => {
        this.isLoading.set(false);
        // Refresh the current user state
        this.fetchCurrentUser().subscribe();
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al actualizar perfil');
        throw err;
      })
    );
  }

  // --- Logout ---
  logout(): void {
    localStorage.removeItem('token');
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  // --- Fetch current user info ---
  fetchCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/me`).pipe(
      tap(user => this.currentUser.set(user)),
      catchError(err => {
        this.logout();
        return throwError(() => err);
      })
    );
  }

  // --- Token Management ---
  private setToken(token: string): void {
    localStorage.setItem('token', token);
  }

  public getToken(): string | null {
    return localStorage.getItem('token');
  }

  private loadUserFromToken(): void {
    const token = this.getToken();
    if (token) {
      // Just check if it exists and fetch user profile to validate
      this.fetchCurrentUser().subscribe({
        error: () => console.warn('Token expired or invalid on startup')
      });
    }
  }
}

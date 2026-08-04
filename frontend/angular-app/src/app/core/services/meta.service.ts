import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MetaService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl + '/meta';

  getDiets(): Observable<string[]> {
    return this.http.get<string[]>(`${this.apiUrl}/diets`);
  }

  getAllergens(): Observable<string[]> {
    return this.http.get<string[]>(`${this.apiUrl}/allergens`);
  }
}

import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, catchError, throwError, BehaviorSubject } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User } from './auth.service';

export interface DietType {
  name: string;
}

export interface Allergen {
  name: string;
}

export interface Ingredient {
  name: string;
  calorias_100g: number;
  proteinas_100g: number;
  grasas_100g: number;
  carbohidratos_100g: number;
  origen: string;
  categoria: string;
  allergens?: string[];
}

export interface RecipeIngredient {
  name: string;
  grams: number;
}

export interface Recipe {
  id?: string;
  name: string;
  description: string;
  ingredients: RecipeIngredient[];
  calories?: number;
  protein_g?: number;
  fat_g?: number;
  carbs_g?: number;
}

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private readonly apiUrl = `${environment.apiUrl}/admin/users`;
  private readonly dietsApiUrl = `${environment.apiUrl}/admin/diet-types`;
  private readonly allergensApiUrl = `${environment.apiUrl}/admin/allergens`;
  private readonly ingredientsApiUrl = `${environment.apiUrl}/admin/ingredients`;
  private readonly recipesApiUrl = `${environment.apiUrl}/admin/recipes`;
  
  private usersSubject = new BehaviorSubject<User[]>([]);
  public users$ = this.usersSubject.asObservable();
  
  private dietsSubject = new BehaviorSubject<DietType[]>([]);
  public diets$ = this.dietsSubject.asObservable();
  
  private allergensSubject = new BehaviorSubject<Allergen[]>([]);
  public allergens$ = this.allergensSubject.asObservable();

  private ingredientsSubject = new BehaviorSubject<Ingredient[]>([]);
  public ingredients$ = this.ingredientsSubject.asObservable();

  private recipesSubject = new BehaviorSubject<Recipe[]>([]);
  public recipes$ = this.recipesSubject.asObservable();


  
  public isLoading = signal<boolean>(false);
  public error = signal<string | null>(null);

  constructor(private http: HttpClient) {}

  fetchUsers(): Observable<User[]> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.get<User[]>(this.apiUrl).pipe(
      tap(users => {
        this.usersSubject.next(users);
        this.isLoading.set(false);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al cargar usuarios');
        return throwError(() => err);
      })
    );
  }

  createUser(userData: any): Observable<User> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.post<User>(this.apiUrl, userData).pipe(
      tap(newUser => {
        this.isLoading.set(false);
        const current = this.usersSubject.value;
        this.usersSubject.next([...current, newUser]);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al crear usuario');
        return throwError(() => err);
      })
    );
  }

  updateUser(email: string, userData: any): Observable<User> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.put<User>(`${this.apiUrl}/${email}`, userData).pipe(
      tap(updatedUser => {
        this.isLoading.set(false);
        const current = this.usersSubject.value;
        this.usersSubject.next(
          current.map(u => u.email === updatedUser.email ? updatedUser : u)
        );
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al actualizar usuario');
        return throwError(() => err);
      })
    );
  }

  deleteUser(email: string): Observable<void> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.delete<void>(`${this.apiUrl}/${email}`).pipe(
      tap(() => {
        this.isLoading.set(false);
        const current = this.usersSubject.value;
        this.usersSubject.next(current.filter(u => u.email !== email));
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al eliminar usuario');
        return throwError(() => err);
      })
    );
  }

  fetchDietTypes(): Observable<DietType[]> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.get<DietType[]>(this.dietsApiUrl).pipe(
      tap(diets => {
        this.dietsSubject.next(diets);
        this.isLoading.set(false);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al cargar tipos de dieta');
        return throwError(() => err);
      })
    );
  }

  createDietType(dietData: { name: string }): Observable<DietType> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.post<DietType>(this.dietsApiUrl, dietData).pipe(
      tap(newDiet => {
        this.isLoading.set(false);
        const current = this.dietsSubject.value;
        this.dietsSubject.next([...current, newDiet]);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al crear tipo de dieta');
        return throwError(() => err);
      })
    );
  }

  updateDietType(oldName: string, dietData: { name: string }): Observable<DietType> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.put<DietType>(`${this.dietsApiUrl}/${oldName}`, dietData).pipe(
      tap(updatedDiet => {
        this.isLoading.set(false);
        const current = this.dietsSubject.value;
        this.dietsSubject.next(
          current.map(d => d.name === oldName ? updatedDiet : d)
        );
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al actualizar tipo de dieta');
        return throwError(() => err);
      })
    );
  }

  deleteDietType(name: string): Observable<void> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.delete<void>(`${this.dietsApiUrl}/${name}`).pipe(
      tap(() => {
        this.isLoading.set(false);
        const current = this.dietsSubject.value;
        this.dietsSubject.next(current.filter(d => d.name !== name));
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al eliminar tipo de dieta');
        return throwError(() => err);
      })
    );
  }

  fetchAllergens(): Observable<Allergen[]> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.get<Allergen[]>(this.allergensApiUrl).pipe(
      tap(allergens => {
        this.allergensSubject.next(allergens);
        this.isLoading.set(false);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al cargar alérgenos');
        return throwError(() => err);
      })
    );
  }

  createAllergen(allergenData: { name: string }): Observable<Allergen> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.post<Allergen>(this.allergensApiUrl, allergenData).pipe(
      tap(newAllergen => {
        this.isLoading.set(false);
        const current = this.allergensSubject.value;
        this.allergensSubject.next([...current, newAllergen]);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al crear alérgeno');
        return throwError(() => err);
      })
    );
  }

  updateAllergen(oldName: string, allergenData: { name: string }): Observable<Allergen> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.put<Allergen>(`${this.allergensApiUrl}/${oldName}`, allergenData).pipe(
      tap(updatedAllergen => {
        this.isLoading.set(false);
        const current = this.allergensSubject.value;
        this.allergensSubject.next(
          current.map(a => a.name === oldName ? updatedAllergen : a)
        );
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al actualizar alérgeno');
        return throwError(() => err);
      })
    );
  }

  deleteAllergen(name: string): Observable<void> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.delete<void>(`${this.allergensApiUrl}/${name}`).pipe(
      tap(() => {
        this.isLoading.set(false);
        const current = this.allergensSubject.value;
        this.allergensSubject.next(current.filter(a => a.name !== name));
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al eliminar alérgeno');
        return throwError(() => err);
      })
    );
  }

  fetchIngredients(): Observable<Ingredient[]> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.get<Ingredient[]>(this.ingredientsApiUrl).pipe(
      tap(ingredients => {
        this.ingredientsSubject.next(ingredients);
        this.isLoading.set(false);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al cargar ingredientes');
        return throwError(() => err);
      })
    );
  }

  createIngredient(ingredientData: Ingredient): Observable<Ingredient> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.post<Ingredient>(this.ingredientsApiUrl, ingredientData).pipe(
      tap(newIngredient => {
        this.isLoading.set(false);
        const current = this.ingredientsSubject.value;
        this.ingredientsSubject.next([...current, newIngredient]);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al crear ingrediente');
        return throwError(() => err);
      })
    );
  }

  updateIngredient(oldName: string, ingredientData: Ingredient): Observable<Ingredient> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.put<Ingredient>(`${this.ingredientsApiUrl}/${oldName}`, ingredientData).pipe(
      tap(updatedIngredient => {
        this.isLoading.set(false);
        const current = this.ingredientsSubject.value;
        this.ingredientsSubject.next(
          current.map(i => i.name === oldName ? updatedIngredient : i)
        );
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al actualizar ingrediente');
        return throwError(() => err);
      })
    );
  }

  deleteIngredient(name: string): Observable<void> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.delete<void>(`${this.ingredientsApiUrl}/${name}`).pipe(
      tap(() => {
        this.isLoading.set(false);
        const current = this.ingredientsSubject.value;
        this.ingredientsSubject.next(current.filter(i => i.name !== name));
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al eliminar ingrediente');
        return throwError(() => err);
      })
    );
  }

  fetchRecipes(): Observable<Recipe[]> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.get<Recipe[]>(this.recipesApiUrl).pipe(
      tap(recipes => {
        this.recipesSubject.next(recipes);
        this.isLoading.set(false);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al cargar recetas');
        return throwError(() => err);
      })
    );
  }

  createRecipe(recipeData: Recipe): Observable<Recipe> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.post<Recipe>(this.recipesApiUrl, recipeData).pipe(
      tap(newRecipe => {
        this.isLoading.set(false);
        const current = this.recipesSubject.value;
        this.recipesSubject.next([...current, newRecipe]);
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al crear receta');
        return throwError(() => err);
      })
    );
  }

  updateRecipe(recipeId: string, recipeData: Recipe): Observable<Recipe> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.put<Recipe>(`${this.recipesApiUrl}/${recipeId}`, recipeData).pipe(
      tap(updatedRecipe => {
        this.isLoading.set(false);
        const current = this.recipesSubject.value;
        this.recipesSubject.next(
          current.map(r => r.id === recipeId ? updatedRecipe : r)
        );
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al actualizar receta');
        return throwError(() => err);
      })
    );
  }

  deleteRecipe(recipeId: string): Observable<void> {
    this.isLoading.set(true);
    this.error.set(null);
    return this.http.delete<void>(`${this.recipesApiUrl}/${recipeId}`).pipe(
      tap(() => {
        this.isLoading.set(false);
        const current = this.recipesSubject.value;
        this.recipesSubject.next(current.filter(r => r.id !== recipeId));
      }),
      catchError(err => {
        this.isLoading.set(false);
        this.error.set(err.error?.detail || 'Error al eliminar receta');
        return throwError(() => err);
      })
    );
  }
}



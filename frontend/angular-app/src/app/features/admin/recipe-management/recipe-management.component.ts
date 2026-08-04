import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, Recipe, RecipeIngredient, Ingredient } from '../../../core/services/admin.service';

@Component({
  selector: 'app-recipe-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './recipe-management.component.html',
  styleUrls: ['./recipe-management.component.css']
})
export class RecipeManagementComponent implements OnInit {
  private adminService = inject(AdminService);

  recipes = signal<Recipe[]>([]);
  availableIngredients = signal<Ingredient[]>([]);
  isLoading = this.adminService.isLoading;
  error = this.adminService.error;

  searchTerm = signal('');

  showModal = signal(false);
  isEditing = signal(false);
  currentRecipeId = signal<string | null>(null);

  currentRecipe: Recipe = {
    name: '',
    description: '',
    ingredients: []
  };

  selectedIngredientName: string = '';
  selectedIngredientGrams: number = 100;

  ngOnInit() {
    this.loadData();
    this.adminService.recipes$.subscribe(recipes => {
      this.recipes.set(recipes);
    });
    this.adminService.ingredients$.subscribe(ingredients => {
      this.availableIngredients.set(ingredients);
      if (ingredients.length > 0 && !this.selectedIngredientName) {
        this.selectedIngredientName = ingredients[0].name;
      }
    });
  }

  loadData() {
    this.adminService.fetchRecipes().subscribe();
    this.adminService.fetchIngredients().subscribe();
  }

  get filteredRecipes(): Recipe[] {
    const term = this.searchTerm().toLowerCase().trim();
    const list = this.recipes();

    if (!term) return list;

    return list.filter(r =>
      r.name.toLowerCase().includes(term) ||
      (r.description || '').toLowerCase().includes(term)
    );
  }

  openCreateModal() {
    this.isEditing.set(false);
    this.currentRecipeId.set(null);
    this.currentRecipe = {
      name: '',
      description: '',
      ingredients: []
    };
    if (this.availableIngredients().length > 0) {
      this.selectedIngredientName = this.availableIngredients()[0].name;
    }
    this.selectedIngredientGrams = 100;
    this.showModal.set(true);
  }

  openEditModal(recipe: Recipe) {
    this.isEditing.set(true);
    this.currentRecipeId.set(recipe.id || null);
    this.currentRecipe = {
      name: recipe.name,
      description: recipe.description || '',
      ingredients: recipe.ingredients ? recipe.ingredients.map(i => ({ ...i })) : []
    };
    if (this.availableIngredients().length > 0) {
      this.selectedIngredientName = this.availableIngredients()[0].name;
    }
    this.selectedIngredientGrams = 100;
    this.showModal.set(true);
  }

  closeModal() {
    this.showModal.set(false);
    this.currentRecipeId.set(null);
  }

  addIngredientToDraft() {
    if (!this.selectedIngredientName || this.selectedIngredientGrams <= 0) return;
    
    // Check if ingredient is already in the list
    const existingIndex = this.currentRecipe.ingredients.findIndex(
      i => i.name.toLowerCase() === this.selectedIngredientName.toLowerCase()
    );

    if (existingIndex >= 0) {
      this.currentRecipe.ingredients[existingIndex].grams += Number(this.selectedIngredientGrams);
    } else {
      this.currentRecipe.ingredients.push({
        name: this.selectedIngredientName,
        grams: Number(this.selectedIngredientGrams)
      });
    }
  }

  removeIngredientFromDraft(index: number) {
    this.currentRecipe.ingredients.splice(index, 1);
  }

  saveRecipe() {
    if (!this.currentRecipe.name.trim()) return;

    const payload: Recipe = {
      name: this.currentRecipe.name.trim(),
      description: this.currentRecipe.description.trim(),
      ingredients: this.currentRecipe.ingredients.map(i => ({
        name: i.name,
        grams: Number(i.grams) || 0
      }))
    };

    if (this.isEditing() && this.currentRecipeId()) {
      this.adminService.updateRecipe(this.currentRecipeId()!, payload).subscribe({
        next: () => this.closeModal(),
        error: (err) => console.error('Error al actualizar receta:', err)
      });
    } else {
      this.adminService.createRecipe(payload).subscribe({
        next: () => this.closeModal(),
        error: (err) => console.error('Error al crear receta:', err)
      });
    }
  }

  deleteRecipe(recipe: Recipe) {
    if (!recipe.id) return;
    if (confirm(`¿Estás seguro de que deseas eliminar la receta "${recipe.name}"? Esta acción no se puede deshacer.`)) {
      this.adminService.deleteRecipe(recipe.id).subscribe();
    }
  }
}

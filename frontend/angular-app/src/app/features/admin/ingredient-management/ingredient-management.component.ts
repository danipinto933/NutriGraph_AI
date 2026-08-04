import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, Ingredient, Allergen } from '../../../core/services/admin.service';

@Component({
  selector: 'app-ingredient-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './ingredient-management.component.html',
  styleUrls: ['./ingredient-management.component.css']
})
export class IngredientManagementComponent implements OnInit {
  private adminService = inject(AdminService);
  
  ingredients = signal<Ingredient[]>([]);
  availableAllergens = signal<Allergen[]>([]);
  isLoading = this.adminService.isLoading;
  error = this.adminService.error;
  
  searchTerm = signal('');
  selectedCategoryFilter = signal<string>('all');
  collapsedCategories = signal<Set<string>>(new Set());
  viewMode = signal<'accordion' | 'table'>('accordion');
  
  showModal = signal(false);
  isEditing = signal(false);
  originalName = signal('');
  
  sortColumn = signal<keyof Ingredient | ''>('');
  sortDirection = signal<'asc' | 'desc'>('asc');
  
  currentIngredient: Ingredient = {
    name: '',
    calorias_100g: 0,
    proteinas_100g: 0,
    grasas_100g: 0,
    carbohidratos_100g: 0,
    origen: 'vegetal',
    categoria: 'varios',
    allergens: []
  };
  
  ngOnInit() {
    this.loadData();
    this.adminService.ingredients$.subscribe(ingredients => {
      this.ingredients.set(ingredients);
    });
    this.adminService.allergens$.subscribe(allergens => {
      this.availableAllergens.set(allergens);
    });
  }
  
  loadData() {
    this.adminService.fetchIngredients().subscribe();
    this.adminService.fetchAllergens().subscribe();
  }

  sortBy(columnKey: keyof Ingredient) {
    if (this.sortColumn() === columnKey) {
      this.sortDirection.set(this.sortDirection() === 'asc' ? 'desc' : 'asc');
    } else {
      this.sortColumn.set(columnKey);
      const isNumeric = ['calorias_100g', 'proteinas_100g', 'grasas_100g', 'carbohidratos_100g'].includes(columnKey);
      // Para números: primer click de mayor a menor ('desc'). Para texto: primer click A-Z ('asc').
      this.sortDirection.set(isNumeric ? 'desc' : 'asc');
    }
  }
  
  get existingCategories(): string[] {
    const baseCategories = [
      'Aceites y Grasas',
      'Carnes',
      'Cereales y Tubérculos',
      'Frutas',
      'Frutos Secos y Semillas',
      'Lácteos',
      'Legumbres',
      'Pescados y Mariscos',
      'Salsas y Condimentos',
      'Verduras y Hortalizas'
    ];
    const dbCats = this.ingredients()
      .map(i => i.categoria)
      .filter((c): c is string => !!c && c.trim() !== '');
    return Array.from(new Set([...baseCategories, ...dbCats])).sort((a, b) => 
      a.localeCompare(b, 'es', { sensitivity: 'base' })
    );
  }

  get filteredIngredients(): Ingredient[] {
    const term = this.searchTerm().toLowerCase().trim();
    const selectedCat = this.selectedCategoryFilter();
    let list = this.ingredients();

    if (selectedCat !== 'all') {
      list = list.filter(i => (i.categoria || 'varios').toLowerCase() === selectedCat.toLowerCase());
    }

    if (term) {
      list = list.filter(i => 
        i.name.toLowerCase().includes(term) ||
        (i.categoria || '').toLowerCase().includes(term) ||
        (i.origen || '').toLowerCase().includes(term)
      );
    }

    const col = this.sortColumn();
    const dir = this.sortDirection();

    if (!col) return list;

    return [...list].sort((a, b) => {
      let valA = a[col];
      let valB = b[col];

      if (valA === undefined || valA === null) valA = '';
      if (valB === undefined || valB === null) valB = '';

      if (typeof valA === 'number' && typeof valB === 'number') {
        return dir === 'desc' ? valB - valA : valA - valB;
      }

      const strA = String(valA).localeCompare(String(valB), 'es', { sensitivity: 'base' });
      return dir === 'desc' ? -strA : strA;
    });
  }

  get groupedIngredients(): { category: string; ingredients: Ingredient[]; count: number }[] {
    const list = this.filteredIngredients;
    const groupsMap = new Map<string, Ingredient[]>();

    for (const item of list) {
      const catName = item.categoria?.trim() || 'Sin Categoría';
      if (!groupsMap.has(catName)) {
        groupsMap.set(catName, []);
      }
      groupsMap.get(catName)!.push(item);
    }

    const result = Array.from(groupsMap.entries()).map(([category, ingredients]) => ({
      category,
      ingredients,
      count: ingredients.length
    }));

    return result.sort((a, b) => a.category.localeCompare(b.category, 'es', { sensitivity: 'base' }));
  }

  toggleCategory(categoryName: string) {
    const current = new Set(this.collapsedCategories());
    if (current.has(categoryName)) {
      current.delete(categoryName);
    } else {
      current.add(categoryName);
    }
    this.collapsedCategories.set(current);
  }

  isCategoryCollapsed(categoryName: string): boolean {
    return this.collapsedCategories().has(categoryName);
  }

  expandAllCategories() {
    this.collapsedCategories.set(new Set());
  }

  collapseAllCategories() {
    const allCats = new Set(this.groupedIngredients.map(g => g.category));
    this.collapsedCategories.set(allCats);
  }
  
  openCreateModal() {
    this.isEditing.set(false);
    this.originalName.set('');
    this.currentIngredient = {
      name: '',
      calorias_100g: 0,
      proteinas_100g: 0,
      grasas_100g: 0,
      carbohidratos_100g: 0,
      origen: 'vegetal',
      categoria: this.existingCategories[0] || 'Verduras y Hortalizas',
      allergens: []
    };
    this.showModal.set(true);
  }
  
  openEditModal(ingredient: Ingredient) {
    this.isEditing.set(true);
    this.originalName.set(ingredient.name);
    this.currentIngredient = {
      name: ingredient.name,
      calorias_100g: ingredient.calorias_100g,
      proteinas_100g: ingredient.proteinas_100g,
      grasas_100g: ingredient.grasas_100g,
      carbohidratos_100g: ingredient.carbohidratos_100g,
      origen: ingredient.origen,
      categoria: ingredient.categoria,
      allergens: ingredient.allergens ? [...ingredient.allergens] : []
    };
    this.showModal.set(true);
  }
  
  closeModal() {
    this.showModal.set(false);
    this.originalName.set('');
  }
  
  isAllergenSelected(allergenName: string): boolean {
    return !!this.currentIngredient.allergens?.includes(allergenName);
  }
  
  toggleAllergen(allergenName: string) {
    if (!this.currentIngredient.allergens) {
      this.currentIngredient.allergens = [];
    }
    const idx = this.currentIngredient.allergens.indexOf(allergenName);
    if (idx > -1) {
      this.currentIngredient.allergens.splice(idx, 1);
    } else {
      this.currentIngredient.allergens.push(allergenName);
    }
  }
  
  saveIngredient() {
    if (!this.currentIngredient.name.trim()) return;
    
    const payload: Ingredient = {
      name: this.currentIngredient.name.trim(),
      calorias_100g: Number(this.currentIngredient.calorias_100g) || 0,
      proteinas_100g: Number(this.currentIngredient.proteinas_100g) || 0,
      grasas_100g: Number(this.currentIngredient.grasas_100g) || 0,
      carbohidratos_100g: Number(this.currentIngredient.carbohidratos_100g) || 0,
      origen: this.currentIngredient.origen || 'vegetal',
      categoria: this.currentIngredient.categoria.trim() || 'varios',
      allergens: this.currentIngredient.allergens || []
    };
    
    if (this.isEditing()) {
      this.adminService.updateIngredient(this.originalName(), payload).subscribe({
        next: () => this.closeModal(),
        error: (err) => console.error('Error al actualizar ingrediente:', err)
      });
    } else {
      this.adminService.createIngredient(payload).subscribe({
        next: () => this.closeModal(),
        error: (err) => console.error('Error al crear ingrediente:', err)
      });
    }
  }
  
  deleteIngredient(ingredient: Ingredient) {
    if (confirm(`¿Estás seguro de que deseas eliminar el ingrediente "${ingredient.name}"? Esta acción no se puede deshacer.`)) {
      this.adminService.deleteIngredient(ingredient.name).subscribe();
    }
  }
}

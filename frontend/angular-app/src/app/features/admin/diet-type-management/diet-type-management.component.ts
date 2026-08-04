import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, DietType } from '../../../core/services/admin.service';

@Component({
  selector: 'app-diet-type-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './diet-type-management.component.html',
  styleUrls: ['./diet-type-management.component.css']
})
export class DietTypeManagementComponent implements OnInit {
  private adminService = inject(AdminService);
  
  dietTypes = signal<DietType[]>([]);
  isLoading = this.adminService.isLoading;
  error = this.adminService.error;
  
  searchTerm = signal('');
  
  showModal = signal(false);
  isEditing = signal(false);
  
  // Form State
  currentDietName = signal('');
  originalDietName = signal('');
  
  ngOnInit() {
    this.loadDiets();
    this.adminService.diets$.subscribe(diets => {
      this.dietTypes.set(diets);
    });
  }
  
  loadDiets() {
    this.adminService.fetchDietTypes().subscribe();
  }
  
  get filteredDiets() {
    const term = this.searchTerm().toLowerCase();
    if (!term) return this.dietTypes();
    
    return this.dietTypes().filter(d => 
      d.name.toLowerCase().includes(term)
    );
  }
  
  openCreateModal() {
    this.isEditing.set(false);
    this.currentDietName.set('');
    this.originalDietName.set('');
    this.showModal.set(true);
  }
  
  openEditModal(diet: DietType) {
    this.isEditing.set(true);
    this.currentDietName.set(diet.name);
    this.originalDietName.set(diet.name);
    this.showModal.set(true);
  }
  
  closeModal() {
    this.showModal.set(false);
    this.currentDietName.set('');
    this.originalDietName.set('');
  }
  
  saveDiet() {
    if (!this.currentDietName().trim()) return;
    
    const dietData = { name: this.currentDietName().trim() };
    
    if (this.isEditing()) {
      this.adminService.updateDietType(this.originalDietName(), dietData).subscribe({
        next: () => this.closeModal()
      });
    } else {
      this.adminService.createDietType(dietData).subscribe({
        next: () => this.closeModal()
      });
    }
  }
  
  deleteDiet(diet: DietType) {
    if (confirm(`¿Estás seguro de que deseas eliminar el tipo de dieta "${diet.name}"? Los usuarios que tengan esta dieta se quedarán sin dieta asignada.`)) {
      this.adminService.deleteDietType(diet.name).subscribe();
    }
  }
}

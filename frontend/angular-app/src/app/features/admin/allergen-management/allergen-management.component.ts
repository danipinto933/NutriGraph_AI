import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, Allergen } from '../../../core/services/admin.service';

@Component({
  selector: 'app-allergen-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './allergen-management.component.html',
  styleUrls: ['./allergen-management.component.css']
})
export class AllergenManagementComponent implements OnInit {
  private adminService = inject(AdminService);
  
  allergens = signal<Allergen[]>([]);
  isLoading = this.adminService.isLoading;
  error = this.adminService.error;
  
  searchTerm = signal('');
  
  showModal = signal(false);
  isEditing = signal(false);
  
  // Form State
  currentAllergenName = signal('');
  originalAllergenName = signal('');
  
  ngOnInit() {
    this.loadAllergens();
    this.adminService.allergens$.subscribe(allergens => {
      this.allergens.set(allergens);
    });
  }
  
  loadAllergens() {
    this.adminService.fetchAllergens().subscribe();
  }
  
  get filteredAllergens() {
    const term = this.searchTerm().toLowerCase();
    if (!term) return this.allergens();
    
    return this.allergens().filter(a => 
      a.name.toLowerCase().includes(term)
    );
  }
  
  openCreateModal() {
    this.isEditing.set(false);
    this.currentAllergenName.set('');
    this.originalAllergenName.set('');
    this.showModal.set(true);
  }
  
  openEditModal(allergen: Allergen) {
    this.isEditing.set(true);
    this.currentAllergenName.set(allergen.name);
    this.originalAllergenName.set(allergen.name);
    this.showModal.set(true);
  }
  
  closeModal() {
    this.showModal.set(false);
    this.currentAllergenName.set('');
    this.originalAllergenName.set('');
  }
  
  saveAllergen() {
    if (!this.currentAllergenName().trim()) return;
    
    const allergenData = { name: this.currentAllergenName().trim() };
    
    if (this.isEditing()) {
      this.adminService.updateAllergen(this.originalAllergenName(), allergenData).subscribe({
        next: () => this.closeModal()
      });
    } else {
      this.adminService.createAllergen(allergenData).subscribe({
        next: () => this.closeModal()
      });
    }
  }
  
  deleteAllergen(allergen: Allergen) {
    if (confirm(`¿Estás seguro de que deseas eliminar el alérgeno "${allergen.name}"? Los usuarios que lo tengan asignado perderán esta intolerancia.`)) {
      this.adminService.deleteAllergen(allergen.name).subscribe();
    }
  }
}

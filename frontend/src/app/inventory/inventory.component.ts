import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { SneakerService, Sneaker, SneakerCreate } from '../services/sneaker.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-inventory',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './inventory.component.html',
  styleUrl: './inventory.component.scss'
})
export class InventoryComponent implements OnInit {
  private sneakerService = inject(SneakerService);
  private authService = inject(AuthService);
  private router = inject(Router);

  sneakers = signal<Sneaker[]>([]);
  isLoading = signal<boolean>(false);
  
  // Filter signals
  searchText = signal<string>('');
  selectedBrand = signal<string>('');
  selectedSize = signal<string>('');
  
  // Computed values for filters
  availableBrands = computed(() => {
    const brands = new Set(this.sneakers().map(s => s.brand));
    return Array.from(brands).sort();
  });
  
  availableSizes = computed(() => {
    const sizes = new Set(this.sneakers().map(s => s.size.toString()));
    return Array.from(sizes).sort((a, b) => parseFloat(a) - parseFloat(b));
  });
  
  filteredSneakers = computed(() => {
    let filtered = this.sneakers();
    
    // Filter by search text
    const search = this.searchText().toLowerCase();
    if (search) {
      filtered = filtered.filter(s => 
        s.brand.toLowerCase().includes(search) ||
        s.model.toLowerCase().includes(search) ||
        s.sku.toLowerCase().includes(search) ||
        (s.color && s.color.toLowerCase().includes(search))
      );
    }
    
    // Filter by brand
    if (this.selectedBrand()) {
      filtered = filtered.filter(s => s.brand === this.selectedBrand());
    }
    
    // Filter by size
    if (this.selectedSize()) {
      filtered = filtered.filter(s => s.size.toString() === this.selectedSize());
    }
    
    return filtered;
  });
  
  sneakerForm = new FormGroup({
    sku: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    brand: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    model: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    size: new FormControl<number | null>(null, { validators: [Validators.required, Validators.min(0)] }),
    color: new FormControl('', { nonNullable: true }),
    purchase_price: new FormControl<number | null>(null, { validators: [Validators.min(0)] }),
    description: new FormControl('', { nonNullable: true })
  });

  ngOnInit(): void {
    this.loadSneakers();
  }

  loadSneakers(): void {
    const user = this.authService.currentUserValue;
    if (user) {
      this.sneakerService.getSneakers(user.id).subscribe({
        next: (data) => this.sneakers.set(data),
        error: (err) => console.error('Failed to load sneakers', err)
      });
    }
  }

  onSubmit(): void {
    if (this.sneakerForm.valid && !this.isLoading()) {
      this.isLoading.set(true);
      this.sneakerForm.disable();
      
      const formValue = this.sneakerForm.getRawValue();
      
      const newSneaker: SneakerCreate = {
        sku: formValue.sku,
        brand: formValue.brand,
        model: formValue.model,
        size: formValue.size!,
        color: formValue.color || undefined,
        purchase_price: formValue.purchase_price || undefined,
        description: formValue.description || undefined
      };

      this.sneakerService.createSneaker(newSneaker).subscribe({
        next: (sneaker) => {
          this.sneakers.update(current => [...current, sneaker]);
          this.sneakerForm.reset();
          this.sneakerForm.enable();
          this.isLoading.set(false);
        },
        error: (err) => {
          console.error('Failed to create sneaker', err);
          this.sneakerForm.enable();
          this.isLoading.set(false);
        }
      });
    }
  }

  clearFilters(): void {
    this.searchText.set('');
    this.selectedBrand.set('');
    this.selectedSize.set('');
  }

  viewSneaker(id: number): void {
    this.router.navigate(['/sneaker', id]);
  }

  editSneaker(event: Event, id: number): void {
    event.stopPropagation(); // Prevent row click from triggering
    this.router.navigate(['/sneaker', id, 'edit']);
  }
}

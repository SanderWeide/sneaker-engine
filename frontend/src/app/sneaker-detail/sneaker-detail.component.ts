import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { SneakerService, Sneaker, SneakerUpdate } from '../services/sneaker.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-sneaker-detail',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './sneaker-detail.component.html',
  styleUrl: './sneaker-detail.component.scss'
})
export class SneakerDetailComponent implements OnInit {
  private sneakerService = inject(SneakerService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  sneaker = signal<Sneaker | null>(null);
  isLoading = signal<boolean>(false);
  isEditing = signal<boolean>(false);
  
  editForm = new FormGroup({
    sku: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    brand: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    model: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    size: new FormControl<number | null>(null, { validators: [Validators.required, Validators.min(0)] }),
    color: new FormControl('', { nonNullable: true }),
    purchase_price: new FormControl<number | null>(null, { validators: [Validators.min(0)] }),
    description: new FormControl('', { nonNullable: true })
  });

  ngOnInit(): void {
    window.scrollTo(0, 0);
    const id = this.route.snapshot.paramMap.get('id');
    
    // Check if we're in edit mode based on the URL
    const urlSegments = this.route.snapshot.url;
    const isEditRoute = urlSegments.some(segment => segment.path === 'edit');
    if (isEditRoute) {
      this.isEditing.set(true);
    }
    
    if (id) {
      this.loadSneaker(parseInt(id));
    }
  }

  loadSneaker(id: number): void {
    this.isLoading.set(true);
    const user = this.authService.currentUserValue;
    if (user) {
      this.sneakerService.getSneakers(user.id).subscribe({
        next: (sneakers) => {
          const found = sneakers.find(s => s.id === id);
          if (found) {
            this.sneaker.set(found);
            this.populateForm(found);
          } else {
            this.router.navigate(['/inventory']);
          }
          this.isLoading.set(false);
        },
        error: (err) => {
          console.error('Failed to load sneaker', err);
          this.isLoading.set(false);
          this.router.navigate(['/inventory']);
        }
      });
    }
  }

  populateForm(sneaker: Sneaker): void {
    this.editForm.patchValue({
      sku: sneaker.sku,
      brand: sneaker.brand,
      model: sneaker.model,
      size: sneaker.size,
      color: sneaker.color || '',
      purchase_price: sneaker.purchase_price || null,
      description: sneaker.description || ''
    });
  }

  toggleEdit(): void {
    this.isEditing.update(v => !v);
    if (!this.isEditing() && this.sneaker()) {
      this.populateForm(this.sneaker()!);
    }
  }

  onSubmit(): void {
    if (this.editForm.valid && this.sneaker() && !this.isLoading()) {
      this.isLoading.set(true);
      this.editForm.disable();
      
      const formValue = this.editForm.getRawValue();
      const updateData: SneakerUpdate = {
        sku: formValue.sku,
        brand: formValue.brand,
        model: formValue.model,
        size: formValue.size!,
        color: formValue.color || undefined,
        purchase_price: formValue.purchase_price || undefined,
        description: formValue.description || undefined
      };

      this.sneakerService.updateSneaker(this.sneaker()!.id, updateData).subscribe({
        next: (updatedSneaker) => {
          this.sneaker.set(updatedSneaker);
          this.editForm.enable();
          this.isEditing.set(false);
          this.isLoading.set(false);
        },
        error: (err) => {
          console.error('Failed to update sneaker', err);
          this.editForm.enable();
          this.isLoading.set(false);
        }
      });
    }
  }

  goBack(): void {
    this.router.navigate(['/inventory']);
  }
}

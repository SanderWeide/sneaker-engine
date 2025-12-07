import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
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

  sneakers = signal<Sneaker[]>([]);
  
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
    if (this.sneakerForm.valid) {
      const user = this.authService.currentUserValue;
      if (!user) return;

      const formValue = this.sneakerForm.getRawValue();
      
      const newSneaker: SneakerCreate = {
        sku: formValue.sku,
        brand: formValue.brand,
        model: formValue.model,
        size: formValue.size!,
        color: formValue.color || undefined,
        purchase_price: formValue.purchase_price || undefined,
        description: formValue.description || undefined,
        user_id: user.id
      };

      this.sneakerService.createSneaker(newSneaker).subscribe({
        next: (sneaker) => {
          this.sneakers.update(current => [...current, sneaker]);
          this.sneakerForm.reset();
        },
        error: (err) => console.error('Failed to create sneaker', err)
      });
    }
  }
}

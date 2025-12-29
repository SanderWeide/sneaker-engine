import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { SignupComponent } from './signup/signup.component';
import { HomeComponent } from './home/home.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'home', component: HomeComponent, canActivate: [authGuard] },
  { 
    path: 'inventory', 
    loadComponent: () => import('./inventory/inventory.component').then(m => m.InventoryComponent),
    canActivate: [authGuard] 
  },
  {
    path: 'sneaker/:id',
    loadComponent: () => import('./sneaker-detail/sneaker-detail.component').then(m => m.SneakerDetailComponent),
    canActivate: [authGuard]
  },
  {
    path: 'sneaker/:id/edit',
    loadComponent: () => import('./sneaker-detail/sneaker-detail.component').then(m => m.SneakerDetailComponent),
    canActivate: [authGuard]
  }
];

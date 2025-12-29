import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Sneaker {
  id: number;
  sku: string;
  brand: string;
  model: string;
  size: number;
  color?: string;
  purchase_price?: number;
  description?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface SneakerCreate {
  sku: string;
  brand: string;
  model: string;
  size: number;
  color?: string;
  purchase_price?: number;
  description?: string;
}

export interface SneakerUpdate {
  sku?: string;
  brand?: string;
  model?: string;
  size?: number;
  color?: string;
  purchase_price?: number;
  description?: string;
}

@Injectable({
  providedIn: 'root'
})
export class SneakerService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/sneakers`;

  getSneakers(userId?: number): Observable<Sneaker[]> {
    let url = this.apiUrl;
    if (userId) {
      url += `?user_id=${userId}`;
    }
    return this.http.get<Sneaker[]>(url);
  }

  createSneaker(sneaker: SneakerCreate): Observable<Sneaker> {
    return this.http.post<Sneaker>(this.apiUrl, sneaker);
  }

  updateSneaker(id: number, sneaker: SneakerUpdate): Observable<Sneaker> {
    return this.http.put<Sneaker>(`${this.apiUrl}/${id}`, sneaker);
  }
}

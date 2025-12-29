import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap, switchMap } from 'rxjs';
import { environment } from '../../environments/environment';

interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface SignupData {
  email: string;
  username: string;
  password: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser: Observable<User | null>;

  constructor(private http: HttpClient) {
    const storedUser = localStorage.getItem('currentUser');
    this.currentUserSubject = new BehaviorSubject<User | null>(
      storedUser ? JSON.parse(storedUser) : null
    );
    this.currentUser = this.currentUserSubject.asObservable();
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  login(email: string, password: string): Observable<User> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, formData)
      .pipe(
        switchMap(response => {
          if (response.access_token) {
            localStorage.setItem('access_token', response.access_token);
            return this.getUserProfile();
          }
          throw new Error('No access token received');
        })
      );
  }

  signup(data: SignupData): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/auth/register`, data)
      .pipe(
        switchMap(() => {
          // After signup, automatically log in and get user profile
          return this.login(data.email, data.password);
        })
      );
  }

  getUserProfile(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/api/users/me`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }).pipe(
      tap(user => {
        localStorage.setItem('currentUser', JSON.stringify(user));
        this.currentUserSubject.next(user);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }
}

# GitHub Copilot Instructions for Sneaker Engine

**IMPORTANT**: When working on Angular code, always refer to the official Angular LLM context:
- Full documentation: https://angular.dev/assets/context/llms-full.txt

## Project Overview
This is a sneaker marketplace application with an Angular frontend and FastAPI backend. Users can buy, sell, and trade sneakers with a proposition-based trading system.

## Tech Stack
- **Frontend**: Angular 20.3.0 (standalone components), TypeScript 5.9.2, RxJS, Vite
- **Backend**: FastAPI (Python 3.12), PostgreSQL 16, Alembic, SQLAlchemy
- **Styling**: SCSS with custom properties (SCSS variables) for theming
- **Authentication**: JWT tokens with Bearer authentication

## Code Style & Standards

### TypeScript Best Practices
- Use **strict type checking** - all types must be defined
- Prefer **type inference** when the type is obvious from the value
- **Avoid the `any` type** - use `unknown` when the type is uncertain
- Use union types and type guards for type safety
- Prefer `interface` over `type` for object shapes (better for extension)

### Angular Best Practices
- Use **standalone components** - no NgModules
- **Do NOT set `standalone: true`** in decorators - it's the default in Angular v20+
- Use **signals** for state management
- Implement **lazy loading** for feature routes
- **Do NOT use `@HostBinding` and `@HostListener` decorators** - use the `host` object in `@Component` or `@Directive` decorator instead
- Use **`NgOptimizedImage`** for all static images (does not work for inline base64 images)
- Import from `@angular/common` explicitly (CommonModule, etc.)
- Component file naming: `{name}.component.ts`, `{name}.component.html`, `{name}.component.scss`
- Service file naming: `{name}.service.ts`

### Accessibility Requirements
- **MUST pass all AXE checks** - run accessibility audits regularly
- **MUST follow WCAG AA minimums** including:
  - Focus management (visible focus indicators, logical tab order)
  - Color contrast ratios (4.5:1 for normal text, 3:1 for large text)
  - ARIA attributes (roles, labels, descriptions where needed)
  - Keyboard navigation support for all interactive elements
  - Screen reader compatibility

### Component Architecture
- Keep components **small and focused** on a single responsibility
- Use **`input()` and `output()` functions** instead of `@Input` and `@Output` decorators
- Use **`computed()`** for derived state
- Set **`changeDetection: ChangeDetectionStrategy.OnPush`** in `@Component` decorator for performance
- Prefer **inline templates** for small components
- Prefer **Reactive forms** over Template-driven forms
- **Do NOT use `ngClass`** - use `class` bindings instead
- **Do NOT use `ngStyle`** - use `style` bindings instead
- When using external templates/styles, use **paths relative to the component TS file**

```typescript
// Good: Modern standalone component with best practices
@Component({
  selector: 'app-example',
  imports: [CommonModule, FormsModule],
  templateUrl: './example.component.html',
  styleUrl: './example.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    '(click)': 'onClick()',
    '[class.active]': 'isActive()'
  }
})
export class ExampleComponent implements OnInit, OnDestroy {
  // Use input() and output() functions
  title = input<string>('Default Title');
  itemClicked = output<string>();
  
  // Use signals for simple state
  protected readonly count = signal(0);
  
  // Use computed() for derived state
  protected readonly doubleCount = computed(() => this.count() * 2);
  
  // Use Observables for async streams
  private subscription?: Subscription;
  
  constructor(private exampleService: ExampleService) {}
  
  ngOnInit(): void {
    this.subscription = this.exampleService.data$.subscribe(data => {
      // Handle data
    });
  }
  
  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }
  
  onClick(): void {
    this.itemClicked.emit('clicked');
  }
  
  isActive(): boolean {
    return this.count() > 0;
  }
}
```

### State Management
- Use **signals** for local component state
- Use **`computed()`** for derived state
- Keep state transformations **pure and predictable**
- **Do NOT use `mutate`** on signals - use **`update`** or **`set`** instead
- Use **RxJS Observables** for async operations and complex data streams

```typescript
// Good: Proper signal usage
protected readonly items = signal<Item[]>([]);

// Add item using update (good)
addItem(item: Item): void {
  this.items.update(current => [...current, item]);
}

// Remove item using set (good)
removeItem(id: string): void {
  this.items.set(this.items().filter(item => item.id !== id));
}

// Bad: Using mutate (avoid this)
addItemBad(item: Item): void {
  this.items.mutate(items => items.push(item)); // ❌ Don't do this
}
```

### Templates
- Keep templates **simple** and avoid complex logic
- Use **native control flow** (`@if`, `@for`, `@switch`) instead of `*ngIf`, `*ngFor`, `*ngSwitch`
- Use the **`async` pipe** to handle observables
- **Do NOT assume globals** like `new Date()` are available in templates
- **Do NOT write arrow functions** in templates (they are not supported)
- Use **class bindings** instead of `ngClass`
- Use **style bindings** instead of `ngStyle`

```html
<!-- Good: Native control flow -->
@if (isLoading()) {
  <div class="loading">Loading...</div>
} @else {
  <div class="content">
    @for (item of items(); track item.id) {
      <div [class.active]="item.id === selectedId()"
           [style.color]="item.color">
        {{ item.name }}
      </div>
    }
  </div>
}

<!-- Good: Async pipe -->
@if (data$ | async; as data) {
  <div>{{ data.title }}</div>
}

<!-- Bad: Old syntax -->
<div *ngIf="isLoading">Loading...</div>
<div *ngFor="let item of items">{{ item.name }}</div>

<!-- Bad: Arrow functions in templates -->
<button (click)="items.filter(i => i.active)">Filter</button>

<!-- Bad: ngClass and ngStyle -->
<div [ngClass]="{'active': isActive}"></div>
<div [ngStyle]="{'color': textColor}"></div>
```

### Services
- All services should be `providedIn: 'root'`
- Design services around a **single responsibility**
- Use the **`inject()` function** instead of constructor injection
- Use **BehaviorSubject** for state that needs initial value
- Expose Observables as `readonly` properties ending with `$`
- Handle errors gracefully with proper error messages

```typescript
@Injectable({
  providedIn: 'root',
})
export class ExampleService {
  private http = inject(HttpClient);
  private toastService = inject(ToastService);
  
  private dataSubject = new BehaviorSubject<Data[]>([]);
  public readonly data$ = this.dataSubject.asObservable();
  
  fetchData(): void {
    this.http.get<Data[]>('/api/data').subscribe({
      next: (data) => this.dataSubject.next(data),
      error: (error) => {
        console.error('Failed to fetch data:', error);
        this.toastService.error('Failed to load data');
      }
    });
  }
}
```

### SCSS & Theming
- **Always use SCSS variables** for colors - never hardcode colors
- SCSS variables are defined in `frontend/src/styles.scss`
- Light mode in `:root`, dark mode in `body.dark-mode`
- Available variables:
  - `--bg-primary`, `--bg-secondary`, `--bg-tertiary`
  - `--text-primary`, `--text-secondary`, `--text-on-dark-bg`, `--text-on-light-bg`
  - `--card-bg`, `--card-border`
  - `--button-primary-bg`, `--button-primary-text`, `--button-primary-hover`
  - `--button-success-bg`, `--button-success-text`, `--button-success-hover`
  - `--button-danger-bg`, `--button-danger-text`, `--button-danger-hover`
  - `--input-bg`, `--input-border`, `--input-focus-border`
  - `--border-color`, `--modal-overlay`
  - `--shadow`, `--shadow-medium`, `--shadow-large`
  - `--focus-shadow`, `--focus-shadow-strong`
  - `--toast-{type}-{bg|border|text}` (success, info, warning, error)
  - `--alert-{type}-{bg|border|text}` (success, info, warning, danger)

```scss
/* Good: Use SCSS variables */
.card {
  background-color: var(--card-bg);
  border: 1px solid var(--card-border);
  color: var(--text-primary);
  box-shadow: var(--shadow);
}

/* Bad: Hardcoded colors */
.card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  color: #333333;
}
```

### Dark Mode Best Practices

**1. Always Use SCSS Variables**
- Never use hardcoded colors (#hex, rgb, rgba)
- Never use generic color names (white, black, gray)
- Use semantic variable names that work in both themes

**2. Contrast & Readability**
- Ensure text has sufficient contrast against backgrounds
- Use `--text-primary` for main text, `--text-secondary` for muted text
- Active/selected items should have clear visual distinction
- Links and buttons must be readable in both themes

**3. Hover & Focus States**
- All interactive elements need visible hover states
- Focus states should use `--focus-shadow` or `--focus-shadow-strong`
- Hover should change background, border, or shadow
- Transitions smooth (0.2s) for better UX

```scss
/* Good: Proper interactive states */
.button {
  background-color: var(--button-primary-bg);
  color: var(--button-primary-text);
  transition: all 0.2s;
}

.button:hover {
  background-color: var(--button-primary-hover);
  box-shadow: var(--shadow-medium);
  transform: translateY(-2px);
}

.button:focus {
  outline: none;
  box-shadow: var(--focus-shadow-strong);
}
```

**4. Shadows & Depth**
- Use `--shadow` for subtle elevation
- Use `--shadow-medium` for hover states
- Use `--shadow-large` for modals and popovers
- Shadows should work in both light and dark modes

**5. Borders & Dividers**
- Always use `--border-color` for borders
- Use `--card-border` for card/component borders
- Borders help define boundaries in dark mode

**6. Forms & Inputs**
- Use `--input-bg` for input backgrounds
- Use `--input-border` for default borders
- Use `--input-focus-border` for focused state
- Placeholders should use `--text-secondary` with opacity
- Input text should use `--text-primary`

```scss
/* Good: Dark mode friendly inputs */
.input {
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  color: var(--text-primary);
}

.input::placeholder {
  color: var(--text-secondary);
  opacity: 0.7;
}

.input:hover {
  border-color: var(--text-secondary);
}

.input:focus {
  border-color: var(--input-focus-border);
  box-shadow: var(--focus-shadow);
  background-color: var(--card-bg);
}
```

**7. Modal & Overlay**
- Use `--modal-overlay` for semi-transparent backgrounds
- Add `backdrop-filter: blur(2px)` for modern browsers
- Modal content should use `--card-bg` with `--shadow-large`
- Animate modal appearance (fade + slide)

**8. Visual Hierarchy**
- Use background colors to create sections (`--bg-tertiary`)
- Use gradients sparingly with SCSS variables
- Layer shadows to indicate depth
- Group related items with subtle backgrounds

**9. Icons & SVG**
- SVGs should inherit `currentColor` for automatic theme support
- Use `stroke="currentColor"` and `fill="currentColor"`
- Icon buttons should have clear hover states

```scss
/* Good: Theme-aware icons */
.icon-btn {
  color: var(--text-secondary);
  background: none;
  border: 1px solid var(--border-color);
}

.icon-btn:hover {
  color: var(--button-primary-text);
  background-color: var(--button-primary-bg);
  border-color: var(--button-primary-bg);
}

.icon-btn svg {
  stroke: currentColor; /* Inherits button color */
}
```

**10. Animations & Transitions**
- All color changes should have `transition: all 0.2s`
- Hover effects: slight movement + shadow increase
- Focus effects: glow with theme color
- Modal/overlay animations: fade in (0.2s) + slide in (0.3s)

```scss
/* Good: Smooth animations */
.card {
  transition: all 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
  border-color: var(--button-primary-bg);
}
```

**11. Testing Requirements**
- Test every component in both light and dark mode
- Check contrast ratios (WCAG AA minimum)
- Verify hover/focus states are visible
- Ensure forms are readable when filled
- Check that errors/success states are clear

**12. Common Pitfalls to Avoid**
- ❌ Hardcoded white/black for text
- ❌ Transparent backgrounds without considering underlying color
- ❌ Missing hover states on interactive elements
- ❌ Insufficient contrast between text and background
- ❌ Using opacity on colored elements (use SCSS variables instead)
- ❌ Forgetting placeholder text colors
- ❌ Missing focus indicators
- ❌ Gradients with hardcoded colors

### API Integration
- Backend runs on `http://127.0.0.1:8000`
- All API requests require JWT token in Authorization header: `Bearer {token}`
- Use `AuthService` for token management
- Handle 401 responses by redirecting to login

```typescript
// Good: Proper authentication headers
this.http.get(`${environment.apiUrl}/api/endpoint`, {
  headers: { Authorization: `Bearer ${this.authService.getToken()}` }
})
```

### Error Handling
- Use `ToastService` for user-facing error messages
- Log errors to console for debugging
- Provide helpful error messages to users

```typescript
// Good: Proper error handling
this.exampleService.getData().subscribe({
  next: (data) => {
    // Handle success
  },
  error: (error) => {
    console.error('Failed to load data:', error);
    this.toastService.error('Failed to load data. Please try again.');
  }
});
```

## Backend Conventions

### FastAPI Routes
- Use proper HTTP methods: GET, POST, PUT, DELETE
- All routes require authentication except `/auth/*`
- Return proper HTTP status codes
- Use Pydantic models for request/response validation

```python
# Good: Proper route with authentication and validation
@router.get("/api/sneakers", response_model=List[SneakerResponse])
async def get_sneakers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sneakers = db.query(Sneaker).filter(Sneaker.owner_id == current_user.id).all()
    return sneakers
```

### Database Models
- Use SQLAlchemy ORM models
- Define proper relationships with `relationship()` and `foreign_key`
- Use Alembic for migrations
- Never commit database credentials

## Common Patterns

### Toast Notifications
```typescript
// Use ToastService for user feedback
this.toastService.success('Sneaker added successfully!');
this.toastService.error('Failed to save sneaker');
this.toastService.warning('Unsaved changes');
this.toastService.info('Loading data...');
```

### Theme Switching
```typescript
// Use ThemeService for dark mode
constructor(private themeService: ThemeService) {}

toggleTheme(): void {
  this.themeService.toggleDarkMode();
}
```

### Form Handling
```typescript
// Use Angular Forms with proper validation
protected sneakerForm = new FormGroup({
  name: new FormControl('', [Validators.required, Validators.minLength(3)]),
  price: new FormControl(0, [Validators.required, Validators.min(0)]),
  size: new FormControl('', Validators.required)
});
```

## Testing Requirements
- Write unit tests for services and components
- Test error handling paths
- Mock HTTP requests in tests
- Test theme switching behavior

## Security Best Practices
- Never log sensitive data (passwords, tokens)
- Validate all user inputs on backend
- Use parameterized SQL queries (SQLAlchemy handles this)
- Store tokens securely in localStorage with proper key names
- Check authentication status before allowing protected actions

## Performance Guidelines
- Unsubscribe from Observables in `ngOnDestroy()`
- Use `OnPush` change detection for performance-critical components
- Lazy load routes when possible
- Optimize images (compress, use appropriate formats)
- Use pagination for large lists

## Debugging Tips
- Check browser console for frontend errors
- Check terminal running `npm run dev` for compilation errors
- Check terminal running backend for API errors
- Use `console.log()` sparingly - remove before committing
- Use browser DevTools Network tab for API debugging

## File Organization
```
frontend/src/app/
├── components/          # Reusable UI components
├── services/            # Business logic and state management
├── models/              # TypeScript interfaces and types
└── guards/              # Route guards for authentication

backend/
├── api/                 # FastAPI routes
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── services/            # Business logic
└── alembic/             # Database migrations
```

## When in Doubt
1. Check existing code for patterns
2. Use SCSS variables for all colors
3. Use TypeScript types for everything
4. Handle errors gracefully with user feedback
5. Clean up subscriptions and resources
6. Test in both light and dark mode

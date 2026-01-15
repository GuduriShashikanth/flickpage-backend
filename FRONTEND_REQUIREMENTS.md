# CineLibre Frontend Requirements

## Project Overview

Build a modern, responsive web application for CineLibre - a movie and book recommendation platform with semantic search capabilities.

---

## Tech Stack Recommendations

### Option 1: React + Vite (Recommended)
- **Framework**: React 18+
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand or React Context
- **HTTP Client**: Axios or Fetch API
- **Routing**: React Router v6
- **UI Components**: shadcn/ui or Material-UI

### Option 2: Next.js
- **Framework**: Next.js 14+ (App Router)
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **UI Components**: shadcn/ui

### Option 3: Vue.js
- **Framework**: Vue 3 + Vite
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **HTTP Client**: Axios
- **Routing**: Vue Router
- **UI Components**: Vuetify or PrimeVue

---

## Core Features

### 1. Authentication
- [ ] User registration page
- [ ] Login page
- [ ] Logout functionality
- [ ] Protected routes (redirect to login if not authenticated)
- [ ] JWT token management (localStorage/sessionStorage)
- [ ] Auto-refresh on token expiry (optional)
- [ ] User profile display

**Pages**:
- `/register` - Registration form
- `/login` - Login form
- `/profile` - User profile (protected)

---

### 2. Home/Landing Page
- [ ] Hero section with app description
- [ ] Featured movies/books carousel
- [ ] Popular items section
- [ ] Search bar (prominent)
- [ ] Quick category filters (Action, Romance, Thriller, etc.)
- [ ] Call-to-action buttons (Sign Up, Explore)

**Page**: `/`

---

### 3. Search
- [ ] Global search bar (in navbar)
- [ ] Dedicated search page
- [ ] Real-time search suggestions (debounced)
- [ ] Filter by type (Movies/Books)
- [ ] Search results with similarity scores
- [ ] Empty state when no results
- [ ] Loading states
- [ ] Search history (optional)

**Page**: `/search?q=query&type=movie`

**Features**:
- Debounce search input (300ms)
- Show loading spinner during search
- Display similarity percentage
- Click on result to view details

---

### 4. Movie Details Page
- [ ] Movie poster (large)
- [ ] Title, release date, language
- [ ] Overview/description
- [ ] Rating widget (star rating 0.5-5.0)
- [ ] User's rating (if exists)
- [ ] Similar movies section
- [ ] "Add to Watchlist" button (optional)
- [ ] Share button (optional)

**Page**: `/movies/:id`

**Components**:
- Movie poster with fallback image
- Star rating component (interactive)
- Similar items carousel
- Back button

---

### 5. Book Details Page
- [ ] Book cover thumbnail
- [ ] Title, author, published date
- [ ] Description
- [ ] Categories/genres
- [ ] Language
- [ ] Rating widget
- [ ] Similar books section
- [ ] External link to Google Books (optional)

**Page**: `/books/:id`

---

### 6. Browse Movies
- [ ] Grid/list view toggle
- [ ] Pagination or infinite scroll
- [ ] Filter by language (en, hi, te, ta, kn, ml)
- [ ] Sort options (newest, popular, top-rated)
- [ ] Movie cards with poster, title, rating
- [ ] Hover effects

**Page**: `/movies`

---

### 7. Browse Books
- [ ] Grid/list view toggle
- [ ] Pagination or infinite scroll
- [ ] Filter by category
- [ ] Sort options (newest, relevance)
- [ ] Book cards with cover, title, author
- [ ] Hover effects

**Page**: `/books`

---

### 8. Recommendations
- [ ] Personalized recommendations section
- [ ] "For You" page based on user ratings
- [ ] Popular items section
- [ ] Trending section (optional)
- [ ] Category-based recommendations

**Page**: `/recommendations`

**Sections**:
- "Recommended for You" (collaborative filtering)
- "Popular Now" (popularity-based)
- "Because you liked..." (similar items)

---

### 9. My Ratings
- [ ] List of all user ratings
- [ ] Filter by type (Movies/Books)
- [ ] Edit rating functionality
- [ ] Delete rating functionality
- [ ] Sort by date, rating
- [ ] Statistics (total ratings, average rating)

**Page**: `/my-ratings`

---

### 10. Watchlist (Optional)
- [ ] Save movies/books for later
- [ ] Remove from watchlist
- [ ] Mark as watched/read
- [ ] Notes/comments

**Page**: `/watchlist`

---

## UI/UX Requirements

### Design Principles
1. **Clean & Modern**: Minimalist design with focus on content
2. **Responsive**: Mobile-first approach (320px - 1920px)
3. **Fast**: Optimized images, lazy loading, code splitting
4. **Accessible**: WCAG 2.1 AA compliance
5. **Intuitive**: Clear navigation, consistent patterns

### Color Scheme
- **Primary**: Blue/Purple gradient (modern, tech-focused)
- **Secondary**: Orange/Yellow (accent for CTAs)
- **Background**: Dark mode support (optional but recommended)
- **Text**: High contrast for readability

### Typography
- **Headings**: Bold, modern sans-serif (Inter, Poppins, Montserrat)
- **Body**: Readable sans-serif (Inter, Open Sans, Roboto)
- **Sizes**: Responsive (16px base, scale up for headings)

### Components Needed

#### Navigation
- [ ] Navbar with logo, search, user menu
- [ ] Mobile hamburger menu
- [ ] Sticky header
- [ ] Active route highlighting

#### Cards
- [ ] Movie card (poster, title, rating, language)
- [ ] Book card (cover, title, author, rating)
- [ ] Recommendation card
- [ ] Hover effects (scale, shadow)

#### Forms
- [ ] Input fields (email, password, text)
- [ ] Validation messages
- [ ] Submit buttons with loading states
- [ ] Error handling

#### Modals/Dialogs
- [ ] Rating modal (star rating interface)
- [ ] Confirmation dialogs (delete rating)
- [ ] Image lightbox (optional)

#### Loading States
- [ ] Skeleton loaders for cards
- [ ] Spinner for search
- [ ] Progress bars (optional)
- [ ] Shimmer effects

#### Empty States
- [ ] No search results
- [ ] No ratings yet
- [ ] No recommendations
- [ ] 404 page

---

## Responsive Breakpoints

```css
/* Mobile */
@media (min-width: 320px) { }

/* Tablet */
@media (min-width: 768px) { }

/* Desktop */
@media (min-width: 1024px) { }

/* Large Desktop */
@media (min-width: 1440px) { }
```

### Layout
- **Mobile**: Single column, stacked cards
- **Tablet**: 2-3 columns grid
- **Desktop**: 4-6 columns grid, sidebar navigation

---

## State Management

### Global State (Zustand/Context)
```javascript
{
  user: {
    id: number,
    email: string,
    name: string,
    token: string
  },
  isAuthenticated: boolean,
  ratings: Rating[],
  searchHistory: string[]
}
```

### Actions
- `login(email, password)`
- `register(email, password, name)`
- `logout()`
- `setUser(user)`
- `addRating(rating)`
- `updateRating(ratingId, newRating)`
- `deleteRating(ratingId)`

---

## API Integration

### HTTP Client Setup (Axios)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app',
  timeout: 15000,
});

// Request interceptor (add token)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle errors)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### API Service Functions
```javascript
// auth.service.js
export const authService = {
  register: (email, password, name) => api.post('/auth/register', { email, password, name }),
  login: (email, password) => api.post('/auth/login', { email, password }),
  getProfile: () => api.get('/auth/me'),
};

// search.service.js
export const searchService = {
  search: (query, itemType = 'movie', limit = 10) => 
    api.get('/search/semantic', { params: { q: query, item_type: itemType, limit } }),
};

// ratings.service.js
export const ratingsService = {
  createRating: (itemId, itemType, rating) => 
    api.post('/ratings', { item_id: itemId, item_type: itemType, rating }),
  getMyRatings: (itemType) => 
    api.get('/ratings/my', { params: { item_type: itemType } }),
  deleteRating: (ratingId) => 
    api.delete(`/ratings/${ratingId}`),
};

// recommendations.service.js
export const recommendationsService = {
  getPersonalized: (limit = 20) => 
    api.get('/recommendations/personalized', { params: { limit } }),
  getSimilar: (itemType, itemId, limit = 10) => 
    api.get(`/recommendations/similar/${itemType}/${itemId}`, { params: { limit } }),
  getPopular: (limit = 20) => 
    api.get('/recommendations/popular', { params: { limit } }),
};

// movies.service.js
export const moviesService = {
  getMovie: (id) => api.get(`/movies/${id}`),
  listMovies: (skip = 0, limit = 20) => 
    api.get('/movies', { params: { skip, limit } }),
};

// books.service.js
export const booksService = {
  getBook: (id) => api.get(`/books/${id}`),
};
```

---

## Performance Optimization

### Image Optimization
- [ ] Lazy loading for images
- [ ] Placeholder images while loading
- [ ] Responsive images (srcset)
- [ ] WebP format with fallback
- [ ] CDN for static assets

### Code Splitting
- [ ] Route-based code splitting
- [ ] Dynamic imports for heavy components
- [ ] Lazy load modals/dialogs

### Caching
- [ ] Cache API responses (React Query or SWR)
- [ ] Service Worker for offline support (optional)
- [ ] LocalStorage for user preferences

### Bundle Size
- [ ] Tree shaking
- [ ] Minification
- [ ] Gzip compression
- [ ] Analyze bundle size (webpack-bundle-analyzer)

---

## SEO & Meta Tags

```html
<!-- Home Page -->
<title>CineLibre - Discover Movies & Books with AI</title>
<meta name="description" content="Find your next favorite movie or book with AI-powered recommendations" />

<!-- Movie Details -->
<title>{Movie Title} - CineLibre</title>
<meta name="description" content="{Movie Overview}" />
<meta property="og:image" content="{Poster URL}" />

<!-- Book Details -->
<title>{Book Title} by {Author} - CineLibre</title>
<meta name="description" content="{Book Description}" />
<meta property="og:image" content="{Thumbnail URL}" />
```

---

## Testing Requirements

### Unit Tests
- [ ] Component rendering
- [ ] User interactions (click, input)
- [ ] Form validation
- [ ] API service functions

### Integration Tests
- [ ] Authentication flow
- [ ] Search functionality
- [ ] Rating creation/deletion
- [ ] Navigation

### E2E Tests (Optional)
- [ ] User registration and login
- [ ] Search and view details
- [ ] Rate a movie/book
- [ ] View recommendations

**Tools**: Jest, React Testing Library, Cypress/Playwright

---

## Deployment

### Build Configuration
```bash
# Install dependencies
npm install

# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables
```env
VITE_API_BASE_URL=https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app
VITE_APP_NAME=CineLibre
VITE_APP_VERSION=1.0.0
```

### Hosting Options
1. **Vercel** (Recommended for Next.js/React)
2. **Netlify** (Great for static sites)
3. **GitHub Pages** (Free, static only)
4. **Cloudflare Pages** (Fast, global CDN)

---

## Project Structure (React + Vite)

```
cinelibre-frontend/
├── public/
│   ├── favicon.ico
│   └── logo.png
├── src/
│   ├── assets/
│   │   ├── images/
│   │   └── icons/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   └── Card.jsx
│   │   ├── movies/
│   │   │   ├── MovieCard.jsx
│   │   │   ├── MovieGrid.jsx
│   │   │   └── MovieDetails.jsx
│   │   ├── books/
│   │   │   ├── BookCard.jsx
│   │   │   ├── BookGrid.jsx
│   │   │   └── BookDetails.jsx
│   │   ├── search/
│   │   │   ├── SearchBar.jsx
│   │   │   └── SearchResults.jsx
│   │   └── ratings/
│   │       ├── RatingWidget.jsx
│   │       └── RatingsList.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Profile.jsx
│   │   ├── Search.jsx
│   │   ├── MovieDetails.jsx
│   │   ├── BookDetails.jsx
│   │   ├── Movies.jsx
│   │   ├── Books.jsx
│   │   ├── Recommendations.jsx
│   │   ├── MyRatings.jsx
│   │   └── NotFound.jsx
│   ├── services/
│   │   ├── api.js
│   │   ├── auth.service.js
│   │   ├── search.service.js
│   │   ├── ratings.service.js
│   │   ├── recommendations.service.js
│   │   ├── movies.service.js
│   │   └── books.service.js
│   ├── store/
│   │   └── useStore.js (Zustand)
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useSearch.js
│   │   └── useDebounce.js
│   ├── utils/
│   │   ├── constants.js
│   │   ├── helpers.js
│   │   └── validators.js
│   ├── styles/
│   │   └── index.css
│   ├── App.jsx
│   └── main.jsx
├── .env
├── .gitignore
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

---

## Development Timeline

### Phase 1: Setup & Authentication (Week 1)
- [ ] Project setup (Vite + React + Tailwind)
- [ ] API client configuration
- [ ] Authentication pages (Login, Register)
- [ ] Protected routes
- [ ] Basic navigation

### Phase 2: Core Features (Week 2)
- [ ] Home page with featured content
- [ ] Search functionality
- [ ] Movie/Book listing pages
- [ ] Detail pages
- [ ] Rating widget

### Phase 3: Recommendations (Week 3)
- [ ] Personalized recommendations
- [ ] Similar items
- [ ] Popular items
- [ ] My Ratings page

### Phase 4: Polish & Testing (Week 4)
- [ ] Responsive design refinement
- [ ] Loading states & error handling
- [ ] Performance optimization
- [ ] Testing
- [ ] Deployment

---

## Nice-to-Have Features (Future)

- [ ] Dark mode toggle
- [ ] Watchlist functionality
- [ ] Social sharing
- [ ] User reviews/comments
- [ ] Advanced filters (genre, year, rating)
- [ ] Infinite scroll
- [ ] Keyboard shortcuts
- [ ] PWA support (offline mode)
- [ ] Multi-language support (i18n)
- [ ] Analytics integration

---

## Resources

### Design Inspiration
- [Dribbble - Movie App Designs](https://dribbble.com/search/movie-app)
- [Netflix UI](https://www.netflix.com)
- [Goodreads](https://www.goodreads.com)
- [IMDb](https://www.imdb.com)

### UI Component Libraries
- [shadcn/ui](https://ui.shadcn.com/)
- [Material-UI](https://mui.com/)
- [Ant Design](https://ant.design/)
- [Chakra UI](https://chakra-ui.com/)

### Icons
- [Heroicons](https://heroicons.com/)
- [Lucide Icons](https://lucide.dev/)
- [React Icons](https://react-icons.github.io/react-icons/)

### Fonts
- [Google Fonts](https://fonts.google.com/)
- Recommended: Inter, Poppins, Montserrat, Roboto

---

## Getting Started

1. **Read API Documentation**: `API_REFERENCE.md`
2. **Choose Tech Stack**: React + Vite recommended
3. **Setup Project**: `npm create vite@latest cinelibre-frontend -- --template react`
4. **Install Dependencies**: Tailwind CSS, Axios, React Router, Zustand
5. **Configure API Client**: Set base URL and interceptors
6. **Start Building**: Begin with authentication pages
7. **Test Endpoints**: Use `test_all_endpoints.py` to verify API

---

## Support & Questions

- API Documentation: `API_REFERENCE.md`
- Backend Repository: [GitHub](https://github.com/GuduriShashikanth/Movie-Book-recommendation-system)
- API Base URL: `https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app`

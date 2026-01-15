# Frontend Quick Start Guide

Get your CineLibre frontend up and running in minutes!

## Prerequisites
- Node.js 18+ installed
- npm or yarn
- Code editor (VS Code recommended)

---

## Quick Setup (React + Vite + Tailwind)

### 1. Create Project
```bash
npm create vite@latest cinelibre-frontend -- --template react
cd cinelibre-frontend
```

### 2. Install Dependencies
```bash
npm install
npm install -D tailwindcss postcss autoprefixer
npm install axios react-router-dom zustand
npm install lucide-react  # For icons
```

### 3. Configure Tailwind
```bash
npx tailwindcss init -p
```

Update `tailwind.config.js`:
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Update `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 4. Create API Client

Create `src/services/api.js`:
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://amateur-meredithe-shashikanth-45dbe15b.koyeb.app',
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 5. Create Auth Service

Create `src/services/auth.service.js`:
```javascript
import api from './api';

export const authService = {
  register: async (email, password, name) => {
    const response = await api.post('/auth/register', { email, password, name });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  getProfile: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },

  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
};
```

### 6. Create Store (Zustand)

Create `src/store/useStore.js`:
```javascript
import { create } from 'zustand';
import { authService } from '../services/auth.service';

export const useStore = create((set) => ({
  user: authService.getUser(),
  isAuthenticated: authService.isAuthenticated(),
  
  setUser: (user) => set({ user, isAuthenticated: true }),
  
  logout: () => {
    authService.logout();
    set({ user: null, isAuthenticated: false });
  },
}));
```

### 7. Create Login Page

Create `src/pages/Login.jsx`:
```javascript
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/auth.service';
import { useStore } from '../store/useStore';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const setUser = useStore((state) => state.setUser);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await authService.login(email, password);
      setUser(data.user);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <div>
          <h2 className="text-3xl font-bold text-center">Sign in to CineLibre</h2>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 text-red-500 p-3 rounded">
              {error}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>

          <p className="text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="text-blue-600 hover:text-blue-500">
              Sign up
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
```

### 8. Create Home Page

Create `src/pages/Home.jsx`:
```javascript
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

export default function Home() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await api.get('/movies?limit=12');
        setMovies(response.data.movies);
      } catch (error) {
        console.error('Failed to fetch movies:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-4">
            Discover Your Next Favorite
          </h1>
          <p className="text-xl mb-8">
            AI-powered movie and book recommendations
          </p>
          <Link
            to="/search"
            className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100"
          >
            Start Exploring
          </Link>
        </div>
      </div>

      {/* Movies Section */}
      <div className="container mx-auto px-4 py-12">
        <h2 className="text-3xl font-bold mb-6">Featured Movies</h2>
        
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {movies.map((movie) => (
              <Link
                key={movie.id}
                to={`/movies/${movie.id}`}
                className="group"
              >
                <div className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition">
                  {movie.poster_url ? (
                    <img
                      src={movie.poster_url}
                      alt={movie.title}
                      className="w-full h-64 object-cover"
                    />
                  ) : (
                    <div className="w-full h-64 bg-gray-200 flex items-center justify-center">
                      <span className="text-gray-400">No Image</span>
                    </div>
                  )}
                  <div className="p-3">
                    <h3 className="font-semibold text-sm truncate">
                      {movie.title}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {movie.language?.toUpperCase()}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

### 9. Setup Routing

Update `src/App.jsx`:
```javascript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useStore } from './store/useStore';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';

// Protected Route Component
function ProtectedRoute({ children }) {
  const isAuthenticated = useStore((state) => state.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Protected routes */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <div>Profile Page</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

### 10. Run Development Server
```bash
npm run dev
```

Visit `http://localhost:5173`

---

## Next Steps

1. **Add more pages**: Register, Search, Movie Details, etc.
2. **Create components**: Navbar, MovieCard, SearchBar
3. **Add search functionality**: Use `/search/semantic` endpoint
4. **Implement ratings**: Star rating component
5. **Add recommendations**: Personalized page
6. **Style with Tailwind**: Make it beautiful!

---

## Useful Code Snippets

### Search with Debounce
```javascript
import { useState, useEffect } from 'react';

function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

// Usage in Search component
const [query, setQuery] = useState('');
const debouncedQuery = useDebounce(query, 300);

useEffect(() => {
  if (debouncedQuery) {
    // Perform search
    searchMovies(debouncedQuery);
  }
}, [debouncedQuery]);
```

### Star Rating Component
```javascript
import { Star } from 'lucide-react';

function StarRating({ rating, onRate, readonly = false }) {
  const [hover, setHover] = useState(0);

  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={readonly}
          onClick={() => !readonly && onRate(star)}
          onMouseEnter={() => !readonly && setHover(star)}
          onMouseLeave={() => !readonly && setHover(0)}
          className="focus:outline-none"
        >
          <Star
            className={`w-6 h-6 ${
              star <= (hover || rating)
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300'
            }`}
          />
        </button>
      ))}
    </div>
  );
}
```

---

## Common Issues & Solutions

### CORS Error
- API already has CORS enabled
- If issues persist, check browser console

### 401 Unauthorized
- Token expired or invalid
- Clear localStorage and login again
- Check token in API interceptor

### Images Not Loading
- Use fallback image for missing posters
- Check TMDB image URLs are correct

### Slow Search
- Implement debouncing (300ms)
- Show loading spinner
- Cache results if possible

---

## Resources

- **API Docs**: `API_REFERENCE.md`
- **Full Requirements**: `FRONTEND_REQUIREMENTS.md`
- **React Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **React Router**: https://reactrouter.com

---

## Need Help?

1. Check API documentation
2. Test endpoints with `test_all_endpoints.py`
3. Review browser console for errors
4. Check network tab for API responses

Happy coding! 🚀

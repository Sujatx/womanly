import { useState } from 'react';
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { signup, login } from '@/lib/auth-api';

export function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
  });

  const { login: authLogin } = useAuth();
  const { showToast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.email || !formData.password) {
      showToast('Please fill in all required fields', 'error');
      return;
    }
    
    if (!isLogin && !formData.full_name) {
      showToast('Please enter your full name', 'error');
      return;
    }
    
    if (formData.password.length < 6) {
      showToast('Password must be at least 6 characters', 'error');
      return;
    }
    
    setIsLoading(true);

    try {
      if (isLogin) {
        const result = await login({
          email: formData.email,
          password: formData.password,
        });
        authLogin(result.access_token, result.user);
        showToast('Welcome back!', 'success');
        window.location.hash = '#/';
      } else {
        const result = await signup({
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name,
        });
        authLogin(result.access_token, result.user);
        showToast('Account created successfully! Please check your email to verify.', 'success');
        window.location.hash = '#/';
      }
    } catch (error) {
      console.error('Auth error:', error);
      showToast(error instanceof Error ? error.message : 'Authentication failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  return (
    <section className="container mx-auto px-4 sm:px-6 py-16 md:py-24">
      <div className="max-w-md mx-auto">
        <div className="mb-10 text-center">
          <p className="text-small text-muted uppercase tracking-wide">Account</p>
          <h1 className="font-headline mb-4">{isLogin ? 'Welcome Back' : 'Create Account'}</h1>
          <p className="text-muted">
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setFormData({ email: '', password: '', full_name: '' });
              }}
              className="text-accent hover:underline font-medium"
            >
              {isLogin ? 'Create one' : 'Log in'}
            </button>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {!isLogin && (
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium mb-2">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted" />
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  required={!isLogin}
                  className="w-full pl-12 pr-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                  placeholder="Jane Doe"
                />
              </div>
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-2">
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted" />
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full pl-12 pr-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted" />
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={6}
                className="w-full pl-12 pr-12 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-muted hover:text-foreground transition-colors"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {!isLogin && (
              <p className="text-xs text-muted mt-2">Minimum 6 characters</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-foreground text-white py-3 rounded-[var(--radius-sm)] hover:bg-accent transition-colors duration-[var(--motion-micro)] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Processing...' : isLogin ? 'Log In' : 'Create Account'}
          </button>
        </form>

        {isLogin && (
          <div className="mt-6 text-center">
            <a href="#/forgot-password" className="text-sm text-muted hover:text-accent">
              Forgot your password?
            </a>
          </div>
        )}

        <div className="mt-10 pt-10 border-t border-border">
          <p className="text-xs text-muted text-center">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </section>
  );
}

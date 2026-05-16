/// <reference path="../../types/jsx.d.ts" />
import { useState } from "react";
import { Eye, EyeOff, Mail, Lock, User } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/contexts/ToastContext";
import { signup, login } from "@/lib/auth-api";

export function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    full_name: "",
  });

  const { login: authLogin } = useAuth();
  const { showToast } = useToast();

  const handleSubmit = async (e: any) => {
    e.preventDefault();

    // Validation
    if (!formData.email || !formData.password) {
      showToast("Please fill in all required fields", "error");
      return;
    }

    if (!isLogin && !formData.full_name) {
      showToast("Please enter your full name", "error");
      return;
    }

    if (isLogin) {
      if (formData.password.length < 6) {
        showToast("Password must be at least 6 characters", "error");
        return;
      }
    } else {
      // For signup enforce stronger password (score 3/4)
      if (getPasswordStrength(formData.password) < 3) {
        showToast(
          "Password too weak — use 8+ chars, upper, number and/or symbol",
          "error",
        );
        return;
      }
    }

    setIsLoading(true);

    try {
      if (isLogin) {
        const result = await login({
          email: formData.email,
          password: formData.password,
        });
        authLogin(result.access_token, result.user);
        showToast("Welcome back!", "success");
        window.location.hash = "#/";
      } else {
        const result = await signup({
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name,
        });
        authLogin(result.access_token, result.user);
        showToast(
          "Account created successfully! Please check your email to verify.",
          "success",
        );
        window.location.hash = "#/";
      }
    } catch (error) {
      console.error("Auth error:", error);
      showToast(
        error instanceof Error ? error.message : "Authentication failed",
        "error",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: any) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  // Password strength helper
  function getPasswordStrength(pw: string) {
    let score = 0;
    if (pw.length >= 8) score += 1;
    if (/[A-Z]/.test(pw)) score += 1;
    if (/[0-9]/.test(pw)) score += 1;
    if (/[^A-Za-z0-9]/.test(pw)) score += 1;
    return score; // 0-4
  }

  const strength = getPasswordStrength(formData.password);

  return (
    <section className="no-focus-outline container mx-auto px-4 sm:px-6 py-16 md:py-24">
      <div className="max-w-md mx-auto">
        <div className="mb-10 text-center">
          <p className="text-small text-muted uppercase tracking-wide">Account</p>
          <h1 className="font-headline mb-4">{isLogin ? "Welcome Back" : "Create Account"}</h1>
          <p className="text-muted">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setFormData({ email: "", password: "", full_name: "" });
              }}
              className="text-accent hover:underline font-medium"
            >
              {isLogin ? "Create one" : "Log in"}
            </button>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {!isLogin && (
            <div>
              <label
                htmlFor="full_name"
                className="block text-sm font-medium mb-2"
              >
                Full Name
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
                  <User className="w-5 h-5 text-muted" aria-hidden />
                </div>
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
              <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
                <Mail className="w-5 h-5 text-muted" aria-hidden />
              </div>
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
            <label
              htmlFor="password"
              className="block text-sm font-medium mb-2"
            >
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
                <Lock className="w-5 h-5 text-muted" aria-hidden />
              </div>
              <input
                type={showPassword ? "text" : "password"}
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
                className="absolute inset-y-0 right-0 flex items-center pr-4 text-muted hover:text-foreground transition-colors z-10"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
            {!isLogin && (
              <div className="mt-2">
                <div className="h-2 w-full bg-gray-100 rounded overflow-hidden">
                  <div
                    className={`h-full bg-gradient-to-r from-accent to-foreground transition-width`} 
                    style={{ width: `${(strength / 4) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-muted mt-2">
                  Strength: {['Very weak','Weak','Fair','Strong','Very strong'][strength]}
                </p>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-foreground text-white py-3 rounded-[var(--radius-sm)] hover:bg-accent transition-colors duration-[var(--motion-micro)] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading
              ? "Processing..."
              : isLogin
                ? "Log In"
                : "Create Account"}
          </button>
        </form>

        {isLogin && (
          <div className="mt-6 text-center">
            <a
              href="#/forgot-password"
              className="text-sm text-muted hover:text-accent"
            >
              Forgot your password?
            </a>
          </div>
        )}

        {/* footer removed from auth page - footer appears site-wide elsewhere */}
      </div>
    </section>
  );
}

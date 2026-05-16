import { getAuthToken } from './api-client';

const RAW_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = RAW_API_URL.endsWith('/api/v1') ? RAW_API_URL : `${RAW_API_URL}/api/v1`;

interface SignupData {
  email: string;
  password: string;
  full_name: string;
}

interface LoginData {
  email: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    full_name: string;
    is_verified: boolean;
  };
}

export async function signup(data: SignupData): Promise<AuthResponse> {
  console.log('🔵 Signup attempt:', { email: data.email, full_name: data.full_name });
  
  const response = await fetch(`${API_URL}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  console.log('🔵 Signup response status:', response.status);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Signup failed' }));
    console.error('❌ Signup failed:', error);
    throw new Error(error.detail || 'Signup failed');
  }

  const result = await response.json();
  console.log('✅ Signup successful:', { user: result.user });
  
  // Store tokens
  localStorage.setItem('auth_token', result.access_token);
  localStorage.setItem('refresh_token', result.refresh_token);
  
  return result;
}

export async function login(data: LoginData): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(error.detail || 'Invalid credentials');
  }

  const result = await response.json();
  
  // Store tokens
  localStorage.setItem('auth_token', result.access_token);
  localStorage.setItem('refresh_token', result.refresh_token);
  
  return result;
}

export async function verifyEmail(token: string): Promise<{ message: string }> {
  const response = await fetch(`${API_URL}/auth/verify-email?token=${encodeURIComponent(token)}`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Verification failed' }));
    throw new Error(error.detail || 'Verification failed');
  }

  return response.json();
}

export async function getCurrentUser() {
  const token = getAuthToken();
  if (!token) return null;

  const response = await fetch(`${API_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    return null;
  }

  return response.json();
}

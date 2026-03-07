import { useEffect, useState } from 'react';
import { User as UserIcon, Mail, Package, Heart, LogOut, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { apiRequest } from '@/lib/api-client';

export function ProfilePage() {
  const { user, isAuthenticated, logout, updateUser } = useAuth();
  const { showToast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [isSendingVerification, setIsSendingVerification] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
  });

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.hash = '#/auth';
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    async function refreshCurrentUser() {
      try {
        const latestUser = await apiRequest<{
          id: number;
          email: string;
          full_name: string;
          is_verified: boolean;
        }>('/auth/me');
        updateUser(latestUser);
      } catch (error) {
        console.error('[Profile] Failed to refresh user state:', error);
      }
    }

    refreshCurrentUser();
  }, [isAuthenticated]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement profile update API call
    showToast('Profile update feature coming soon!', 'info');
    setIsEditing(false);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleResendVerification = async () => {
    console.log('[Profile] === Starting Verification Email Request ===');
    console.log('[Profile] User state:', user);
    console.log('[Profile] IsAuthenticated:', isAuthenticated);
    
    const token = localStorage.getItem('auth_token');
    console.log('[Profile] Token exists:', !!token);
    console.log('[Profile] Token preview:', token ? token.substring(0, 30) + '...' : 'null');
    
    setIsSendingVerification(true);
    try {
      console.log('[Profile] Making POST request to /auth/resend-verification');
      const response = await apiRequest<{ status: string; message: string }>('/auth/resend-verification', {
        method: 'POST',
      });
      console.log('[Profile] Success! Response:', response);
      showToast('Verification email sent! Check your email inbox.', 'success');
    } catch (error) {
      console.error('[Profile] ERROR caught:', error);
      console.error('[Profile] Error type:', error instanceof Error ? error.constructor.name : typeof error);
      const message = error instanceof Error ? error.message : 'Failed to send verification email';
      console.error('[Profile] Error message:', message);
      
      // Don't show error if already redirecting to auth
      if (!window.location.hash.includes('#/auth')) {
        showToast(message, 'error');
      }
    } finally {
      setIsSendingVerification(false);
      console.log('[Profile] === Verification Email Request Complete ===');
    }
  };

  const handleLogout = () => {
    logout();
    showToast('Logged out successfully', 'success');
  };

  if (!user) {
    return null;
  }

  return (
    <section className="container mx-auto px-6 py-16 md:py-24">
      <div className="max-w-4xl mx-auto">
        <div className="mb-10">
          <p className="text-small text-muted uppercase tracking-wide">Account</p>
          <h1 className="font-headline text-4xl">My Profile</h1>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Sidebar */}
          <aside className="space-y-2">
            <a
              href="#/profile"
              className="flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] bg-accent/10 text-accent"
            >
              <UserIcon className="w-5 h-5" />
              <span>Profile</span>
            </a>
            <a
              href="#/orders"
              className="flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] hover:bg-secondary transition-colors"
            >
              <Package className="w-5 h-5" />
              <span>Orders</span>
            </a>
            <a
              href="#/wishlist"
              className="flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] hover:bg-secondary transition-colors"
            >
              <Heart className="w-5 h-5" />
              <span>Wishlist</span>
            </a>
            <a
              href="#/addresses"
              className="flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] hover:bg-secondary transition-colors"
            >
              <Mail className="w-5 h-5" />
              <span>Addresses</span>
            </a>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] hover:bg-red-50 hover:text-red-600 transition-colors text-left"
            >
              <LogOut className="w-5 h-5" />
              <span>Log Out</span>
            </button>
          </aside>

          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="rounded-[var(--radius-lg)] border border-border bg-white p-6 md:p-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-medium">Personal Information</h2>
                {!isEditing && (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="text-accent hover:underline text-sm"
                  >
                    Edit
                  </button>
                )}
              </div>

              {isEditing ? (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label htmlFor="full_name" className="block text-sm font-medium mb-2">
                      Full Name
                    </label>
                    <input
                      type="text"
                      id="full_name"
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                    />
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      disabled
                      className="w-full px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-secondary cursor-not-allowed"
                    />
                    <p className="text-xs text-muted mt-2">Email cannot be changed</p>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="submit"
                      className="px-6 py-2 bg-foreground text-white rounded-[var(--radius-sm)] hover:bg-accent transition-colors"
                    >
                      Save Changes
                    </button>
                    <button
                      type="button"
                      onClick={() => setIsEditing(false)}
                      className="px-6 py-2 border border-border rounded-[var(--radius-sm)] hover:border-accent transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-6">
                  <div>
                    <p className="text-sm text-muted mb-1">Full Name</p>
                    <p className="text-lg">{user.full_name}</p>
                  </div>

                  <div>
                    <p className="text-sm text-muted mb-1">Email</p>
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex-1">
                        <p className="text-lg">{user.email}</p>
                        {user.is_verified ? (
                          <div className="flex items-center gap-2 text-sm text-green-600 mt-2">
                            <CheckCircle className="w-4 h-4" />
                            <span>Verified</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2 text-sm text-yellow-600 mt-2">
                            <AlertCircle className="w-4 h-4" />
                            <span>Not verified</span>
                          </div>
                        )}
                      </div>
                      {!user.is_verified && (
                        <button
                          onClick={handleResendVerification}
                          disabled={isSendingVerification}
                          className="px-4 py-2 bg-accent text-white rounded-[var(--radius-sm)] hover:bg-accent/90 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {isSendingVerification ? 'Sending...' : 'Verify Email'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Additional Sections */}
            <div className="mt-6 rounded-[var(--radius-lg)] border border-border bg-white p-6 md:p-8">
              <h2 className="text-2xl font-medium mb-6">Account Security</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-border">
                  <div>
                    <p className="font-medium">Password</p>
                    <p className="text-sm text-muted">Last changed 30 days ago</p>
                  </div>
                  <button className="text-accent hover:underline text-sm">Change</button>
                </div>
                <div className="flex items-center justify-between py-3">
                  <div>
                    <p className="font-medium">Two-Factor Authentication</p>
                    <p className="text-sm text-muted">Add an extra layer of security</p>
                  </div>
                  <button className="text-accent hover:underline text-sm">Enable</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

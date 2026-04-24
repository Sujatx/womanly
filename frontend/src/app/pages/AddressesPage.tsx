import { useEffect, useState } from 'react';
import { Plus, MapPin, Trash2, Edit2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';

interface Address {
  id: number;
  user_id: number;
  full_name: string;
  phone: string;
  street_address: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}

export function AddressesPage() {
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.hash = '#/auth';
      return;
    }
    
    // TODO: Fetch addresses from API
    // For now, show empty state
    setLoading(false);
  }, [isAuthenticated]);

  const handleAddAddress = () => {
    showToast('Address management feature coming soon!', 'info');
    setShowForm(false);
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <section className="container mx-auto px-4 sm:px-6 py-16 md:py-24">
      <div className="max-w-4xl mx-auto">
        <div className="mb-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <p className="text-small text-muted uppercase tracking-wide">Account</p>
            <h1 className="font-headline">Shipping Addresses</h1>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex w-full sm:w-auto items-center justify-center gap-2 px-4 py-2 bg-foreground text-white rounded-[var(--radius-sm)] hover:bg-accent transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Address
          </button>
        </div>

        {showForm && (
          <div className="mb-8 rounded-[var(--radius-lg)] border border-border bg-white p-6">
            <h2 className="font-headline mb-6">New Address</h2>
            <form onSubmit={(e) => { e.preventDefault(); handleAddAddress(); }} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Full Name</label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Phone</label>
                  <input
                    type="tel"
                    required
                    className="w-full px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Street Address</label>
                <input
                  type="text"
                  required
                  className="w-full px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">City</label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">State/Province</label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Postal Code</label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Country</label>
                <select
                  required
                  className="w-full px-4 py-3 border border-border rounded-[var(--radius-sm)] bg-background focus:border-accent focus:outline-none transition-colors"
                >
                  <option value="IN">India</option>
                  <option value="US">United States</option>
                  <option value="GB">United Kingdom</option>
                  <option value="CA">Canada</option>
                  <option value="AU">Australia</option>
                </select>
              </div>

              <div className="flex items-center gap-2">
                <input type="checkbox" id="is_default" className="rounded" />
                <label htmlFor="is_default" className="text-sm">
                  Set as default address
                </label>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <button
                  type="submit"
                  className="w-full sm:w-auto px-6 py-2 bg-foreground text-white rounded-[var(--radius-sm)] hover:bg-accent transition-colors"
                >
                  Save Address
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="w-full sm:w-auto px-6 py-2 border border-border rounded-[var(--radius-sm)] hover:border-accent transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {loading ? (
          <p className="text-muted">Loading addresses...</p>
        ) : addresses.length === 0 ? (
          <div className="rounded-[var(--radius-lg)] border border-border bg-white p-10 text-center">
            <MapPin className="mx-auto mb-4 h-10 w-10 text-muted" />
            <p className="text-muted mb-3">No saved addresses</p>
            <p className="text-small text-muted">Add a shipping address to speed up checkout</p>
          </div>
        ) : (
          <div className="space-y-4">
            {addresses.map((address) => (
              <div
                key={address.id}
                className="rounded-[var(--radius-lg)] border border-border bg-white p-6 relative"
              >
                {address.is_default && (
                  <span className="absolute top-4 right-4 text-xs bg-accent text-white px-3 py-1 rounded-full max-w-[40%] text-center">
                    Default
                  </span>
                )}
                <div className="pr-0 sm:pr-24">
                  <h3 className="font-medium mb-2">{address.full_name}</h3>
                  <p className="text-muted text-sm leading-relaxed">
                    {address.street_address}<br />
                    {address.city}, {address.state} {address.postal_code}<br />
                    {address.country}<br />
                    Phone: {address.phone}
                  </p>
                </div>
                <div className="flex flex-wrap gap-3 mt-4">
                  <button className="flex items-center gap-2 text-sm text-accent hover:underline">
                    <Edit2 className="w-4 h-4" />
                    Edit
                  </button>
                  <button className="flex items-center gap-2 text-sm text-red-600 hover:underline">
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

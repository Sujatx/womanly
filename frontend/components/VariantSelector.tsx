// components/VariantSelector.tsx
// Button-based variant selector to maximize visibility and reduce errors.
// - Options render as grids of buttons (e.g., Size, Color).
// - Disabled states show unavailable combos without allowing selection.

'use client';

type Option = { name: string; values: string[] };

// disabledValues: map option name -> array of disabled values (e.g., { Size: ["XL"] })
export function VariantSelector({
  options,
  selected,
  onChange,
  disabledValues = {},
  labelMap = {},
}: {
  options: Option[];
  selected: Record<string, string>;
  onChange: (name: string, value: string) => void;
  disabledValues?: Record<string, string[]>;
  labelMap?: Record<string, string>;
}) {
  if (!options?.length) return null;

  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      {options.map((opt) => {
        const pretty = labelMap[opt.name] || opt.name;
        const disabledSet = new Set(disabledValues[opt.name] || []);
        return (
          <div key={opt.name}>
            <p style={{ 
              fontSize: '0.7rem', 
              fontWeight: 900, 
              textTransform: 'uppercase', 
              letterSpacing: '0.1em',
              marginBottom: '0.75rem',
              color: 'var(--muted)'
            }}>{pretty}</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
              {opt.values.map((value) => {
                const isSelected = selected[opt.name] === value;
                const isDisabled = disabledSet.has(value);
                return (
                  <button
                    key={value}
                    type="button"
                    disabled={isDisabled}
                    aria-pressed={isSelected}
                    onClick={() => onChange(opt.name, value)}
                    style={{
                      padding: '0.6rem 1.5rem',
                      borderRadius: 'var(--radius-pill)',
                      border: isSelected ? '2px solid var(--fg)' : '1px solid var(--border)',
                      background: isSelected ? 'var(--fg)' : 'transparent',
                      color: isSelected ? 'white' : isDisabled ? 'var(--muted)' : 'var(--fg)',
                      cursor: isDisabled ? 'not-allowed' : 'pointer',
                      fontSize: '0.8rem',
                      fontWeight: 800,
                      textTransform: 'uppercase',
                      transition: 'all 0.2s',
                      opacity: isDisabled ? 0.4 : 1
                    }}
                  >
                    {value}
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

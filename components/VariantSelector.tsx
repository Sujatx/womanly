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
  labelMap?: Record<string, string>; // optional human labels per option (e.g., { Color: 'Color' })
}) {
  if (!options?.length) return null;

  return (
    <div className="space-y-3">
      {options.map((opt) => {
        const pretty = labelMap[opt.name] || opt.name;
        const disabledSet = new Set(disabledValues[opt.name] || []);
        return (
          <div key={opt.name}>
            <p className="text-xs muted" style={{ marginBottom: '0.25rem' }}>{pretty}</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
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
                    className="rounded"
                    style={{
                      padding: '0.4rem 0.75rem',
                      border: isSelected ? '2px solid #111' : '1px solid #ddd',
                      background: isDisabled ? '#f2f2f2' : '#fff',
                      color: isDisabled ? '#9a9a9a' : '#111',
                      cursor: isDisabled ? 'not-allowed' : 'pointer',
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

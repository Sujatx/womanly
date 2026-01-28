// lib/plp-transform.ts
export type CardLike = { title: string; price: { amount: string; currencyCode: string } };

export function filterByPrice<T extends CardLike>(items: T[], min?: number, max?: number) {
  return items.filter((i) => {
    const p = Number(i.price.amount);
    if (!Number.isFinite(p)) return false;
    if (min != null && p < min) return false;
    if (max != null && p > max) return false;
    return true;
  });
}

export function sortCards<T extends CardLike>(items: T[], sort: string) {
  const clone = [...items];
  switch (sort) {
    case 'price-asc':
      clone.sort((a,b)=>Number(a.price.amount)-Number(b.price.amount)); break;
    case 'price-desc':
      clone.sort((a,b)=>Number(b.price.amount)-Number(a.price.amount)); break;
    case 'title-asc':
      clone.sort((a,b)=>a.title.localeCompare(b.title)); break;
    default:
      return items; // relevance = original
  }
  return clone;
}

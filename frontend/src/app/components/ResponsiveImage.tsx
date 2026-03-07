import type { ImgHTMLAttributes } from 'react';

type ResponsiveImageProps = Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'alt'> & {
  src: string;
  alt: string;
  sizes?: string;
  widths?: number[];
};

function withQueryParams(url: string, params: Record<string, string | number>) {
  const [base, hash = ''] = url.split('#');
  const [path, query = ''] = base.split('?');
  const searchParams = new URLSearchParams(query);
  Object.entries(params).forEach(([key, value]) => searchParams.set(key, String(value)));
  const built = `${path}?${searchParams.toString()}`;
  return hash ? `${built}#${hash}` : built;
}

export function ResponsiveImage({
  src,
  alt,
  sizes = '(max-width: 768px) 100vw, 50vw',
  widths = [320, 640, 960, 1280],
  loading = 'lazy',
  decoding = 'async',
  ...props
}: ResponsiveImageProps) {
  const srcSet = widths.map((width) => `${withQueryParams(src, { w: width })} ${width}w`).join(', ');
  const webpSet = widths
    .map((width) => `${withQueryParams(src, { w: width, format: 'webp' })} ${width}w`)
    .join(', ');

  return (
    <picture>
      <source type="image/webp" srcSet={webpSet} sizes={sizes} />
      <img
        src={src}
        srcSet={srcSet}
        sizes={sizes}
        alt={alt}
        loading={loading}
        decoding={decoding}
        {...props}
      />
    </picture>
  );
}

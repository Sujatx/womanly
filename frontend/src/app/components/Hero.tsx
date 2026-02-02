import { motion } from 'motion/react';

interface HeroProps {
  variant?: 'image-left' | 'image-right' | 'full-bleed';
  image: string;
  heading: string;
  subheading?: string;
  ctaText: string;
  ctaHref: string;
}

export function Hero({
  variant = 'image-left',
  image,
  heading,
  subheading,
  ctaText,
  ctaHref
}: HeroProps) {
  if (variant === 'full-bleed') {
    return (
      <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0">
          <img
            src={image}
            alt=""
            className="w-full h-full object-cover"
            aria-hidden="true"
          />
          <div className="absolute inset-0 bg-black/30" />
        </div>
        <div className="relative z-10 text-center text-white px-6">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.2, 0.8, 0.2, 1] }}
            className="font-headline mb-6"
          >
            {heading}
          </motion.h1>
          {subheading && (
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1, ease: [0.2, 0.8, 0.2, 1] }}
              className="text-xl mb-8 max-w-2xl mx-auto"
            >
              {subheading}
            </motion.p>
          )}
          <motion.a
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2, ease: [0.2, 0.8, 0.2, 1] }}
            href={ctaHref}
            className="inline-block bg-white text-foreground px-8 py-4 rounded-[var(--radius-sm)] hover:bg-accent hover:text-white transition-colors duration-[var(--motion-micro)]"
          >
            {ctaText}
          </motion.a>
        </div>
      </section>
    );
  }

  const isImageLeft = variant === 'image-left';

  return (
    <section className="container mx-auto px-6 py-16 md:py-24">
      <div className={`grid md:grid-cols-2 gap-12 items-center ${isImageLeft ? '' : 'md:grid-flow-dense'}`}>
        {/* Image */}
        <motion.div
          initial={{ opacity: 0, x: isImageLeft ? -20 : 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, ease: [0.2, 0.8, 0.2, 1] }}
          className={`relative ${isImageLeft ? '' : 'md:col-start-2'}`}
        >
          <div className="aspect-[4/5] rounded-[var(--radius-lg)] overflow-hidden shadow-[var(--shadow-soft)]">
            <img
              src={image}
              alt=""
              className="w-full h-full object-cover"
              aria-hidden="true"
            />
          </div>
        </motion.div>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, x: isImageLeft ? 20 : -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1, ease: [0.2, 0.8, 0.2, 1] }}
          className={isImageLeft ? '' : 'md:col-start-1'}
        >
          <h1 className="font-headline mb-6">
            {heading}
          </h1>
          {subheading && (
            <p className="text-lg text-muted mb-8 leading-relaxed">
              {subheading}
            </p>
          )}
          <a
            href={ctaHref}
            className="inline-block bg-foreground text-white px-8 py-4 rounded-[var(--radius-sm)] hover:bg-accent transition-colors duration-[var(--motion-micro)]"
          >
            {ctaText}
          </a>
        </motion.div>
      </div>
    </section>
  );
}

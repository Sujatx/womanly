export function AboutPage() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative h-[60vh] min-h-[500px] flex items-center justify-center">
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1487412912498-0447578fcca8?w=1600&q=90"
            alt="About Womanly"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/40" />
        </div>
        <div className="relative z-10 text-center text-white px-6">
          <h1 className="font-headline text-5xl md:text-6xl mb-6">Our Story</h1>
          <p className="text-xl md:text-2xl max-w-3xl mx-auto">
            Crafting timeless pieces for the modern woman
          </p>
        </div>
      </section>

      {/* Mission Section */}
      <section className="container mx-auto px-6 py-16 md:py-24">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-small text-muted uppercase tracking-wide mb-4">Our Mission</p>
          <h2 className="font-headline text-4xl mb-6">Quality Over Quantity</h2>
          <p className="text-lg text-muted leading-relaxed mb-8">
            At Womanly, we believe in creating pieces that transcend seasonal trends. Each garment
            is carefully designed and ethically produced, ensuring that you invest in quality that
            lasts. Our commitment to sustainability and craftsmanship is woven into every thread.
          </p>
          <p className="text-lg text-muted leading-relaxed">
            We partner with skilled artisans and use responsibly sourced materials to create
            collections that honor both people and planet. From our studio to your wardrobe, every
            step reflects our dedication to conscious fashion.
          </p>
        </div>
      </section>

      {/* Values Grid */}
      <section className="bg-secondary py-16 md:py-24">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-accent/10 flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-accent"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"
                  />
                </svg>
              </div>
              <h3 className="font-headline text-2xl mb-4">Sustainable</h3>
              <p className="text-muted">
                Ethically sourced materials and eco-friendly production processes that minimize our
                environmental impact.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-accent/10 flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-accent"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="font-headline text-2xl mb-4">Quality First</h3>
              <p className="text-muted">
                Every piece is crafted with meticulous attention to detail, ensuring durability and
                timeless style.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-accent/10 flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-accent"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                  />
                </svg>
              </div>
              <h3 className="font-headline text-2xl mb-4">Made with Care</h3>
              <p className="text-muted">
                Working with skilled artisans who are fairly compensated and work in safe,
                dignified conditions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Journey Section */}
      <section className="container mx-auto px-6 py-16 md:py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <p className="text-small text-muted uppercase tracking-wide mb-4">Since 2020</p>
            <h2 className="font-headline text-4xl mb-6">Our Journey</h2>
            <p className="text-muted leading-relaxed mb-4">
              Womanly was born from a simple idea: that fashion should be both beautiful and
              responsible. Founded in 2020, we started as a small studio with a vision to create
              clothing that women could feel good about wearing.
            </p>
            <p className="text-muted leading-relaxed mb-4">
              Today, we've grown into a community of conscious consumers who believe that style and
              sustainability can coexist. Our collections are sold in boutiques worldwide, but our
              values remain the same.
            </p>
            <p className="text-muted leading-relaxed">
              Thank you for being part of our journey. Together, we're proving that fashion can be a
              force for good.
            </p>
          </div>
          <div className="aspect-[4/5] rounded-[var(--radius-lg)] overflow-hidden">
            <img
              src="https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800&q=90"
              alt="Womanly studio"
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-foreground text-white py-16 md:py-24">
        <div className="container mx-auto px-6 text-center">
          <h2 className="font-headline text-4xl mb-6">Join Our Community</h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto opacity-90">
            Be the first to know about new collections, exclusive offers, and sustainable fashion
            tips.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Your email address"
              className="flex-1 px-4 py-3 rounded-[var(--radius-sm)] text-foreground"
            />
            <button className="px-6 py-3 bg-accent text-white rounded-[var(--radius-sm)] hover:bg-accent/90 transition-colors">
              Subscribe
            </button>
          </div>
        </div>
      </section>
    </>
  );
}

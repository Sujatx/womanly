// Temporary local JSX declaration to suppress editor errors when React types are not installed.
// This allows intrinsic JSX elements without importing full `@types/react` during development.

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

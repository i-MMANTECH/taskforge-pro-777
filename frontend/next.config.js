/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: false,  // Permanently disable Turbopack to avoid ESM/CJS conflicts
  },
  transpilePackages: ['@tanstack/react-query', 'sonner'],  // Transpile problematic deps
};

module.exports = nextConfig;
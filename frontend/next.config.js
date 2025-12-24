const path = require('path')
const webpack = require('webpack')
const createNextIntlPlugin = require('next-intl/plugin')

const withNextIntl = createNextIntlPlugin('./i18n.ts')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  transpilePackages: ['@react-three/drei', '@react-three/fiber'],
  webpack: (config, { isServer }) => {
    // Alias for react-three-fiber to @react-three/fiber
    const aliases = {
      'react-three-fiber': '@react-three/fiber',
      // Stub out DeviceOrientationControls which doesn't exist in three.js 0.160.1
      'three/examples/jsm/controls/DeviceOrientationControls': path.resolve(__dirname, 'webpack-stubs/DeviceOrientationControls.js'),
      // Stub out stats.min which is not exported in three.js 0.160.1
      'three/examples/js/libs/stats.min': path.resolve(__dirname, 'webpack-stubs/stats.min.js'),
      // Force resolution of use-asset
      'use-asset': path.resolve(__dirname, 'node_modules/use-asset'),
    }

    // On client side, force axios to use browser build
    if (!isServer) {
      aliases['axios'] = path.resolve(__dirname, 'node_modules/axios/dist/browser/axios.cjs')
    }

    config.resolve.alias = {
      ...config.resolve.alias,
      ...aliases,
    }

    // Make sure webpack can resolve ESM modules from three.js
    // Also stub Node.js modules that don't exist in browser
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      path: false,
      crypto: false,
      http2: false, // http2 is Node.js only, not available in browser
      http: false, // Use browser's fetch instead
      https: false,
      zlib: false,
      stream: false,
      util: false,
    }

    // Ensure webpack resolves three.js examples properly
    config.resolve.modules = [
      ...(config.resolve.modules || []),
      'node_modules',
    ]

    // Handle ESM imports from three.js - only on client side
    if (!isServer) {
      config.resolve.conditionNames = ['import', 'require', 'default']
      // Force axios to use browser build on client side (already set in aliases above)
    }

    // Don't exclude drei from server-side if it's needed for compilation
    // The dynamic import with ssr:false should handle this, but we need use-asset available
    // Only exclude three.js core, not drei/fiber which need to be processed
    if (isServer) {
      config.externals = config.externals || []
      // Only externalize three.js core, keep drei and fiber for processing
      config.externals.push('three')
    }

    return config
  },
}

module.exports = withNextIntl(nextConfig)


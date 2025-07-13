import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    devIndicators: false,
    // output: 'export',
    trailingSlash: true,
    images: {
        unoptimized: true,
    },

    turbopack: {
        rules: {},
    },

    webpack: (config, { dev, isServer }) => {
        if (dev && !isServer) {
            config.devtool = false;
        }
        return config;
    },
}

export default nextConfig;
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    devIndicators: false,

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
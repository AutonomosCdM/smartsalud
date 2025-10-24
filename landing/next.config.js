/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  env: {
    NEXT_PUBLIC_ELEVENLABS_API_KEY: process.env.NEXT_PUBLIC_ELEVENLABS_API_KEY,
    NEXT_PUBLIC_AGENT_ID: process.env.NEXT_PUBLIC_AGENT_ID,
  },
}

module.exports = nextConfig

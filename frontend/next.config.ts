import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // async headers() {
  //   return [
  //     {
  //       source: '/(.*)',
  //       headers: [
  //         {
  //           key: 'Content-Security-Policy',
  //           value: [
  //             "frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com",
  //             "connect-src 'self' https://www.youtube.com https://www.youtube-nocookie.com https://youtubei.googleapis.com",
  //             "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.youtube.com",
  //             "img-src 'self' data: https: https://img.youtube.com https://i.ytimg.com"
  //           ].join('; ')
  //         }
  //       ]
  //     }
  //   ]
  // },

//  async headers() {
//     return [
//       {
//         source: "/(.*)", // apply to all routes
//         headers: [
//           // remove X-Frame-Options DENY if you want to allow iframes
//           // or change to SAMEORIGIN if you only want self-embedding
//           {
//             key: "X-Frame-Options",
//             value: "SAMEORIGIN", 
//           },
//           {
//             key: "Content-Security-Policy",
//             value: "frame-ancestors 'self' https://www.youtube.com",
//           },
//         ],
//       },
//     ]
//   },

};

export default nextConfig;

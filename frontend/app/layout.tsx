import type React from "react"
import "./globals.css"
import type { Metadata } from "next"
import { Inter, Poppins, JetBrains_Mono } from "next/font/google"
import { cn } from "@/lib/utils"

// Font configurations
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  preload: true,
})

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-poppins",
  display: "swap",
  preload: true,
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
  preload: false, // Only load when needed
})

// Metadata configuration
export const metadata: Metadata = {
  title: {
    default: "Salesdok - Your AI-Powered Sales Assistant",
    template: "%s | Salesdok",
  },
  description:
    "Transform your website into a 24/7 sales machine with AI-powered conversations that convert. Deploy intelligent RAG-powered salesdoks that know your products inside out.",
  keywords: [
    "AI chatbot",
    "sales automation",
    "RAG chatbot",
    "customer service AI",
    "website chatbot",
    "sales assistant",
    "conversational AI",
    "lead generation",
    "customer support",
  ],
  authors: [{ name: "salesdok Team" }],
  creator: "salesdok",
  publisher: "salesdok",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "https://salesdok.com"),
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "/",
    title: "Salesdok - AI-Powered Sales Assistant",
    description: "Transform your website into a 24/7 sales machine with AI-powered conversations that convert.",
    siteName: "salesdok",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "salesdok - AI-Powered Sales Assistant",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Salesdok - AI-Powered Sales Assistant",
    description: "Transform your website into a 24/7 sales machine with AI-powered conversations that convert.",
    images: ["/og-image.png"],
    creator: "@salesdok",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: {
    google: process.env.GOOGLE_SITE_VERIFICATION,
    yandex: process.env.YANDEX_VERIFICATION,
    yahoo: process.env.YAHOO_VERIFICATION,
  },
  category: "technology",
  classification: "Business Software",
  referrer: "origin-when-cross-origin",
  colorScheme: "light dark",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#119da4" },
    { media: "(prefers-color-scheme: dark)", color: "#0c7489" },
  ],
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 5,
    userScalable: true,
  },
  manifest: "/manifest.json",
  icons: {
    icon: [
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-96x96.png", sizes: "96x96", type: "image/png" },
    ],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
    other: [
      {
        rel: "mask-icon",
        url: "/safari-pinned-tab.svg",
        color: "#119da4",
      },
    ],
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "salesdok",
  },
  applicationName: "salesdok",
  generator: "Next.js",
  abstract: "AI-powered sales assistant for websites",
  archives: [],
  assets: [],
  bookmarks: [],
}

// Structured Data (JSON-LD)
const structuredData = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "salesdok",
  description: "AI-powered sales assistant that transforms websites into 24/7 sales machines",
  url: "https://salesdok.com",
  applicationCategory: "BusinessApplication",
  operatingSystem: "Web",
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "USD",
    description: "Free trial avcomlable",
  },
  author: {
    "@type": "Organization",
    name: "salesdok",
    url: "https://salesdok.com",
  },
  publisher: {
    "@type": "Organization",
    name: "salesdok",
    url: "https://salesdok.com",
  },
  aggregateRating: {
    "@type": "AggregateRating",
    ratingValue: "4.9",
    ratingCount: "2847",
    bestRating: "5",
    worstRating: "1",
  },
  featureList: [
    "AI-powered conversations",
    "RAG technology",
    "Document processing",
    "Website integration",
    "Real-time analytics",
    "Multi-language support",
  ],
}

interface RootLayoutProps {
  children: React.ReactNode
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html
      lang="en"
      className={cn("scroll-smooth", inter.variable, poppins.variable, jetbrainsMono.variable)}
      suppressHydrationWarning
    >
      <head>
        {/* Preconnect to external domains */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />

        {/* DNS prefetch for performance */}
        <link rel="dns-prefetch" href="https://api.salesdok.com" />
        <link rel="dns-prefetch" href="https://cdn.salesdok.com" />

        {/* Structured Data */}
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />

        {/* Additional meta tags */}
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="salesdok" />
        <meta name="application-name" content="salesdok" />
        <meta name="msapplication-TileColor" content="#119da4" />
        <meta name="msapplication-config" content="/browserconfig.xml" />
        <meta name="theme-color" content="#119da4" />

        {/* Security headers */}
        <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
        <meta httpEquiv="X-Frame-Options" content="DENY" />
        <meta httpEquiv="X-XSS-Protection" content="1; mode=block" />
        <meta httpEquiv="Referrer-Policy" content="strict-origin-when-cross-origin" />

        {/* Performance hints */}
        <link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        <link rel="preload" href="/fonts/poppins-var.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />

        {/* Critical CSS (if any) */}
        <style
          dangerouslySetInnerHTML={{
            __html: `
            /* Critical above-the-fold styles */
            body { 
              font-family: 'Inter', system-ui, sans-serif; 
              line-height: 1.6;
              -webkit-font-smoothing: antialiased;
              -moz-osx-font-smoothing: grayscale;
            }
            .loading-screen {
              position: fixed;
              top: 0;
              left: 0;
              width: 100%;
              height: 100%;
              background: #ffffff;
              display: flex;
              align-items: center;
              justify-content: center;
              z-index: 9999;
            }
          `,
          }}
        />
      </head>
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          "selection:bg-primary/20 selection:text-primary-foreground",
        )}
        suppressHydrationWarning
      >
        {/* Skip to main content for accessibility */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md focus:shadow-lg"
        >
          Skip to main content
        </a>

        {/* Main content wrapper */}
        <div id="main-content" className="relative">
          {children}
        </div>

        {/* Analytics Scripts */}
        {process.env.NODE_ENV === "production" && (
          <>
            {/* Google Analytics */}
            {process.env.NEXT_PUBLIC_GA_ID && (
              <>
                <script async src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`} />
                <script
                  dangerouslySetInnerHTML={{
                    __html: `
                      window.dataLayer = window.dataLayer || [];
                      function gtag(){dataLayer.push(arguments);}
                      gtag('js', new Date());
                      gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}', {
                        page_title: document.title,
                        page_location: window.location.href,
                      });
                    `,
                  }}
                />
              </>
            )}

            {/* Hotjar */}
            {process.env.NEXT_PUBLIC_HOTJAR_ID && (
              <script
                dangerouslySetInnerHTML={{
                  __html: `
                    (function(h,o,t,j,a,r){
                      h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
                      h._hjSettings={hjid:${process.env.NEXT_PUBLIC_HOTJAR_ID},hjsv:6};
                      a=o.getElementsByTagName('head')[0];
                      r=o.createElement('script');r.async=1;
                      r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
                      a.appendChild(r);
                    })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
                  `,
                }}
              />
            )}

            {/* Intercom or other chat widgets */}
            {process.env.NEXT_PUBLIC_INTERCOM_APP_ID && (
              <script
                dangerouslySetInnerHTML={{
                  __html: `
                    window.intercomSettings = {
                      app_id: "${process.env.NEXT_PUBLIC_INTERCOM_APP_ID}"
                    };
                    (function(){var w=window;var ic=w.Intercom;if(typeof ic==="function"){ic('reattach_activator');ic('update',w.intercomSettings);}else{var d=document;var i=function(){i.c(arguments);};i.q=[];i.c=function(args){i.q.push(args);};w.Intercom=i;var l=function(){var s=d.createElement('script');s.type='text/javascript';s.async=true;s.src='https://widget.intercom.io/widget/${process.env.NEXT_PUBLIC_INTERCOM_APP_ID}';var x=d.getElementsByTagName('script')[0];x.parentNode.insertBefore(s,x);};if(document.readyState==='complete'){l();}else if(w.attachEvent){w.attachEvent('onload',l);}else{w.addEventListener('load',l,false);}}})();
                  `,
                }}
              />
            )}
          </>
        )}

        {/* Service Worker Registration */}
        {process.env.NODE_ENV === "production" && (
          <script
            dangerouslySetInnerHTML={{
              __html: `
                if ('serviceWorker' in navigator) {
                  window.addEventListener('load', function() {
                    navigator.serviceWorker.register('/sw.js')
                      .then(function(registration) {
                        console.log('SW registered: ', registration);
                      })
                      .catch(function(registrationError) {
                        console.log('SW registration failed: ', registrationError);
                      });
                  });
                }
              `,
            }}
          />
        )}

        {/* Error Boundary Script */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.addEventListener('error', function(e) {
                console.error('Global error:', e.error);
                // You can send this to your error tracking service
              });
              
              window.addEventListener('unhandledrejection', function(e) {
                console.error('Unhandled promise rejection:', e.reason);
                // You can send this to your error tracking service
              });
            `,
          }}
        />
      </body>
    </html>
  )
}

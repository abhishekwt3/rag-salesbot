import React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  Code,
  ArrowRight,
  Clock,
  Download,
} from "lucide-react"

export default function Integration() {
  return (
    <section id="integration" className="w-full py-16 md:py-24 lg:py-32 bg-brand-timberwolf/20">
      <div className="container px-4 md:px-6">
        <div className="grid gap-12 lg:grid-cols-[1fr_500px] lg:gap-16 xl:grid-cols-[1fr_550px] items-center">
          <div className="flex flex-col justify-center space-y-6">
            <div className="space-y-4">
              <Badge
                variant="secondary"
                className="w-fit bg-brand-cerulean/10 text-brand-cerulean border-brand-cerulean/20 font-medium"
              >
                <Code className="w-3 h-3 mr-1" />
                Simple Integration
              </Badge>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold tracking-tight text-brand-black">
                Deploy in{" "}
                <span className="bg-gradient-to-r from-brand-cerulean to-brand-midnight bg-clip-text text-transparent">
                  Minutes, Not Hours
                </span>
              </h2>
              <p className="max-w-[600px] text-lg md:text-xl text-brand-midnight/80 leading-relaxed">
                Get your AI salesbot up and running with just a few clicks. No technical expertise required, no
                complex setup process.
              </p>
            </div>

            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-dark-cyan text-white text-sm font-bold flex-shrink-0">
                  1
                </div>
                <div className="space-y-2">
                  <h3 className="font-display font-semibold text-lg text-brand-black">Upload Your Content</h3>
                  <p className="text-brand-midnight/70 leading-relaxed">
                    Add documents, website URLs, or paste text directly. Our AI processes and understands your
                    content instantly.
                  </p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    <Badge variant="outline" className="text-xs">
                      PDF
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      DOCX
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      TXT
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      URLs
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      +50 more
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-cerulean text-white text-sm font-bold flex-shrink-0">
                  2
                </div>
                <div className="space-y-2">
                  <h3 className="font-display font-semibold text-lg text-brand-black">Customize Your Bot</h3>
                  <p className="text-brand-midnight/70 leading-relaxed">
                    Match your brand colors, set the tone of voice, and configure conversation flows to align with
                    your business.
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="w-4 h-4 rounded-full bg-brand-dark-cyan"></div>
                    <div className="w-4 h-4 rounded-full bg-brand-cerulean"></div>
                    <div className="w-4 h-4 rounded-full bg-brand-midnight"></div>
                    <span className="text-xs text-brand-midnight/60 ml-2">Brand colors</span>
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-midnight text-white text-sm font-bold flex-shrink-0">
                  3
                </div>
                <div className="space-y-2">
                  <h3 className="font-display font-semibold text-lg text-brand-black">Embed & Launch</h3>
                  <p className="text-brand-midnight/70 leading-relaxed">
                    Copy one line of code to your website and your AI salesbot is live, ready to convert visitors
                    24/7.
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <Clock className="h-4 w-4 text-brand-dark-cyan" />
                    <span className="text-xs text-brand-midnight/60">Average setup time: 5 minutes</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-4">
              <Button className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white font-semibold">
                Start Integration Now
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="flex items-center justify-center">
            <Card className="w-full max-w-md shadow-xl border-0 bg-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-display">
                  <Code className="h-5 w-5 text-brand-dark-cyan" />
                  Integration Code
                </CardTitle>
                <CardDescription>Copy and paste into your website</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-brand-black/95 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                  <div className="text-gray-400">{"<!-- Add to your website -->"}</div>
                  <div className="text-blue-400">{"<script"}</div>
                  <div className="ml-2 text-green-400">src=&quot;https://salesbot.ai/embed.js&quot;</div>
                  <div className="ml-2 text-green-400">data-bot-id=&quot;your-bot-id&quot;</div>
                  <div className="ml-2 text-yellow-400">data-theme=&quot;custom&quot;</div>
                  <div className="text-blue-400">{"></script>"}</div>
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-brand-midnight/60">That&apos;s it! Your salesbot is now live.</p>
                  <Button size="sm" variant="outline" className="text-xs bg-transparent">
                    <Download className="h-3 w-3 mr-1" />
                    Copy Code
                  </Button>
                </div>

                <Separator />

                <div className="space-y-3">
                  <h4 className="font-semibold text-sm text-brand-black">Popular Platforms</h4>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="text-center p-2 bg-brand-timberwolf/30 rounded-lg">
                      <div className="text-xs font-medium text-brand-midnight">WordPress</div>
                    </div>
                    <div className="text-center p-2 bg-brand-timberwolf/30 rounded-lg">
                      <div className="text-xs font-medium text-brand-midnight">Shopify</div>
                    </div>
                    <div className="text-center p-2 bg-brand-timberwolf/30 rounded-lg">
                      <div className="text-xs font-medium text-brand-midnight">Webflow</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  )
}
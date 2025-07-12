import React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  FileText,
  Globe,
  Zap,
  MessageSquare,
  BarChart3,
  Shield,
  CheckCircle,
  Rocket,
  Play,
} from "lucide-react"

export default function Features() {
  return (
    <section id="features" className="w-full py-16 md:py-24 lg:py-32">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-6 text-center mb-16">
          <Badge
            variant="secondary"
            className="bg-brand-dark-cyan/10 text-brand-dark-cyan border-brand-dark-cyan/20 font-medium"
          >
            <Rocket className="w-3 h-3 mr-1" />
            Powerful Features
          </Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold tracking-tight text-brand-black">
            Everything You Need to{" "}
            <span className="bg-gradient-to-r from-brand-dark-cyan to-brand-cerulean bg-clip-text text-transparent">
              Boost Sales
            </span>
          </h2>
          <p className="max-w-3xl text-lg md:text-xl text-brand-midnight/80 leading-relaxed">
            Our RAG-powered assitant learns from your content and provides accurate, contextual responses to convert
            visitors into customers automatically.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 mb-16">
          <Card className="group hover:shadow-xl transition-all duration-300 border-brand-timberwolf/50 hover:border-brand-dark-cyan/30">
            <CardHeader className="pb-4">
              <div className="w-12 h-12 bg-brand-dark-cyan/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-brand-dark-cyan/20 transition-colors">
                <FileText className="h-6 w-6 text-brand-dark-cyan" />
              </div>
              <CardTitle className="text-xl font-display font-semibold text-brand-black">
                Smart Document Processing
              </CardTitle>
              <CardDescription className="text-brand-midnight/70 leading-relaxed">
                Upload PDFs, Word docs, and text files. Your bot instantly learns from product manuals, FAQs, and
                sales materials with advanced AI understanding.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Supports 50+ file formats</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Automatic content extraction</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Real-time updates</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-xl transition-all duration-300 border-brand-timberwolf/50 hover:border-brand-dark-cyan/30">
            <CardHeader className="pb-4">
              <div className="w-12 h-12 bg-brand-cerulean/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-brand-cerulean/20 transition-colors">
                <Globe className="h-6 w-6 text-brand-cerulean" />
              </div>
              <CardTitle className="text-xl font-display font-semibold text-brand-black">
                Intelligent Web Crawling
              </CardTitle>
              <CardDescription className="text-brand-midnight/70 leading-relaxed">
                Add any website URL and our bot will crawl and learn from your existing web content automatically,
                keeping knowledge fresh and up-to-date.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Deep site crawling</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Scheduled updates</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Content prioritization</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-xl transition-all duration-300 border-brand-timberwolf/50 hover:border-brand-dark-cyan/30">
            <CardHeader className="pb-4">
              <div className="w-12 h-12 bg-brand-midnight/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-brand-midnight/20 transition-colors">
                <Zap className="h-6 w-6 text-brand-midnight" />
              </div>
              <CardTitle className="text-xl font-display font-semibold text-brand-black">
                One-Click Integration
              </CardTitle>
              <CardDescription className="text-brand-midnight/70 leading-relaxed">
                Embed on any website with a single line of code. Works seamlessly with WordPress, Shopify, and
                custom sites without any technical expertise.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Universal compatibility</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Mobile responsive</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Custom branding</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-xl transition-all duration-300 border-brand-timberwolf/50 hover:border-brand-dark-cyan/30">
            <CardHeader className="pb-4">
              <div className="w-12 h-12 bg-brand-dark-cyan/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-brand-dark-cyan/20 transition-colors">
                <MessageSquare className="h-6 w-6 text-brand-dark-cyan" />
              </div>
              <CardTitle className="text-xl font-display font-semibold text-brand-black">
                Natural Conversations
              </CardTitle>
              <CardDescription className="text-brand-midnight/70 leading-relaxed">
                Advanced NLP ensures your bot understands context, handles complex queries, and provides relevant,
                helpful responses that feel genuinely human.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Multi-language support</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Context awareness</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Sentiment analysis</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-xl transition-all duration-300 border-brand-timberwolf/50 hover:border-brand-dark-cyan/30">
            <CardHeader className="pb-4">
              <div className="w-12 h-12 bg-brand-cerulean/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-brand-cerulean/20 transition-colors">
                <BarChart3 className="h-6 w-6 text-brand-cerulean" />
              </div>
              <CardTitle className="text-xl font-display font-semibold text-brand-black">
                Advanced Analytics
              </CardTitle>
              <CardDescription className="text-brand-midnight/70 leading-relaxed">
                Track conversations, conversion rates, and identify the most common questions to optimize
                performance and maximize your ROI.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Real-time dashboards</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Conversion tracking</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Performance insights</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="group hover:shadow-xl transition-all duration-300 border-brand-timberwolf/50 hover:border-brand-dark-cyan/30">
            <CardHeader className="pb-4">
              <div className="w-12 h-12 bg-brand-midnight/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-brand-midnight/20 transition-colors">
                <Shield className="h-6 w-6 text-brand-midnight" />
              </div>
              <CardTitle className="text-xl font-display font-semibold text-brand-black">
                Enterprise Security
              </CardTitle>
              <CardDescription className="text-brand-midnight/70 leading-relaxed">
                SOC 2 compliant with end-to-end encryption, GDPR compliance, and enterprise-grade security. Your
                data and customer conversations are always protected.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>SOC 2 Type II certified</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>GDPR compliant</span>
                </div>
                <div className="flex items-center gap-2 text-brand-midnight/60">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>256-bit encryption</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Feature highlight */}
        <div className="bg-gradient-to-r from-brand-dark-cyan/5 via-brand-cerulean/5 to-brand-midnight/5 rounded-2xl p-8 md:p-12">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-2xl md:text-3xl font-display font-bold text-brand-black mb-4">
                See salesdok in action
              </h3>
              <p className="text-brand-midnight/80 mb-6 leading-relaxed">
                Watch how our AI sales assistant handles real customer inquiries, provides accurate product information,
                and converts visitors into leads automatically.
              </p>
              <Button className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white font-semibold">
                <Play className="mr-2 h-4 w-4" />
                Watch Salesdok in Action
              </Button>
            </div>
            <div className="relative">
              <div className="aspect-video bg-brand-timberwolf/50 rounded-xl flex items-center justify-center border-2 border-dashed border-brand-dark-cyan/30">
                <div className="text-center">
                  <video
          src="https://ik.imagekit.io/90xvn3fidvl/salesdok_demo_eVz5JtT6vO.mp4?updatedAt=1752223828802"
          controls
          className="w-full h-full object-cover"
        />
                  {/* <Play className="h-16 w-16 text-brand-dark-cyan mx-auto mb-4" />
                  <p className="text-brand-midnight/60 font-medium">Interactive Demo Video</p> */}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
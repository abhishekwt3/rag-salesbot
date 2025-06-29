import React from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Star,
  Users,
  TrendingUp,
  Clock,
  Target,
  Award,
} from "lucide-react"

export default function Testimonials() {
  return (
    <section className="w-full py-16 md:py-24 lg:py-32">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-6 text-center mb-16">
          <Badge
            variant="secondary"
            className="bg-brand-dark-cyan/10 text-brand-dark-cyan border-brand-dark-cyan/20 font-medium"
          >
            <Users className="w-3 h-3 mr-1" />
            Customer Success
          </Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold tracking-tight text-brand-black">
            Trusted by{" "}
            <span className="bg-gradient-to-r from-brand-dark-cyan to-brand-cerulean bg-clip-text text-transparent">
              Growing Businesses
            </span>
          </h2>
          <p className="max-w-3xl text-lg md:text-xl text-brand-midnight/80 leading-relaxed">
            Join thousands of companies using salesbot to increase their conversion rates and automate their sales
            process.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card className="border-brand-timberwolf/50 hover:shadow-lg transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <blockquote className="text-brand-midnight/80 mb-4 leading-relaxed">
                &quot;salesbot increased our lead generation by 340% in just 2 months. The AI understands our products
                better than some of our sales team!&quot;
              </blockquote>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-brand-dark-cyan/10 rounded-full flex items-center justify-center">
                  <span className="text-sm font-semibold text-brand-dark-cyan">SM</span>
                </div>
                <div>
                  <div className="font-semibold text-brand-black">Sarah Mitchell</div>
                  <div className="text-sm text-brand-midnight/60">CEO, TechFlow Solutions</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-brand-timberwolf/50 hover:shadow-lg transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <blockquote className="text-brand-midnight/80 mb-4 leading-relaxed">
                &quot;The setup was incredibly easy. Within 10 minutes, we had a fully functional AI sales assistant that
                knows our entire product catalog.&quot;
              </blockquote>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-brand-cerulean/10 rounded-full flex items-center justify-center">
                  <span className="text-sm font-semibold text-brand-cerulean">MR</span>
                </div>
                <div>
                  <div className="font-semibold text-brand-black">Marcus Rodriguez</div>
                  <div className="text-sm text-brand-midnight/60">Marketing Director, GrowthCorp</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-brand-timberwolf/50 hover:shadow-lg transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <blockquote className="text-brand-midnight/80 mb-4 leading-relaxed">
                &quot;Our customer satisfaction scores improved dramatically. The bot provides instant, accurate answers
                24/7. It&apos;s like having our best salesperson always available.&quot;
              </blockquote>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-brand-midnight/10 rounded-full flex items-center justify-center">
                  <span className="text-sm font-semibold text-brand-midnight">JL</span>
                </div>
                <div>
                  <div className="font-semibold text-brand-black">Jennifer Liu</div>
                  <div className="text-sm text-brand-midnight/60">VP Sales, InnovateTech</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Company logos */}
        <div className="text-center mb-8">
          <p className="text-sm text-brand-midnight/60 mb-6 font-medium">Trusted by industry leaders</p>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 items-center justify-center opacity-60">
            <div className="flex items-center justify-center">
              <div className="text-xl font-display font-bold text-brand-midnight">TechFlow</div>
            </div>
            <div className="flex items-center justify-center">
              <div className="text-xl font-display font-bold text-brand-midnight">GrowthCorp</div>
            </div>
            <div className="flex items-center justify-center">
              <div className="text-xl font-display font-bold text-brand-midnight">InnovateTech</div>
            </div>
            <div className="flex items-center justify-center">
              <div className="text-xl font-display font-bold text-brand-midnight">ScaleUp</div>
            </div>
            <div className="flex items-center justify-center">
              <div className="text-xl font-display font-bold text-brand-midnight">NextGen</div>
            </div>
          </div>
        </div>

        {/* Key metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 bg-gradient-to-r from-brand-dark-cyan/5 via-brand-cerulean/5 to-brand-midnight/5 rounded-2xl p-8">
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <TrendingUp className="h-6 w-6 text-brand-dark-cyan mr-2" />
              <div className="text-3xl font-display font-bold text-brand-dark-cyan">340%</div>
            </div>
            <p className="text-sm text-brand-midnight/70 font-medium">Average lead increase</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Clock className="h-6 w-6 text-brand-cerulean mr-2" />
              <div className="text-3xl font-display font-bold text-brand-cerulean">24/7</div>
            </div>
            <p className="text-sm text-brand-midnight/70 font-medium">Customer support coverage</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Target className="h-6 w-6 text-brand-midnight mr-2" />
              <div className="text-3xl font-display font-bold text-brand-midnight">92%</div>
            </div>
            <p className="text-sm text-brand-midnight/70 font-medium">Customer satisfaction rate</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <Award className="h-6 w-6 text-brand-dark-cyan mr-2" />
              <div className="text-3xl font-display font-bold text-brand-dark-cyan">5min</div>
            </div>
            <p className="text-sm text-brand-midnight/70 font-medium">Average setup time</p>
          </div>
        </div>
      </div>
    </section>
  )
}
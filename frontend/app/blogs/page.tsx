import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Bot, Clock, Users, TrendingUp, ArrowRight, Rocket, MessageCircle, Zap } from "lucide-react"

export default function BlogPage() {
  const blogPosts = [
    {
      id: "24-7-sales-machine",
      title: "Transform Your Website Into a 24/7 Sales Machine in 3 Simple Steps",
      excerpt:
        "Discover how to deploy an AI-powered sales assistant that works around the clock, converts visitors into customers, and never takes a break. No coding required.",
      category: "Sales Automation",
      readTime: "5 min read",
      audience: "Business Owners",
      difficulty: "Beginner",
      icon: Rocket,
      color: "brand-dark-cyan",
      featured: true,
    },
    {
    id: "state-of-ai-chatbots",
    title: "The State of AI Sales Chat Agents in E-Commerce",
    excerpt:
      "A data-driven deep dive into how AI sales chat agents are reshaping the customer experience and driving more revenue for online retailers in 2025. See trends, results, and actionable strategies.",
    category: "AI Technology",
    readTime: "10 min read",
    audience: "E-Commerce Leaders",
    difficulty: "Intermediate",
    icon: Bot,
    color: "brand-dark-cyan",  // Set to 'false' if you want it in the regular grid instead!
  },
    {
      id: "ai-customer-service",
      title: "How AI is Revolutionizing Customer Service in 2024",
      excerpt:
        "Explore the latest trends in AI-powered customer service and how businesses are using chatbots to improve customer satisfaction.",
      category: "AI Technology",
      readTime: "7 min read",
      audience: "Tech Leaders",
      difficulty: "Intermediate",
      icon: MessageCircle,
      color: "brand-cerulean",
    },
    {
      id: "conversion-optimization",
      title: "10 Proven Strategies to Boost Website Conversions with AI",
      excerpt:
        "Learn actionable techniques to increase your website's conversion rate using AI-powered tools and personalization.",
      category: "Conversion Optimization",
      readTime: "8 min read",
      audience: "Marketers",
      difficulty: "Intermediate",
      icon: TrendingUp,
      color: "brand-midnight",
    },
    {
      id: "chatbot-best-practices",
      title: "Chatbot Best Practices: Do's and Don'ts for 2024",
      excerpt:
        "A comprehensive guide to creating effective chatbots that customers love and that drive real business results.",
      category: "Best Practices",
      readTime: "6 min read",
      audience: "All Users",
      difficulty: "Beginner",
      icon: Zap,
      color: "brand-dark-cyan",
    },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-brand-timberwolf/20 bg-white/80 backdrop-blur-md">
        <div className="container flex h-16 items-center px-4 lg:px-6">
          <Link href="/" className="flex items-center justify-center group">
            <div className="relative">
              <Bot className="h-8 w-8 text-brand-dark-cyan group-hover:text-brand-cerulean transition-colors" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-brand-dark-cyan rounded-full animate-pulse"></div>
            </div>
            <span className="ml-3 text-4xl font-logo font-bold text-brand-midnight">Salesdok</span>
          </Link>
          <nav className="ml-auto">
            <Button asChild className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white">
              <Link href="/">Get Started Free</Link>
            </Button>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12 max-w-6xl">
        {/* Header Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-logo  font-bold text-brand-midnight mb-4">Blogs</h1>
          <p className="text-xl text-brand-midnight/80 max-w-3xl mx-auto leading-relaxed">
            Insights, guides, and best practices for building better customer experiences with AI-powered chatbots.
          </p>
        </div>

        {/* Featured Post */}
        {blogPosts
          .filter((post) => post.featured)
          .map((post) => (
            <Card
              key={post.id}
              className="mb-12 border-brand-dark-cyan/20 bg-gradient-to-r from-brand-dark-cyan/5 to-brand-cerulean/5 hover:shadow-xl transition-all duration-300"
            >
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 bg-brand-dark-cyan/10 rounded-full flex items-center justify-center">
                      <post.icon className="h-8 w-8 text-brand-dark-cyan" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <Badge className="bg-brand-dark-cyan/10 text-brand-dark-cyan border-brand-dark-cyan/20">
                        Featured
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {post.category}
                      </Badge>
                    </div>
                    <h2 className="text-2xl md:text-3xl font-display font-bold text-brand-black mb-3 leading-tight">
                      {post.title}
                    </h2>
                    <p className="text-brand-midnight/80 text-lg leading-relaxed mb-4">{post.excerpt}</p>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-brand-midnight/60 mb-4">
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        <span>{post.readTime}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        <span>For {post.audience}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        <span>{post.difficulty} Level</span>
                      </div>
                    </div>
                    <Button asChild className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white">
                      <Link href={`/blogs/${post.id}`}>
                        Read Full Article
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

        {/* Other Posts Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {blogPosts
            .filter((post) => !post.featured)
            .map((post) => (
              <Card
                key={post.id}
                className="border-brand-timberwolf/50 hover:shadow-lg hover:border-brand-dark-cyan/30 transition-all duration-300 group"
              >
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between mb-3">
                    <div
                      className={`w-12 h-12 bg-${post.color}/10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform`}
                    >
                      <post.icon className={`h-6 w-6 text-${post.color}`} />
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {post.category}
                    </Badge>
                  </div>
                  <CardTitle className="text-xl font-bold text-brand-black leading-tight group-hover:text-brand-dark-cyan transition-colors">
                    {post.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-brand-midnight/80 text-sm leading-relaxed mb-4">{post.excerpt}</p>
                  <div className="flex flex-wrap items-center gap-3 text-xs text-brand-midnight/60 mb-4">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>{post.readTime}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      <span>{post.audience}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <TrendingUp className="h-3 w-3" />
                      <span>{post.difficulty}</span>
                    </div>
                  </div>
                  <Button
                    asChild
                    variant="outline"
                    className="w-full border-brand-cerulean text-brand-cerulean hover:bg-brand-cerulean hover:text-white bg-transparent"
                  >
                    <Link href={`/blogs/${post.id}`}>
                      Read Article
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
        </div>

        {/* Newsletter Signup */}
        <Card className="mt-16 bg-gradient-to-r from-brand-dark-cyan/5 via-brand-cerulean/5 to-brand-midnight/5 border-brand-dark-cyan/20">
          <CardContent className="pt-8">
            <div className="text-center space-y-4">
              <h3 className="text-2xl font-bold text-brand-black">Stay Updated with AI Sales Insights</h3>
              <p className="text-brand-midnight/80 max-w-2xl mx-auto">
                Get the latest tips, strategies, and case studies delivered to your inbox. Join 10,000+ business owners
                growing their sales with AI.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-md mx-auto">
                <input
                  type="email"
                  placeholder="Enter your email address"
                  className="flex-1 px-4 py-3 border border-brand-timberwolf rounded-lg focus:border-brand-dark-cyan focus:ring-2 focus:ring-brand-dark-cyan/20 outline-none"
                />
                <Button className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white px-6 py-3 whitespace-nowrap">
                  Subscribe Free
                </Button>
              </div>
              <p className="text-sm text-brand-midnight/60">No spam, unsubscribe anytime. We respect your privacy.</p>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

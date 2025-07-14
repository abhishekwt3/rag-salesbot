import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Bot,
  Database,
  Code,
  Globe,
  FileText,
  Zap,
  Clock,
  TrendingUp,
  CheckCircle,
  Play,
  Copy,
  Upload,
  Settings,
  Rocket,
  Star,
  Users,
  MessageCircle,
  BarChart3,
} from "lucide-react"

export default function BlogPost() {
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
          <nav className="ml-auto flex items-center gap-4">
            <Link
              href="/blogs"
              className="text-sm font-medium text-brand-midnight hover:text-brand-dark-cyan transition-colors"
            >
              ← Back to Blog
            </Link>
            <Button asChild className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white">
              <Link href="/">Get Started Free</Link>
            </Button>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Article Header */}
        <article className="space-y-8">
          <header className="text-center space-y-6">
            <div className="flex justify-center">
              <Badge className="bg-brand-dark-cyan/10 text-brand-dark-cyan border-brand-dark-cyan/20 px-4 py-2 text-sm font-medium">
                <Rocket className="w-4 h-4 mr-2" />
                Sales Automation Guide
              </Badge>
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-5xl font-display font-bold text-brand-black leading-tight">
              Transform Your Website Into a{" "}
              <span className="bg-gradient-to-r from-brand-dark-cyan via-brand-cerulean to-brand-midnight bg-clip-text text-transparent">
                24/7 Sales Machine
              </span>{" "}
              in 3 Simple Steps
            </h1>

            <p className="text-xl text-brand-midnight/80 max-w-3xl mx-auto leading-relaxed">
              Discover how to deploy an AI-powered sales assistant that works around the clock, converts visitors into
              customers, and never takes a break. No coding required.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-brand-midnight/60">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span>5 min read</span>
              </div>
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                <span>For Business Owners</span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                <span>Beginner Friendly</span>
              </div>
            </div>
          </header>

          {/* Introduction */}
          <section className="prose prose-lg max-w-none">
            <div className="bg-gradient-to-r from-brand-dark-cyan/5 via-brand-cerulean/5 to-brand-midnight/5 rounded-2xl p-8 mb-8">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-brand-dark-cyan/10 rounded-full flex-shrink-0">
                  <MessageCircle className="h-8 w-8 text-brand-dark-cyan" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-brand-black mb-4">
                    What if your website could sell while you sleep? 🌙
                  </h2>
                  <p className="text-brand-midnight/80 text-lg leading-relaxed">
                    Imagine having a sales representative who never gets tired, never takes a vacation, and knows your
                    products inside and out. With <strong>salesdok</strong>, you can deploy an AI-powered sales
                    assistant that engages visitors, answers questions, and converts prospects into customers 24/7.
                  </p>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <Card className="text-center p-6 border-brand-timberwolf/50 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-bold text-brand-black mb-2">300% More Leads</h3>
                <p className="text-sm text-brand-midnight/70">Average increase in qualified leads</p>
              </Card>

              <Card className="text-center p-6 border-brand-timberwolf/50 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Clock className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-bold text-brand-black mb-2">24/7 Availability</h3>
                <p className="text-sm text-brand-midnight/70">Never miss a potential customer</p>
              </Card>

              <Card className="text-center p-6 border-brand-timberwolf/50 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-bold text-brand-black mb-2">5 Min Setup</h3>
                <p className="text-sm text-brand-midnight/70">From zero to sales machine</p>
              </Card>
            </div>

            <p className="text-lg text-brand-midnight/80 leading-relaxed mb-8">
              In this guide, we&apos;ll show you exactly how to transform your website into a lead-generating,
              sales-converting powerhouse using Salesdok&apos;s AI technology. The best part? It takes just three simple
              steps and requires zero technical expertise.
            </p>
          </section>

          {/* Step 1 */}
          <section className="space-y-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-brand-dark-cyan text-white rounded-full flex items-center justify-center font-bold text-xl">
                1
              </div>
              <div>
                <h2 className="text-3xl font-display font-bold text-brand-black">Create Your AI Knowledge Base</h2>
                <p className="text-brand-midnight/70">Train your AI assistant with your business knowledge</p>
              </div>
            </div>

            <Card className="border-brand-dark-cyan/20 bg-brand-dark-cyan/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-brand-black">
                  <Database className="h-6 w-6 text-brand-dark-cyan" />
                  Building Your Knowledge Foundation
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <p className="text-brand-midnight/80 leading-relaxed">
                  The first step is to create a knowledge base that will serve as your AI assistant&apos;s brain. This is
                  where you&apos;ll upload all the information about your products, services, and business that your AI will
                  use to answer customer questions.
                </p>

                <div className="bg-white rounded-xl p-6 border border-brand-timberwolf/50">
                  <h4 className="font-semibold text-brand-black mb-4 flex items-center gap-2">
                    <Settings className="h-5 w-5 text-brand-dark-cyan" />
                    How to Create Your Knowledge Base:
                  </h4>

                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-brand-dark-cyan/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-brand-dark-cyan">1</span>
                      </div>
                      <div>
                        <p className="font-medium text-brand-black">Login to your salesdok dashboard</p>
                        <p className="text-sm text-brand-midnight/70">Navigate to the Knowledge Base section</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-brand-dark-cyan/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-brand-dark-cyan">2</span>
                      </div>
                      <div>
                        <p className="font-medium text-brand-black">Click &quot;Create New Knowledge Base&quot;</p>
                        <p className="text-sm text-brand-midnight/70">
                          Give it a descriptive name like &quot;Product Catalog&quot; or &quot;Company Info&quot;
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-brand-dark-cyan/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-brand-dark-cyan">3</span>
                      </div>
                      <div>
                        <p className="font-medium text-brand-black">Add your data sources</p>
                        <p className="text-sm text-brand-midnight/70">Choose from multiple options below</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <Card className="border-brand-cerulean/20 hover:shadow-md transition-shadow">
                    <CardHeader className="pb-4">
                      <CardTitle className="text-lg flex items-center gap-2 text-brand-black">
                        <Globe className="h-5 w-5 text-brand-cerulean" />
                        Website Scraping
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-brand-midnight/80 mb-4">
                        Simply paste your website URL and let our AI crawl and learn from your existing content.
                      </p>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-brand-midnight/70">Automatic content extraction</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-brand-midnight/70">Product pages & descriptions</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-brand-midnight/70">FAQ & support content</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border-brand-midnight/20 hover:shadow-md transition-shadow">
                    <CardHeader className="pb-4">
                      <CardTitle className="text-lg flex items-center gap-2 text-brand-black">
                        <FileText className="h-5 w-5 text-brand-midnight" />
                        Document Upload
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-brand-midnight/80 mb-4">
                        Upload your existing documents to train your AI with specific knowledge.
                      </p>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-brand-midnight/70">PDF product catalogs</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-brand-midnight/70">Word documents (.doc, .docx)</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-brand-midnight/70">Text files (.txt)</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-blue-100 rounded-full">
                      <Upload className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-blue-900 mb-2">Pro Tip: What to Include</h4>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• Product specifications and features</li>
                        <li>• Pricing information and packages</li>
                        <li>• Frequently asked questions</li>
                        <li>• Company policies and procedures</li>
                        <li>• Customer testimonials and case studies</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Step 2 */}
          <section className="space-y-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-brand-cerulean text-white rounded-full flex items-center justify-center font-bold text-xl">
                2
              </div>
              <div>
                <h2 className="text-3xl font-display font-bold text-brand-black">Design Your Chat Widget</h2>
                <p className="text-brand-midnight/70">Customize your AI assistant&apos;s appearance and behavior</p>
              </div>
            </div>

            <Card className="border-brand-cerulean/20 bg-brand-cerulean/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-brand-black">
                  <Code className="h-6 w-6 text-brand-cerulean" />
                  Creating Your Sales Widget
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <p className="text-brand-midnight/80 leading-relaxed">
                  Now that your AI is trained with your business knowledge, it&apos;s time to create the chat widget that
                  will appear on your website. This is where the magic happens – where visitors become customers.
                </p>

                <div className="bg-white rounded-xl p-6 border border-brand-timberwolf/50">
                  <h4 className="font-semibold text-brand-black mb-4 flex items-center gap-2">
                    <Settings className="h-5 w-5 text-brand-cerulean" />
                    Widget Creation Process:
                  </h4>

                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-brand-cerulean/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-brand-cerulean">1</span>
                      </div>
                      <div>
                        <p className="font-medium text-brand-black">Navigate to the Widget section</p>
                        <p className="text-sm text-brand-midnight/70">Find it in your salesdok dashboard sidebar</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-brand-cerulean/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-brand-cerulean">2</span>
                      </div>
                      <div>
                        <p className="font-medium text-brand-black">Click &quot;Create New Widget&quot;</p>
                        <p className="text-sm text-brand-midnight/70">Select your knowledge base from the dropdown</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-brand-cerulean/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-brand-cerulean">3</span>
                      </div>
                      <div>
                        <p className="font-medium text-brand-black">Customize your widget</p>
                        <p className="text-sm text-brand-midnight/70">
                          Match your brand colors and set the welcome message
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-semibold text-brand-black flex items-center gap-2">
                      <Settings className="h-5 w-5 text-brand-cerulean" />
                      Customization Options
                    </h4>

                    <div className="space-y-3">
                      <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-brand-timberwolf/30">
                        <div className="w-8 h-8 bg-brand-cerulean/10 rounded-lg flex items-center justify-center">
                          <span className="text-xs font-bold text-brand-cerulean">🎨</span>
                        </div>
                        <div>
                          <p className="font-medium text-brand-black text-sm">Brand Colors</p>
                          <p className="text-xs text-brand-midnight/70">Match your website&apos;s color scheme</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-brand-timberwolf/30">
                        <div className="w-8 h-8 bg-brand-cerulean/10 rounded-lg flex items-center justify-center">
                          <span className="text-xs font-bold text-brand-cerulean">💬</span>
                        </div>
                        <div>
                          <p className="font-medium text-brand-black text-sm">Welcome Message</p>
                          <p className="text-xs text-brand-midnight/70">First impression matters</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-brand-timberwolf/30">
                        <div className="w-8 h-8 bg-brand-cerulean/10 rounded-lg flex items-center justify-center">
                          <span className="text-xs font-bold text-brand-cerulean">📱</span>
                        </div>
                        <div>
                          <p className="font-medium text-brand-black text-sm">Position & Size</p>
                          <p className="text-xs text-brand-midnight/70">Bottom right, left, or custom</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-brand-cerulean/10 to-brand-midnight/10 rounded-xl p-6">
                    <h4 className="font-semibold text-brand-black mb-4">Widget Preview</h4>
                    <div className="bg-white rounded-lg border shadow-sm p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <Bot className="h-5 w-5 text-brand-cerulean" />
                        <span className="font-medium text-brand-black text-sm">Sales Assistant</span>
                        <Badge className="ml-auto bg-green-100 text-green-700 text-xs">Online</Badge>
                      </div>
                      <div className="bg-brand-timberwolf/30 rounded-lg p-3 text-sm text-brand-black">
                        👋 Hi! I&apos;m here to help you find the perfect solution for your business. What can I help you
                        with today?
                      </div>
                      <div className="mt-3 flex items-center gap-2">
                        <input
                          type="text"
                          placeholder="Type your message..."
                          className="flex-1 text-xs p-2 border border-brand-timberwolf rounded-lg"
                          disabled
                        />
                        <Button
                          size="sm"
                          className="bg-brand-cerulean hover:bg-brand-midnight text-white px-3 py-1 text-xs"
                        >
                          Send
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-green-100 rounded-full">
                      <Star className="h-4 w-4 text-green-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-green-900 mb-2">Best Practices for Widget Setup</h4>
                      <ul className="text-sm text-green-800 space-y-1">
                        <li>• Use a friendly, conversational welcome message</li>
                        <li>• Position the widget where it&apos;s visible but not intrusive</li>
                        <li>• Match your brand colors for consistency</li>
                        <li>• Test the widget on different devices and screen sizes</li>
                        <li>• Set up proactive messages for key pages</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Step 3 */}
          <section className="space-y-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-brand-midnight text-white rounded-full flex items-center justify-center font-bold text-xl">
                3
              </div>
              <div>
                <h2 className="text-3xl font-display font-bold text-brand-black">Deploy to Your Website</h2>
                <p className="text-brand-midnight/70">One line of code, infinite possibilities</p>
              </div>
            </div>

            <Card className="border-brand-midnight/20 bg-brand-midnight/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-brand-black">
                  <Rocket className="h-6 w-6 text-brand-midnight" />
                  Going Live in Minutes
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <p className="text-brand-midnight/80 leading-relaxed">
                  The final step is the easiest – deploying your AI sales assistant to your website. No technical
                  expertise required, just a simple copy-and-paste operation.
                </p>

                <div className="bg-white rounded-xl p-6 border border-brand-timberwolf/50">
                  <h4 className="font-semibold text-brand-black mb-4 flex items-center gap-2">
                    <Code className="h-5 w-5 text-brand-midnight" />
                    Integration Steps:
                  </h4>

                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-brand-midnight/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-brand-midnight">1</span>
                      </div>
                      <div>
                        <p className="font-medium text-brand-black">Copy the embed code</p>
                        <p className="text-sm text-brand-midnight/70">Find it in your widget settings</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-brand-midnight/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-brand-midnight">2</span>
                      </div>
                      <div>
                        <p className="font-medium text-brand-black">Paste into your website</p>
                        <p className="text-sm text-brand-midnight/70">Add it before the closing &lt;/body&gt; tag</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-brand-midnight/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-brand-midnight">3</span>
                      </div>
                      <div>
                        <p className="font-medium text-brand-black">Test and go live</p>
                        <p className="text-sm text-brand-midnight/70">Your 24/7 sales machine is ready!</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-semibold text-brand-black">Sample Embed Code:</h4>
                  <div className="bg-brand-black/95 rounded-xl p-4 font-mono text-sm overflow-x-auto">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400 text-xs">HTML</span>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs h-6 px-2 bg-white/10 border-white/20 text-white hover:bg-white/20"
                      >
                        <Copy className="h-3 w-3 mr-1" />
                        Copy
                      </Button>
                    </div>
                    <div className="text-gray-300">
                      <div className="text-gray-500">{"<!-- Add this before closing </body> tag -->"}</div>
                      <div className="text-blue-400">{"<script"}</div>
                      <div className="ml-3 text-green-400">src=&quot;https://salesdok.com/embed.js&quot;</div>
                      <div className="ml-3 text-green-400">data-widget-id=&quot;your-widget-id&quot;</div>
                      <div className="ml-3 text-yellow-400">data-position=&quot;bottom-right&quot;</div>
                      <div className="text-blue-400">{">"}</div>
                      <div className="text-blue-400">{"</script>"}</div>
                    </div>
                  </div>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <Card className="text-center p-4 border-brand-timberwolf/50">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <Globe className="h-5 w-5 text-blue-600" />
                    </div>
                    <h5 className="font-semibold text-brand-black text-sm mb-1">WordPress</h5>
                    <p className="text-xs text-brand-midnight/70">Add to theme footer or use a plugin</p>
                  </Card>

                  <Card className="text-center p-4 border-brand-timberwolf/50">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <Code className="h-5 w-5 text-green-600" />
                    </div>
                    <h5 className="font-semibold text-brand-black text-sm mb-1">Shopify</h5>
                    <p className="text-xs text-brand-midnight/70">Paste in theme.liquid template</p>
                  </Card>

                  <Card className="text-center p-4 border-brand-timberwolf/50">
                    <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <Settings className="h-5 w-5 text-purple-600" />
                    </div>
                    <h5 className="font-semibold text-brand-black text-sm mb-1">Custom HTML</h5>
                    <p className="text-xs text-brand-midnight/70">Works with any website platform</p>
                  </Card>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-purple-100 rounded-full">
                      <Zap className="h-4 w-4 text-purple-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-purple-900 mb-2">Advanced Integration Options</h4>
                      <ul className="text-sm text-purple-800 space-y-1">
                        <li>
                          • <strong>Targeted Pages:</strong> Show widget only on specific pages
                        </li>
                        <li>
                          • <strong>User Behavior:</strong> Trigger based on scroll depth or time on page
                        </li>
                        <li>
                          • <strong>A/B Testing:</strong> Test different messages and positions
                        </li>
                        <li>
                          • <strong>Analytics:</strong> Track conversations and conversion rates
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Results Section */}
          <section className="space-y-8">
            <div className="text-center">
              <h2 className="text-3xl font-display font-bold text-brand-black mb-4">
                🎉 Congratulations! Your 24/7 Sales Machine is Live
              </h2>
              <p className="text-lg text-brand-midnight/80 max-w-2xl mx-auto">
                You&apos;ve just deployed an AI-powered sales assistant that will work tirelessly to convert your website
                visitors into customers. Here&apos;s what you can expect:
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="text-center p-6 border-brand-dark-cyan/20 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-brand-dark-cyan/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MessageCircle className="h-6 w-6 text-brand-dark-cyan" />
                </div>
                <h3 className="font-bold text-brand-black mb-2">Instant Engagement</h3>
                <p className="text-sm text-brand-midnight/70">Visitors get immediate responses to their questions</p>
              </Card>

              <Card className="text-center p-6 border-brand-cerulean/20 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-brand-cerulean/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="h-6 w-6 text-brand-cerulean" />
                </div>
                <h3 className="font-bold text-brand-black mb-2">Higher Conversions</h3>
                <p className="text-sm text-brand-midnight/70">Turn more visitors into qualified leads</p>
              </Card>

              <Card className="text-center p-6 border-brand-midnight/20 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-brand-midnight/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Clock className="h-6 w-6 text-brand-midnight" />
                </div>
                <h3 className="font-bold text-brand-black mb-2">24/7 Availability</h3>
                <p className="text-sm text-brand-midnight/70">Never miss a potential customer again</p>
              </Card>

              <Card className="text-center p-6 border-green-200 hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-bold text-brand-black mb-2">Valuable Insights</h3>
                <p className="text-sm text-brand-midnight/70">Learn what customers really want to know</p>
              </Card>
            </div>

            <Card className="bg-gradient-to-r from-brand-dark-cyan/5 via-brand-cerulean/5 to-brand-midnight/5 border-brand-dark-cyan/20">
              <CardContent className="pt-6">
                <div className="text-center space-y-4">
                  <h3 className="text-2xl font-bold text-brand-black">Ready to Transform Your Website?</h3>
                  <p className="text-brand-midnight/80 max-w-2xl mx-auto">
                    Join thousands of businesses already using salesdok to increase their sales and improve customer
                    experience.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                    <Button size="lg" className="bg-brand-dark-cyan hover:bg-brand-cerulean text-white px-8 py-3">
                      <Play className="h-5 w-5 mr-2" />
                      Start Free Trial
                    </Button>
                    <Button
                      size="lg"
                      variant="outline"
                      className="border-brand-cerulean text-brand-cerulean hover:bg-brand-cerulean hover:text-white px-8 py-3 bg-transparent"
                    >
                      Watch Demo
                    </Button>
                  </div>
                  <p className="text-sm text-brand-midnight/60">
                    No credit card required • 5-minute setup • 14-day free trial
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

           <section className="space-y-6">
            <h2 className="text-2xl font-display font-bold text-brand-black text-center">Frequently Asked Questions</h2>
          </section> 
          {/* FAQ Section */}
          {/* <section className="space-y-6">
            <h2 className="text-2xl font-display font-bold text-brand-black text-center">Frequently Asked Questions</h2>

            <div className="space-y-4">
              <Card className="border-brand-timberwolf/50">
                <CardHeader>
                  <CardTitle className="text-lg text-brand-black">How long does it take to set up?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-brand-midnight/80">
                    Most users complete the entire setup process in under 10 minutes. The knowledge base creation takes
                    2-3 minutes, widget customization takes another 2-3 minutes, and deployment is instant.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-brand-timberwolf/50">
                <CardHeader>
                  <CardTitle className="text-lg text-brand-black">Do I need technical skills?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-brand-midnight/80">
                    Not at all! Our platform is designed for business owners, not developers. If you can copy and paste,
                    you can deploy a salesdok. We also provide step-by-step guides for popular platforms like WordPress
                    and Shopify.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-brand-timberwolf/50">
                <CardHeader>
                  <CardTitle className="text-lg text-brand-black">How accurate are the AI responses?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-brand-midnight/80">
                    Our RAG technology ensures high accuracy by grounding responses in your specific business content.
                    The AI only answers based on the information you provide, reducing hallucinations and ensuring
                    relevant, accurate responses.
                  </p>
                </CardContent>
              </Card>

              <Card className="border-brand-timberwolf/50">
                <CardHeader>
                  <CardTitle className="text-lg text-brand-black">Can I customize the appearance?</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-brand-midnight/80">
                    Yes! You can customize colors, position, welcome messages, and behavior to match your brand.
                    Advanced users can also use CSS for deeper customization.
                  </p>
                </CardContent>
              </Card>
            </div>
          </section> */}
        </article>
      </main>
    </div>
  )
}

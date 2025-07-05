import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Bot, FileText, Scale, AlertTriangle, CreditCard, Shield, Users, Gavel } from "lucide-react"

export default function TermsOfService() {
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
            <Button
              asChild
              variant="outline"
              className="border-brand-cerulean text-brand-cerulean hover:bg-brand-cerulean hover:text-white bg-transparent"
            >
              <Link href="/">Back to Home</Link>
            </Button>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Header Section */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-brand-dark-cyan/10 rounded-full">
              <Scale className="h-12 w-12 text-brand-dark-cyan" />
            </div>
          </div>
          <h1 className="text-4xl font-display font-bold text-brand-black mb-4">Terms of Service</h1>
          <p className="text-lg text-brand-midnight/70 max-w-2xl mx-auto">
            These terms govern your use of salesbot and our AI-powered chatbot services. Please read them carefully.
          </p>
          <div className="mt-6 text-sm text-brand-midnight/60">
            <p>
              <strong>Effective Date:</strong> January 10, 2024
            </p>
            <p>
              <strong>Last Updated:</strong> July 4, 2025
            </p>
          </div>
        </div>

        {/* Quick Navigation */}
        <Card className="mb-8 border-brand-timberwolf/50">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-brand-black flex items-center gap-2">
              <FileText className="h-5 w-5 text-brand-dark-cyan" />
              Quick Navigation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <a href="#acceptance" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">
                1. Acceptance of Terms
              </a>
              <a href="#description" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">
                2. Service Description
              </a>
              <a href="#eligibility" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">
                3. Eligibility
              </a>
              <a href="#accounts" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">
                4. User Accounts
              </a>
              <a href="#acceptable-use" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">
                5. Acceptable Use
              </a>
              <a href="#content" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">
                6. Content and Data
              </a>
              <a href="#payment" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">
                7. Payment Terms
              </a>
              <a
                href="#intellectual-property"
                className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors"
              >
                8. Intellectual Property
              </a>
              <a href="#privacy" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">
                9. Privacy
              </a>
              <a href="#disclaimers" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">
                10. Disclaimers
              </a>
              <a
                href="#limitation-liability"
                className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors"
              >
                11. Limitation of Liability
              </a>
              <a href="#termination" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">
                12. Termination
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Main Content */}
        <div className="space-y-8">
          {/* Section 1 */}
          <section id="acceptance">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <Gavel className="h-6 w-6 text-brand-dark-cyan" />
                  1. Acceptance of Terms
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-brand-midnight/80">
                  By accessing or using Salesdok (&quot;Service&quot;), you agree to be bound by these Terms of Service (&quot;Terms&quot;).
                  If you disagree with any part of these terms, you may not access the Service.
                </p>

                <div className="bg-brand-dark-cyan/5 p-4 rounded-lg border border-brand-dark-cyan/20">
                  <p className="text-brand-black font-semibold mb-2">Important Notice</p>
                  <p className="text-brand-midnight/80 text-sm">
                    These Terms constitute a legally binding agreement between you and salesbot, Inc. Your use of our
                    Service indicates your acceptance of these Terms.
                  </p>
                </div>

                <p className="text-brand-midnight/80">
                  We may modify these Terms at any time. We will notify you of material changes via email or through our
                  Service. Your continued use after such modifications constitutes acceptance of the new Terms.
                </p>
              </CardContent>
            </Card>
          </section>

          {/* Section 2 */}
          <section id="description">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <Bot className="h-6 w-6 text-brand-dark-cyan" />
                  2. Service Description
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-brand-midnight/80">
                  salesbot provides AI-powered chatbot services that enable businesses to:
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h4 className="font-semibold text-brand-black">Core Features</h4>
                    <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 text-sm ml-2">
                      <li>Create and train AI chatbots using RAG technology</li>
                      <li>Upload documents and website content for training</li>
                      <li>Deploy chatbots on websites and applications</li>
                      <li>Monitor and analyze chatbot performance</li>
                      <li>Customize chatbot appearance and behavior</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-semibold text-brand-black">Service Levels</h4>
                    <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 text-sm ml-2">
                      <li>Free tier with basic functionality</li>
                      <li>Paid plans with advanced features</li>
                      <li>Enterprise solutions with custom requirements</li>
                      <li>API access for developers</li>
                      <li>Technical support and documentation</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                  <p className="text-yellow-800 text-sm">
                    <strong>Service Availability:</strong> While we strive for 99.9% uptime, we do not guarantee
                    uninterrupted service. Scheduled maintenance and updates may temporarily affect availability.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section 3 */}
          <section id="eligibility">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <Users className="h-6 w-6 text-brand-dark-cyan" />
                  3. Eligibility and Registration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Eligibility Requirements</h4>
                  <p className="text-brand-midnight/80 mb-3">To use our Service, you must:</p>
                  <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 ml-4">
                    <li>Be at least 18 years old or the age of majority in your jurisdiction</li>
                    <li>Have the legal capacity to enter into binding agreements</li>
                    <li>Not be prohibited from using our Service under applicable laws</li>
                    <li>Provide accurate and complete registration information</li>
                    <li>Maintain the security of your account credentials</li>
                  </ul>
                </div>

                <Separator className="bg-brand-timberwolf/50" />

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Business Use</h4>
                  <p className="text-brand-midnight/80">
                    If you are using our Service on behalf of a business or organization, you represent that you have
                    the authority to bind that entity to these Terms.
                  </p>
                </div>

                <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                  <p className="text-red-800 text-sm">
                    <strong>Prohibited Users:</strong> Our Service is not available to individuals or entities on trade
                    restriction lists or in countries subject to comprehensive sanctions.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section 4 */}
          <section id="accounts">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <Shield className="h-6 w-6 text-brand-dark-cyan" />
                  4. User Accounts and Security
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Account Responsibility</h4>
                  <p className="text-brand-midnight/80 mb-3">You are responsible for:</p>
                  <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 ml-4">
                    <li>Maintaining the confidentiality of your account credentials</li>
                    <li>All activities that occur under your account</li>
                    <li>Notifying us immediately of any unauthorized access</li>
                    <li>Keeping your account information accurate and up-to-date</li>
                    <li>Complying with our security requirements</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Account Security</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <h5 className="font-medium text-brand-black text-sm">Required Practices</h5>
                      <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 text-sm ml-2">
                        <li>Use strong, unique passwords</li>
                        <li>Enable two-factor authentication when available</li>
                        <li>Log out from shared devices</li>
                        <li>Monitor account activity regularly</li>
                      </ul>
                    </div>
                    <div className="space-y-2">
                      <h5 className="font-medium text-brand-black text-sm">Prohibited Actions</h5>
                      <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 text-sm ml-2">
                        <li>Sharing account credentials</li>
                        <li>Creating multiple accounts without permission</li>
                        <li>Using automated tools to access accounts</li>
                        <li>Attempting to access other user&apos;s accounts</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section 5 */}
          <section id="acceptable-use">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <AlertTriangle className="h-6 w-6 text-brand-dark-cyan" />
                  5. Acceptable Use Policy
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                  <h4 className="font-semibold text-green-800 mb-2">Permitted Uses</h4>
                  <p className="text-green-700 text-sm">
                    You may use our Service for legitimate business purposes, including customer service, sales support,
                    information dissemination, and other lawful commercial activities.
                  </p>
                </div>

                <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                  <h4 className="font-semibold text-red-800 mb-2">Prohibited Uses</h4>
                  <p className="text-red-700 text-sm mb-3">You may not use our Service to:</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <ul className="list-disc list-inside space-y-1 text-red-700 text-sm ml-2">
                      <li>Violate any applicable laws or regulations</li>
                      <li>Infringe on intellectual property rights</li>
                      <li>Distribute malware or harmful content</li>
                      <li>Engage in fraudulent or deceptive practices</li>
                      <li>Harass, abuse, or harm others</li>
                      <li>Spam or send unsolicited communications</li>
                    </ul>
                    <ul className="list-disc list-inside space-y-1 text-red-700 text-sm ml-2">
                      <li>Collect personal information without consent</li>
                      <li>Impersonate others or misrepresent identity</li>
                      <li>Interfere with our Service or infrastructure</li>
                      <li>Attempt to gain unauthorized access</li>
                      <li>Reverse engineer our technology</li>
                      <li>Use our Service for illegal activities</li>
                    </ul>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Content Standards</h4>
                  <p className="text-brand-midnight/80 mb-3">All content used with our Service must:</p>
                  <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 ml-4">
                    <li>Be accurate and not misleading</li>
                    <li>Respect other&apos;s privacy and rights</li>
                    <li>Comply with applicable content regulations</li>
                    <li>Not contain harmful or offensive material</li>
                    <li>Be appropriate for your intended audience</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section 6 */}
          <section id="content">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <FileText className="h-6 w-6 text-brand-dark-cyan" />
                  6. Content and Data Rights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Your Content</h4>
                  <p className="text-brand-midnight/80 mb-3">
                    You retain ownership of all content you upload or provide to our Service. By using our Service, you
                    grant us:
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 ml-4">
                    <li>A license to process, store, and analyze your content for service provision</li>
                    <li>The right to use your content to train and improve our AI models</li>
                    <li>Permission to display your content through chatbot interactions</li>
                    <li>The ability to create derivative works for service functionality</li>
                  </ul>
                </div>

                <div className="bg-brand-dark-cyan/5 p-4 rounded-lg border border-brand-dark-cyan/20">
                  <h4 className="font-semibold text-brand-black mb-2">Content Responsibilities</h4>
                  <p className="text-brand-midnight/80 text-sm">
                    You are solely responsible for ensuring you have the right to use all content you provide. This
                    includes obtaining necessary permissions for copyrighted material, personal data, and proprietary
                    information.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Content Removal</h4>
                  <p className="text-brand-midnight/80">
                    We reserve the right to remove or disable access to content that violates these Terms, infringes on
                    rights, or is otherwise objectionable. We will provide notice when reasonably possible.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section 7 */}
          <section id="payment">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <CreditCard className="h-6 w-6 text-brand-dark-cyan" />
                  7. Payment Terms and Billing
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Subscription Plans</h4>
                  <p className="text-brand-midnight/80 mb-3">
                    We offer various subscription plans with different features and usage limits:
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <h5 className="font-medium text-brand-black text-sm mb-1">Free Plan</h5>
                      <p className="text-brand-midnight/80 text-sm">Basic features with usage limitations</p>
                    </div>
                    <div className="p-3 bg-brand-dark-cyan/5 rounded-lg">
                      <h5 className="font-medium text-brand-black text-sm mb-1">Pro Plan</h5>
                      <p className="text-brand-midnight/80 text-sm">Advanced features and higher usage limits</p>
                    </div>
                    <div className="p-3 bg-brand-cerulean/5 rounded-lg">
                      <h5 className="font-medium text-brand-black text-sm mb-1">Enterprise</h5>
                      <p className="text-brand-midnight/80 text-sm">Custom solutions and dedicated support</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Billing and Payment</h4>
                  <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 ml-4">
                    <li>Subscription fees are billed in advance on a monthly or annual basis</li>
                    <li>All fees are non-refundable except as required by law</li>
                    <li>You must provide valid payment information and keep it current</li>
                    <li>We may suspend service for non-payment after reasonable notice</li>
                    <li>Price changes will be communicated at least 30 days in advance</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Usage-Based Charges</h4>
                  <p className="text-brand-midnight/80">
                    Some features may incur additional charges based on usage. You will be notified of such charges and
                    can set usage limits to control costs.
                  </p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                  <p className="text-yellow-800 text-sm">
                    <strong>Automatic Renewal:</strong> Subscriptions automatically renew unless cancelled before the
                    renewal date. You can cancel anytime through your account settings.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Continue with remaining sections... */}
          <section id="intellectual-property">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black">8. Intellectual Property Rights</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Our Intellectual Property</h4>
                  <p className="text-brand-midnight/80 mb-3">
                    salesbot and all related technology, software, algorithms, and content are owned by us or our
                    licensors. This includes but is not limited to:
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 ml-4">
                    <li>The salesbot platform and software</li>
                    <li>AI models and training algorithms</li>
                    <li>User interface designs and layouts</li>
                    <li>Documentation and support materials</li>
                    <li>Trademarks, logos, and brand elements</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">License to Use</h4>
                  <p className="text-brand-midnight/80">
                    We grant you a limited, non-exclusive, non-transferable license to use our Service in accordance
                    with these Terms. This license does not include the right to resell, distribute, or create
                    derivative works.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Respect for Third-Party Rights</h4>
                  <p className="text-brand-midnight/80">
                    You must respect the intellectual property rights of others. If you believe content on our platform
                    infringes your rights, please contact us with details of the alleged infringement.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

          <section id="disclaimers">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black">10. Disclaimers and Warranties</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                  <p className="text-yellow-800 text-sm font-semibold mb-2">IMPORTANT DISCLAIMER</p>
                  <p className="text-yellow-800 text-sm">
                    OUR SERVICE IS PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
                    IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
                    PURPOSE, AND NON-INFRINGEMENT.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">AI Technology Limitations</h4>
                  <p className="text-brand-midnight/80 mb-3">You acknowledge that:</p>
                  <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 ml-4">
                    <li>AI responses may not always be accurate or appropriate</li>
                    <li>Our Service may not meet all your specific requirements</li>
                    <li>Technology may experience errors, bugs, or interruptions</li>
                    <li>Results may vary based on input quality and configuration</li>
                    <li>AI models are continuously evolving and improving</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">No Professional Advice</h4>
                  <p className="text-brand-midnight/80">
                    Our Service does not provide professional advice (legal, medical, financial, etc.). AI-generated
                    responses should not be relied upon as professional guidance.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

          <section id="limitation-liability">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black">11. Limitation of Liability</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                  <p className="text-red-800 text-sm font-semibold mb-2">LIABILITY LIMITATION</p>
                  <p className="text-red-800 text-sm">
                    TO THE MAXIMUM EXTENT PERMITTED BY LAW, WE SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL,
                    SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, DATA,
                    USE, OR OTHER INTANGIBLE LOSSES.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Maximum Liability</h4>
                  <p className="text-brand-midnight/80">
                    Our total liability to you for all claims arising from or relating to the Service shall not exceed
                    the amount you paid us in the 12 months preceding the claim, or $100, whichever is greater.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Exceptions</h4>
                  <p className="text-brand-midnight/80">
                    Some jurisdictions do not allow the exclusion or limitation of certain damages. In such
                    jurisdictions, our liability will be limited to the fullest extent permitted by law.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

          <section id="termination">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black">12. Termination</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Termination by You</h4>
                  <p className="text-brand-midnight/80">
                    You may terminate your account at any time through your account settings or by contacting us.
                    Termination will be effective at the end of your current billing period.
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Termination by Us</h4>
                  <p className="text-brand-midnight/80 mb-3">We may terminate or suspend your account if:</p>
                  <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 ml-4">
                    <li>You violate these Terms or our policies</li>
                    <li>Your account remains inactive for an extended period</li>
                    <li>We discontinue the Service (with reasonable notice)</li>
                    <li>Required by law or legal process</li>
                    <li>You fail to pay applicable fees</li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-brand-black mb-2">Effect of Termination</h4>
                  <p className="text-brand-midnight/80">
                    Upon termination, your right to use the Service will cease immediately. We will provide reasonable
                    opportunity to export your data, after which it may be deleted according to our data retention
                    policy.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>
        </div>

        {/* Contact Section */}
        <Card className="mt-12 border-brand-dark-cyan/30 bg-gradient-to-r from-brand-dark-cyan/5 to-brand-cerulean/5">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
              <Scale className="h-6 w-6 text-brand-dark-cyan" />
              Questions About These Terms?
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-brand-midnight/80 mb-4">
              If you have any questions about these Terms of Service, please contact our legal team:
            </p>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <span className="text-brand-black font-medium">Email:</span>
                <a
                  href="mailto:legal@salesdok.com"
                  className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors"
                >
                  team@salesdok.com
                </a>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-brand-black font-medium">Website:</span>
                <a
                  href="https://salesdok.com/cotact"
                  className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors"
                >
                  https://salesdok.com/contact
                </a>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

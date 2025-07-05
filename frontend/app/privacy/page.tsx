import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Bot, Shield, Eye, Lock, Database, Globe, Mail, FileText } from 'lucide-react'

export default function PrivacyPolicy() {
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
            <Button asChild variant="outline" className="border-brand-cerulean text-brand-cerulean hover:bg-brand-cerulean hover:text-white bg-transparent">
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
              <Shield className="h-12 w-12 text-brand-dark-cyan" />
            </div>
          </div>
          <h1 className="text-4xl font-display font-bold text-brand-black mb-4">Privacy Policy</h1>
          <p className="text-lg text-brand-midnight/70 max-w-2xl mx-auto">
            Your privacy is important to us. This policy explains how we collect, use, and protect your information when you use Salesdokdok.
          </p>
          <div className="mt-6 text-sm text-brand-midnight/60">
            <p><strong>Effective Date:</strong> January 10, 2024</p>
            <p><strong>Last Updated:</strong> July 4, 2025</p>
          </div>
        </div>

        {/* Quick Navigation */}
        <Card className="mb-8 border-brand-timberwolf/50">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-brand-black flex items-center gap-2">
              <Eye className="h-5 w-5 text-brand-dark-cyan" />
              Quick Navigation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <a href="#information-collection" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">1. Information We Collect</a>
              <a href="#information-use" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">2. How We Use Information</a>
              <a href="#information-sharing" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">3. Information Sharing</a>
              <a href="#data-security" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">4. Data Security</a>
              <a href="#cookies" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">5. Cookies & Tracking</a>
              <a href="#user-rights" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">6. Your Rights</a>
              <a href="#data-retention" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">7. Data Retention</a>
              <a href="#international-transfers" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">8. International Transfers</a>
              <a href="#children-privacy" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">9. Children&apos;s Privacy</a>
              <a href="#policy-changes" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">10. Policy Changes</a>
            </div>
          </CardContent>
        </Card>

        {/* Main Content */}
        <div className="space-y-8">
          {/* Section 1 */}
          <section id="information-collection">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <Database className="h-6 w-6 text-brand-dark-cyan" />
                  1. Information We Collect
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-brand-black mb-2">Personal Information</h3>
                  <p className="text-brand-midnight/80 mb-3">When you create an account or use our services, we may collect:</p>
                  <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 ml-4">
                    <li>Name and email address</li>
                    <li>Company name and website URL</li>
                    <li>Phone number (optional)</li>
                    <li>Billing and payment information</li>
                    <li>Profile information and preferences</li>
                  </ul>
                </div>

                <Separator className="bg-brand-timberwolf/50" />

                <div>
                  <h3 className="text-lg font-semibold text-brand-black mb-2">Usage Information</h3>
                  <p className="text-brand-midnight/80 mb-3">We automatically collect information about how you use our service:</p>
                  <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 ml-4">
                    <li>Chat conversations and messages</li>
                    <li>Knowledge base content you upload</li>
                    <li>Website URLs and documents processed</li>
                    <li>Usage patterns and feature interactions</li>
                    <li>Device information and IP addresses</li>
                    <li>Browser type and operating system</li>
                  </ul>
                </div>

                <Separator className="bg-brand-timberwolf/50" />

                <div>
                  <h3 className="text-lg font-semibold text-brand-black mb-2">Third-Party Information</h3>
                  <p className="text-brand-midnight/80">We may receive information from third-party services you connect to Salesdok, such as website analytics, CRM systems, or payment processors.</p>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section 2 */}
          <section id="information-use">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <Bot className="h-6 w-6 text-brand-dark-cyan" />
                  2. How We Use Your Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-brand-midnight/80">We use your information to:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h4 className="font-semibold text-brand-black">Service Provision</h4>
                    <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 text-sm ml-2">
                      <li>Provide and maintain our AI chatbot service</li>
                      <li>Process and analyze your content for AI training</li>
                      <li>Generate responses to customer inquiries</li>
                      <li>Customize chatbot behavior and responses</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-semibold text-brand-black">Account Management</h4>
                    <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 text-sm ml-2">
                      <li>Create and manage your account</li>
                      <li>Process payments and billing</li>
                      <li>Provide customer support</li>
                      <li>Send service-related communications</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-semibold text-brand-black">Improvement & Analytics</h4>
                    <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 text-sm ml-2">
                      <li>Analyze usage patterns and performance</li>
                      <li>Improve our AI models and algorithms</li>
                      <li>Develop new features and services</li>
                      <li>Conduct research and analytics</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-semibold text-brand-black">Legal & Security</h4>
                    <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 text-sm ml-2">
                      <li>Comply with legal obligations</li>
                      <li>Protect against fraud and abuse</li>
                      <li>Enforce our terms of service</li>
                      <li>Ensure platform security</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section 3 */}
          <section id="information-sharing">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <Globe className="h-6 w-6 text-brand-dark-cyan" />
                  3. Information Sharing and Disclosure
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-brand-dark-cyan/5 p-4 rounded-lg border border-brand-dark-cyan/20">
                  <p className="text-brand-black font-semibold mb-2">🔒 We do not sell your personal information to third parties.</p>
                  <p className="text-brand-midnight/80 text-sm">Your data is only shared in the limited circumstances described below.</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-brand-black mb-2">Service Providers</h4>
                    <p className="text-brand-midnight/80 text-sm">We may share information with trusted third-party service providers who help us operate our service, including:</p>
                    <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 text-sm ml-4 mt-2">
                      <li>Cloud hosting and infrastructure providers</li>
                      <li>Payment processing services</li>
                      <li>Email and communication services</li>
                      <li>Analytics and monitoring tools</li>
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-semibold text-brand-black mb-2">Legal Requirements</h4>
                    <p className="text-brand-midnight/80 text-sm">We may disclose information when required by law or to:</p>
                    <ul className="list-disc list-inside space-y-1 text-brand-midnight/80 text-sm ml-4 mt-2">
                      <li>Comply with legal process or government requests</li>
                      <li>Protect our rights, property, or safety</li>
                      <li>Protect the rights, property, or safety of our users</li>
                      <li>Investigate potential violations of our terms</li>
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-semibold text-brand-black mb-2">Business Transfers</h4>
                    <p className="text-brand-midnight/80 text-sm">In the event of a merger, acquisition, or sale of assets, your information may be transferred as part of the business transaction. We will notify you of any such change.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section 4 */}
          <section id="data-security">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <Lock className="h-6 w-6 text-brand-dark-cyan" />
                  4. Data Security
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-brand-midnight/80">We implement industry-standard security measures to protect your information:</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-brand-dark-cyan rounded-full mt-2"></div>
                      <div>
                        <h4 className="font-semibold text-brand-black text-sm">Encryption</h4>
                        <p className="text-brand-midnight/80 text-sm">All data is encrypted in transit and at rest using AES-256 encryption</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-brand-dark-cyan rounded-full mt-2"></div>
                      <div>
                        <h4 className="font-semibold text-brand-black text-sm">Access Controls</h4>
                        <p className="text-brand-midnight/80 text-sm">Strict access controls and authentication requirements for all systems</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-brand-dark-cyan rounded-full mt-2"></div>
                      <div>
                        <h4 className="font-semibold text-brand-black text-sm">Regular Audits</h4>
                        <p className="text-brand-midnight/80 text-sm">Regular security audits and vulnerability assessments</p>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-brand-dark-cyan rounded-full mt-2"></div>
                      <div>
                        <h4 className="font-semibold text-brand-black text-sm">Secure Infrastructure</h4>
                        <p className="text-brand-midnight/80 text-sm">SOC 2 Type II compliant cloud infrastructure</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-brand-dark-cyan rounded-full mt-2"></div>
                      <div>
                        <h4 className="font-semibold text-brand-black text-sm">Monitoring</h4>
                        <p className="text-brand-midnight/80 text-sm">24/7 security monitoring and incident response</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-brand-dark-cyan rounded-full mt-2"></div>
                      <div>
                        <h4 className="font-semibold text-brand-black text-sm">Data Backup</h4>
                        <p className="text-brand-midnight/80 text-sm">Regular encrypted backups with secure recovery procedures</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                  <p className="text-yellow-800 text-sm">
                    <strong>Important:</strong> While we implement strong security measures, no system is 100% secure. Please use strong passwords and keep your account credentials confidential.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section 5 */}
          <section id="cookies">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <Eye className="h-6 w-6 text-brand-dark-cyan" />
                  5. Cookies and Tracking Technologies
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-brand-midnight/80">We use cookies and similar technologies to enhance your experience:</p>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-brand-black mb-2">Essential Cookies</h4>
                    <p className="text-brand-midnight/80 text-sm">Required for basic functionality, including authentication and security features.</p>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-brand-black mb-2">Analytics Cookies</h4>
                    <p className="text-brand-midnight/80 text-sm">Help us understand how you use our service to improve performance and user experience.</p>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-brand-black mb-2">Preference Cookies</h4>
                    <p className="text-brand-midnight/80 text-sm">Remember your settings and preferences for a personalized experience.</p>
                  </div>
                </div>

                <div className="bg-brand-timberwolf/20 p-4 rounded-lg">
                  <p className="text-brand-black text-sm">
                    <strong>Cookie Control:</strong> You can manage cookie preferences through your browser settings. Note that disabling certain cookies may affect service functionality.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Section 6 */}
          <section id="user-rights">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
                  <Shield className="h-6 w-6 text-brand-dark-cyan" />
                  6. Your Rights and Choices
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-brand-midnight/80">You have the following rights regarding your personal information:</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="p-3 bg-brand-dark-cyan/5 rounded-lg">
                      <h4 className="font-semibold text-brand-black text-sm mb-1">Access</h4>
                      <p className="text-brand-midnight/80 text-sm">Request a copy of your personal information</p>
                    </div>
                    <div className="p-3 bg-brand-cerulean/5 rounded-lg">
                      <h4 className="font-semibold text-brand-black text-sm mb-1">Correction</h4>
                      <p className="text-brand-midnight/80 text-sm">Update or correct inaccurate information</p>
                    </div>
                    <div className="p-3 bg-brand-midnight/5 rounded-lg">
                      <h4 className="font-semibold text-brand-black text-sm mb-1">Deletion</h4>
                      <p className="text-brand-midnight/80 text-sm">Request deletion of your personal information</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="p-3 bg-brand-dark-cyan/5 rounded-lg">
                      <h4 className="font-semibold text-brand-black text-sm mb-1">Portability</h4>
                      <p className="text-brand-midnight/80 text-sm">Export your data in a machine-readable format</p>
                    </div>
                    <div className="p-3 bg-brand-cerulean/5 rounded-lg">
                      <h4 className="font-semibold text-brand-black text-sm mb-1">Restriction</h4>
                      <p className="text-brand-midnight/80 text-sm">Limit how we process your information</p>
                    </div>
                    <div className="p-3 bg-brand-midnight/5 rounded-lg">
                      <h4 className="font-semibold text-brand-black text-sm mb-1">Objection</h4>
                      <p className="text-brand-midnight/80 text-sm">Object to certain types of processing</p>
                    </div>
                  </div>
                </div>

                <div className="bg-brand-dark-cyan/10 p-4 rounded-lg border border-brand-dark-cyan/20">
                  <p className="text-brand-black font-semibold mb-2">How to Exercise Your Rights</p>
                  <p className="text-brand-midnight/80 text-sm mb-2">To exercise any of these rights, please contact us at:</p>
                  <div className="flex items-center gap-2 text-brand-dark-cyan">
                    <Mail className="h-4 w-4" />
                    <a href="mailto:team@salesdok.com" className="text-sm font-medium hover:underline">team@salesdok.com</a>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Remaining sections with similar structure... */}
          <section id="data-retention">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black">7. Data Retention</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-brand-midnight/80 mb-4">We retain your information for as long as necessary to provide our services and comply with legal obligations:</p>
                <ul className="list-disc list-inside space-y-2 text-brand-midnight/80 ml-4">
                  <li><strong>Account Information:</strong> Retained while your account is active and for 30 days after deletion</li>
                  <li><strong>Chat Data:</strong> Retained for up to 2 years for service improvement and support</li>
                  <li><strong>Knowledge Base Content:</strong> Retained while your account is active and for 90 days after deletion</li>
                  <li><strong>Usage Analytics:</strong> Aggregated data may be retained indefinitely for research purposes</li>
                  <li><strong>Legal Requirements:</strong> Some data may be retained longer to comply with legal obligations</li>
                </ul>
              </CardContent>
            </Card>
          </section>

          <section id="international-transfers">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black">8. International Data Transfers</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-brand-midnight/80 mb-4">Your information may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place:</p>
                <ul className="list-disc list-inside space-y-2 text-brand-midnight/80 ml-4">
                  <li>Standard Contractual Clauses approved by the European Commission</li>
                  <li>Adequacy decisions for countries with equivalent data protection laws</li>
                  <li>Certification under recognized privacy frameworks</li>
                  <li>Other legally recognized transfer mechanisms</li>
                </ul>
              </CardContent>
            </Card>
          </section>

          <section id="children-privacy">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black">9. Children&apos;s Privacy</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-brand-midnight/80 mb-4">Our service is not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13. If you believe we have collected information from a child under 13, please contact us immediately.</p>
                <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                  <p className="text-red-800 text-sm">
                    <strong>Parents and Guardians:</strong> If you discover that your child has provided personal information to us, please contact us at team@salesdok.com and we will delete the information promptly.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>

          <section id="policy-changes">
            <Card className="border-brand-timberwolf/50">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-brand-black">10. Changes to This Privacy Policy</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-brand-midnight/80 mb-4">We may update this Privacy Policy from time to time. When we make changes:</p>
                <ul className="list-disc list-inside space-y-2 text-brand-midnight/80 ml-4 mb-4">
                  <li>We will post the updated policy on this page</li>
                  <li>We will update the &quot;Last Updated&quot; date at the top</li>
                  <li>For material changes, we will notify you via email or through our service</li>
                  <li>Your continued use of our service constitutes acceptance of the updated policy</li>
                </ul>
                <p className="text-brand-midnight/80">We encourage you to review this Privacy Policy periodically to stay informed about how we protect your information.</p>
              </CardContent>
            </Card>
          </section>
        </div>

        {/* Contact Section */}
        <Card className="mt-12 border-brand-dark-cyan/30 bg-gradient-to-r from-brand-dark-cyan/5 to-brand-cerulean/5">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-brand-black flex items-center gap-2">
              <Mail className="h-6 w-6 text-brand-dark-cyan" />
              Contact Us
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-brand-midnight/80 mb-4">If you have any questions about this Privacy Policy or our privacy practices, please contact us:</p>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <Mail className="h-4 w-4 text-brand-dark-cyan" />
                <span className="text-brand-black font-medium">Email:</span>
                <a href="mailto:team@salesdok.com" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">team@salesdok.com</a>
              </div>
              <div className="flex items-center gap-3">
                <Globe className="h-4 w-4 text-brand-dark-cyan" />
                <span className="text-brand-black font-medium">Website:</span>
                <a href="https://salesdok.com" className="text-brand-dark-cyan hover:text-brand-cerulean transition-colors">https://salesdok.com</a>
              </div>
              <div className="flex items-start gap-3">
                <FileText className="h-4 w-4 text-brand-dark-cyan mt-0.5" />
                <div>
                  <span className="text-brand-black font-medium">Mailing Address:</span>
                  <div className="text-brand-midnight/80 text-sm mt-1">
                    Appwharf, Inc.<br />
                    C-09 Sector Ecotech 16<br />
                    Greater Noida, Uttar Pradesh 201308<br />
                    India
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

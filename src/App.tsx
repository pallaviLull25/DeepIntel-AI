import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  Activity, 
  BarChart3, 
  FileText, 
  AlertCircle, 
  CheckCircle2, 
  Loader2,
  TrendingUp,
  Target,
  Zap,
  ChevronRight,
  Compass,
  BookOpen,
  PieChart,
  ArrowRight
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend,
  Cell
} from 'recharts';
import Markdown from 'react-markdown';
import { motion, AnimatePresence } from 'motion/react';
import { ResearchAgent } from './services/researchAgent';
import { ResearchStep, ResearchReport } from './types';

const COLORS = ['#111827', '#374151', '#6b7280', '#9ca3af'];

export default function App() {
  const [topic, setTopic] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  const [steps, setSteps] = useState<ResearchStep[]>([]);
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [steps]);

  const handleResearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsResearching(true);
    setSteps([]);
    setReport(null);
    setError(null);

    const agent = new ResearchAgent((step) => {
      setSteps(prev => [...prev, { ...step, status: 'completed' }]);
    });

    try {
      const result = await agent.performResearch(topic);
      setReport(result);
    } catch (err: any) {
      setError(err.message || "An error occurred during research.");
    } finally {
      setIsResearching(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper text-ink font-sans selection:bg-ink selection:text-white">
      {/* Navigation */}
      <nav className="border-b border-gray-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-ink rounded-lg flex items-center justify-center text-white">
              <Compass size={18} />
            </div>
            <h1 className="text-sm font-bold tracking-tight">DEEPINTEL</h1>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-muted">
              <div className={`w-1.5 h-1.5 rounded-full ${isResearching ? "bg-blue-500 animate-pulse" : "bg-emerald-500"}`}></div>
              {isResearching ? "Analyzing" : "Online"}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6 lg:p-12 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Input & Log */}
        <div className="lg:col-span-4 space-y-8">
          <section className="bg-white rounded-2xl p-6 soft-border card-shadow space-y-6">
            <div className="space-y-1">
              <h2 className="text-lg font-bold">Research Terminal</h2>
              <p className="text-xs text-muted">Enter a market or competitor to begin.</p>
            </div>

            <form onSubmit={handleResearch} className="space-y-3">
              <div className="relative group">
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g. 'Cloud Storage Market'"
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3 pl-10 text-sm focus:outline-none focus:ring-2 focus:ring-ink/5 focus:border-ink transition-all"
                  disabled={isResearching}
                />
                <Search className="absolute left-3 top-3 text-muted" size={16} />
              </div>
              <button
                type="submit"
                disabled={isResearching || !topic.trim()}
                className="w-full bg-ink text-white py-3 rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-gray-800 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isResearching ? (
                  <>
                    <Loader2 className="animate-spin" size={14} />
                    Processing
                  </>
                ) : (
                  <>
                    <Zap size={14} />
                    Analyze
                  </>
                )}
              </button>
            </form>
          </section>

          {/* Activity Log */}
          <section className="bg-white rounded-2xl p-6 soft-border card-shadow space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted">Process Log</h3>
              <Activity size={14} className="text-muted" />
            </div>
            
            <div 
              ref={scrollRef}
              className="h-[250px] overflow-y-auto space-y-3 pr-2 scrollbar-thin"
            >
              {steps.length === 0 && !isResearching && (
                <div className="h-full flex flex-col items-center justify-center text-center opacity-20 space-y-2">
                  <BookOpen size={24} />
                  <p className="text-[10px] font-bold uppercase tracking-wider">Idle</p>
                </div>
              )}
              {steps.map((step) => (
                <motion.div 
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  key={step.id} 
                  className="flex gap-2 text-[10px] leading-relaxed border-l-2 border-gray-100 pl-3"
                >
                  <p><span className="font-bold text-ink uppercase opacity-40 mr-1">{step.type}</span> {step.message}</p>
                </motion.div>
              ))}
              {isResearching && (
                <div className="flex gap-2 text-[10px] animate-pulse pl-3 border-l-2 border-gray-100">
                  <p className="italic text-muted">Awaiting node response...</p>
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-8">
          <AnimatePresence mode="wait">
            {error && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-50 border border-red-100 p-4 rounded-xl flex gap-3 items-center text-red-800 mb-6"
              >
                <AlertCircle size={18} />
                <p className="text-xs font-medium">{error}</p>
              </motion.div>
            )}

            {!report && !isResearching && !error && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-white rounded-3xl p-12 flex flex-col items-center justify-center text-center space-y-6 soft-border card-shadow min-h-[500px]"
              >
                <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center">
                  <Target size={24} className="text-gray-300" />
                </div>
                <div className="max-w-xs space-y-2">
                  <h3 className="text-xl font-bold">Intelligence Dashboard</h3>
                  <p className="text-xs text-muted leading-relaxed">
                    Start a new analysis to generate a deep-dive competitive report and market intelligence matrix.
                  </p>
                </div>
              </motion.div>
            )}

            {isResearching && !report && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-white rounded-3xl p-12 flex flex-col items-center justify-center text-center space-y-8 soft-border card-shadow min-h-[500px]"
              >
                <div className="relative">
                  <div className="w-16 h-16 border-2 border-gray-100 rounded-2xl"></div>
                  <div className="absolute inset-0 w-16 h-16 border-2 border-ink border-t-transparent rounded-2xl animate-spin"></div>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold">Generating Intelligence</h3>
                  <p className="text-xs text-muted max-w-xs mx-auto">
                    Traversing global market data and synthesizing competitive insights.
                  </p>
                </div>
              </motion.div>
            )}

            {report && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
              >
                {/* Summary */}
                <section className="bg-white rounded-3xl p-8 lg:p-12 soft-border card-shadow">
                  <div className="flex items-center gap-2 mb-6">
                    <FileText size={16} className="text-muted" />
                    <h2 className="text-[10px] font-bold uppercase tracking-widest text-muted">Executive Summary</h2>
                  </div>
                  <div className="prose prose-slate max-w-none text-sm leading-relaxed text-ink/80">
                    <Markdown>{report.summary}</Markdown>
                  </div>
                </section>

                {/* Matrix */}
                <section className="bg-white rounded-3xl p-8 lg:p-12 soft-border card-shadow">
                  <div className="flex items-center gap-2 mb-8">
                    <PieChart size={16} className="text-muted" />
                    <h2 className="text-[10px] font-bold uppercase tracking-widest text-muted">Market Comparison</h2>
                  </div>
                  <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={report.chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                        <XAxis 
                          dataKey="name" 
                          axisLine={false} 
                          tickLine={false}
                          tick={{ fill: '#9ca3af', fontSize: 10, fontWeight: 600 }} 
                        />
                        <YAxis 
                          axisLine={false} 
                          tickLine={false}
                          tick={{ fill: '#9ca3af', fontSize: 10 }} 
                        />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#fff', border: '1px solid #f3f4f6', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', fontSize: '12px' }}
                          cursor={{ fill: '#f9fafb' }}
                        />
                        <Bar dataKey="featureScore" name="Features" radius={[4, 4, 0, 0]}>
                          {report.chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Bar>
                        <Bar dataKey="pricingScore" name="Pricing" fill="#e5e7eb" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </section>

                {/* Competitors */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {report.competitors.map((comp, idx) => (
                    <section key={idx} className="bg-white rounded-2xl p-6 soft-border card-shadow">
                      <div className="flex justify-between items-start mb-6">
                        <h3 className="text-base font-bold">{comp.name}</h3>
                        <span className="text-[9px] font-bold bg-gray-50 text-muted px-2 py-1 rounded-md uppercase tracking-wider border border-gray-100">
                          {comp.pricing || 'Standard'}
                        </span>
                      </div>
                      
                      <div className="space-y-6">
                        <div className="space-y-2">
                          <h4 className="text-[9px] uppercase tracking-widest text-muted font-bold">Core Features</h4>
                          <ul className="space-y-1.5">
                            {comp.features.map((f, i) => (
                              <li key={i} className="text-xs flex items-start gap-2 text-ink/70">
                                <div className="w-1 h-1 bg-gray-300 rounded-full mt-1.5 shrink-0"></div>
                                <span>{f}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-50">
                          <div className="space-y-1.5">
                            <h4 className="text-[9px] uppercase tracking-widest text-ink font-bold">Strengths</h4>
                            <ul className="space-y-1">
                              {comp.strengths.map((s, i) => (
                                <li key={i} className="text-[10px] text-muted flex items-center gap-1.5">
                                  <CheckCircle2 size={10} className="text-emerald-500" /> {s}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div className="space-y-1.5">
                            <h4 className="text-[9px] uppercase tracking-widest text-muted font-bold">Gaps</h4>
                            <ul className="space-y-1">
                              {comp.weaknesses.map((w, i) => (
                                <li key={i} className="text-[10px] text-muted flex items-center gap-1.5">
                                  <div className="w-1 h-1 bg-gray-300 rounded-full"></div> {w}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    </section>
                  ))}
                </div>

                {/* Trends & Advice */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <section className="bg-white rounded-3xl p-8 soft-border card-shadow">
                    <div className="flex items-center gap-2 mb-6">
                      <TrendingUp size={16} className="text-muted" />
                      <h2 className="text-[10px] font-bold uppercase tracking-widest text-muted">Market Trajectory</h2>
                    </div>
                    <ul className="space-y-4">
                      {report.marketTrends.map((trend, i) => (
                        <li key={i} className="flex gap-3">
                          <span className="text-xs font-bold text-gray-300">0{i+1}</span>
                          <p className="text-xs leading-relaxed text-ink/70">{trend}</p>
                        </li>
                      ))}
                    </ul>
                  </section>

                  <section className="bg-ink text-white rounded-3xl p-8 shadow-xl">
                    <div className="flex items-center gap-2 mb-6">
                      <Zap size={16} className="text-gray-400" />
                      <h2 className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Strategic Directives</h2>
                    </div>
                    <ul className="space-y-4">
                      {report.recommendations.map((rec, i) => (
                        <li key={i} className="flex gap-3">
                          <div className="mt-0.5 shrink-0"><CheckCircle2 size={14} className="text-gray-400" /></div>
                          <p className="text-xs font-medium leading-relaxed">{rec}</p>
                        </li>
                      ))}
                    </ul>
                  </section>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      <footer className="border-t border-gray-100 p-8 mt-12">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4 text-[9px] font-bold uppercase tracking-widest text-muted">
          <div className="flex items-center gap-2">
            <Compass size={14} />
            <span>DEEPINTEL ENGINE v1.2</span>
          </div>
          <div className="flex gap-8">
            <a href="#" className="hover:text-ink transition-colors">Methodology</a>
            <a href="#" className="hover:text-ink transition-colors">API</a>
            <a href="#" className="hover:text-ink transition-colors">Privacy</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

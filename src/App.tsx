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
  Cell
} from 'recharts';
import Markdown from 'react-markdown';
import { motion, AnimatePresence } from 'motion/react';
import IntelAtlasLogo from './components/IntelAtlasLogo';
import { ResearchAgent } from './services/researchAgent';
import { EvaluationSummary, ResearchPlan, ResearchReport, ResearchStep, ToolTrace } from './types';
import intelAtlas from './assets/intel-atlas.svg';

const COLORS = ['#111827', '#374151', '#6b7280', '#9ca3af'];
const HERO_PILLS = ['Recursive research loop', 'Grounded evidence ledger', 'Live tool traces'];
const HERO_METRICS = [
  {
    label: 'Planner + Critic',
    value: '2-pass',
    detail: 'Breaks down the brief, identifies gaps, and loops back before final synthesis.',
  },
  {
    label: 'Fetch + Rank',
    value: 'Hybrid',
    detail: 'Blends search results, fetched pages, and ranked passages into one evidence layer.',
  },
  {
    label: 'Confidence + Eval',
    value: 'Scored',
    detail: 'Ships every run with confidence, coverage gaps, and an effectiveness summary.',
  },
];
const SIDE_SIGNALS = [
  {
    title: 'Situation Room',
    description: 'Built to feel like an analyst cockpit: ambient map, live process stream, and source-backed output.',
  },
  {
    title: 'Decision Velocity',
    description: 'Structured for quick operator scans instead of generic chatbot prose.',
  },
  {
    title: 'Research Memory',
    description: 'Local corpus storage keeps each run closer to an actual intelligence workflow.',
  },
];

export default function App() {
  const [topic, setTopic] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  const [steps, setSteps] = useState<ResearchStep[]>([]);
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [plan, setPlan] = useState<ResearchPlan | null>(null);
  const [toolTraces, setToolTraces] = useState<ToolTrace[]>([]);
  const [evaluation, setEvaluation] = useState<EvaluationSummary | null>(null);
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
    setPlan(null);
    setToolTraces([]);
    setEvaluation(null);
    setError(null);

    const agent = new ResearchAgent((step) => {
      setSteps(prev => [...prev, { ...step, status: 'completed' }]);
    });

    try {
      const result = await agent.performResearch(topic);
      setReport(result.report);
      setPlan(result.plan || null);
      setToolTraces(result.toolTraces || []);
      setEvaluation(result.evaluation || null);
    } catch (err: any) {
      setError(err.message || "An error occurred during research.");
    } finally {
      setIsResearching(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-paper text-ink font-sans selection:bg-ink selection:text-white">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_14%_10%,rgba(15,118,110,0.12),transparent_28%),radial-gradient(circle_at_86%_14%,rgba(213,138,46,0.14),transparent_26%),linear-gradient(180deg,rgba(255,255,255,0.45),rgba(247,243,235,0.8))]" />
        <div className="mesh-overlay absolute inset-0 opacity-70" />
        <motion.div
          initial={{ opacity: 0, scale: 1.04 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.1, ease: 'easeOut' }}
          className="absolute right-[-14rem] top-[-7rem] w-[42rem] opacity-70 mix-blend-multiply lg:w-[62rem]"
        >
          <img src={intelAtlas} alt="" className="w-full object-contain" />
        </motion.div>
        <div className="absolute left-[-7rem] top-[18rem] h-[18rem] w-[18rem] rounded-full bg-[radial-gradient(circle,rgba(15,118,110,0.22),transparent_72%)] blur-3xl" />
        <div className="absolute right-[12%] top-[42%] h-[17rem] w-[17rem] rounded-full bg-[radial-gradient(circle,rgba(213,138,46,0.2),transparent_70%)] blur-3xl" />
      </div>

      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-white/40 bg-white/45 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <IntelAtlasLogo size={36} />
            <div className="space-y-0.5">
              <h1 className="text-sm font-bold tracking-tight">INTELATLAS</h1>
              <p className="text-[9px] font-bold uppercase tracking-[0.22em] text-muted/80">Grounded Competitive Intelligence</p>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-muted">
              <div className={`w-1.5 h-1.5 rounded-full ${isResearching ? "bg-blue-500 animate-pulse" : "bg-emerald-500"}`}></div>
              {isResearching ? "Analyzing" : "Online"}
            </div>
          </div>
        </div>
      </nav>

      <main className="relative max-w-7xl mx-auto px-6 py-8 lg:px-12 lg:py-10 space-y-8">
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: 'easeOut' }}
            className="panel-dark relative overflow-hidden rounded-[2rem] p-8 lg:col-span-7 lg:p-10 text-white"
          >
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(15,118,110,0.22),transparent_34%),linear-gradient(140deg,rgba(255,255,255,0.03),transparent_55%)]" />
            <div className="absolute right-[-10rem] top-[-9rem] w-[32rem] opacity-25 mix-blend-screen lg:w-[40rem]">
              <img src={intelAtlas} alt="" className="w-full object-contain" />
            </div>
            <div className="relative space-y-6">
              <div className="flex flex-wrap gap-2">
                {HERO_PILLS.map((item) => (
                  <span
                    key={item}
                    className="hero-chip rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-[0.22em] text-white/78"
                  >
                    {item}
                  </span>
                ))}
              </div>

              <div className="max-w-2xl space-y-4">
                <p className="text-[11px] font-bold uppercase tracking-[0.28em] text-white/55">Competitive intelligence engine</p>
                <h2 className="text-4xl font-semibold leading-[1.02] tracking-tight lg:text-[3.55rem]">
                  Turn a vague market prompt into an evidence-backed brief.
                </h2>
                <p className="max-w-xl text-sm leading-relaxed text-white/72 lg:text-[15px]">
                  IntelAtlas plans the investigation, calls live tools, fetches source pages, ranks evidence, and returns a report that reads like analyst work instead of generic model output.
                </p>
              </div>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                {HERO_METRICS.map((item) => (
                  <div key={item.label} className="rounded-[1.5rem] border border-white/12 bg-white/6 p-4 backdrop-blur-sm">
                    <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-white/48">{item.label}</p>
                    <p className="mt-3 text-2xl font-semibold tracking-tight">{item.value}</p>
                    <p className="mt-2 text-xs leading-relaxed text-white/62">{item.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.section>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:col-span-5 lg:grid-cols-1">
            {SIDE_SIGNALS.map((item, index) => (
              <motion.article
                key={item.title}
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.55, delay: 0.12 + (index * 0.08), ease: 'easeOut' }}
                className="metric-tile rounded-[1.75rem] p-5"
              >
                <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-muted">{item.title}</p>
                <p className="mt-3 text-sm font-semibold text-ink">{item.description}</p>
              </motion.article>
            ))}
          </div>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Input & Log */}
        <div className="lg:col-span-4 space-y-8">
          <section className="panel-surface rounded-[1.75rem] p-6 space-y-6">
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
                  className="w-full rounded-xl border border-white/60 bg-white/70 p-3 pl-10 text-sm shadow-[inset_0_1px_0_rgba(255,255,255,0.55)] focus:outline-none focus:ring-2 focus:ring-ink/8 focus:border-ink/30 transition-all"
                  disabled={isResearching}
                />
                <Search className="absolute left-3 top-3 text-muted" size={16} />
              </div>
              <button
                type="submit"
                disabled={isResearching || !topic.trim()}
                className="w-full rounded-xl bg-[linear-gradient(145deg,#111827,#1f4a57)] py-3 text-xs font-bold uppercase tracking-widest text-white shadow-[0_18px_40px_rgba(17,24,39,0.22)] transition-all hover:-translate-y-px hover:shadow-[0_22px_48px_rgba(17,24,39,0.3)] disabled:opacity-50 flex items-center justify-center gap-2"
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
          <section className="panel-surface rounded-[1.75rem] p-6 space-y-4">
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
                  className="flex gap-2 text-[10px] leading-relaxed border-l-2 border-teal-900/10 pl-3"
                >
                  <p><span className="font-bold text-ink uppercase opacity-40 mr-1">{step.type}</span> {step.message}</p>
                </motion.div>
              ))}
              {isResearching && (
                <div className="flex gap-2 text-[10px] animate-pulse pl-3 border-l-2 border-teal-900/10">
                  <p className="italic text-muted">Awaiting node response...</p>
                </div>
              )}
            </div>
          </section>

          <section className="panel-surface rounded-[1.75rem] p-6 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted">Research Plan</h3>
              <Target size={14} className="text-muted" />
            </div>

            {!plan && (
              <p className="text-xs text-muted">The planner will populate objective, sub-questions, and success criteria after a run.</p>
            )}

            {plan && (
              <div className="space-y-4">
                <div className="rounded-2xl border border-white/70 bg-white/60 p-4">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-muted mb-2">Objective</p>
                  <p className="text-xs leading-relaxed text-ink/70">{plan.objective}</p>
                </div>

                <div className="space-y-2">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-muted">Sub-Questions</p>
                  <ul className="space-y-2">
                    {plan.subQuestions.map((item) => (
                      <li key={item} className="text-xs leading-relaxed text-ink/70 flex gap-2">
                        <ChevronRight size={12} className="mt-0.5 shrink-0 text-gray-400" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
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
                className="panel-surface relative overflow-hidden rounded-[2rem] p-12 flex flex-col items-center justify-center text-center space-y-6 min-h-[500px]"
              >
                <div className="absolute right-[-7rem] top-[-5rem] w-[22rem] opacity-20 mix-blend-multiply">
                  <img src={intelAtlas} alt="" className="w-full object-contain" />
                </div>
                <div className="w-16 h-16 rounded-2xl bg-[linear-gradient(145deg,#eef5f4,#ffffff)] shadow-[0_20px_40px_rgba(15,23,42,0.08)] flex items-center justify-center">
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
                className="panel-dark relative overflow-hidden rounded-[2rem] p-12 flex flex-col items-center justify-center text-center space-y-8 min-h-[500px] text-white"
              >
                <div className="absolute right-[-8rem] top-[-5rem] w-[24rem] opacity-20 mix-blend-screen">
                  <img src={intelAtlas} alt="" className="w-full object-contain" />
                </div>
                <div className="relative">
                  <div className="w-16 h-16 border-2 border-white/15 rounded-2xl"></div>
                  <div className="absolute inset-0 w-16 h-16 border-2 border-white border-t-transparent rounded-2xl animate-spin"></div>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold">Generating Intelligence</h3>
                  <p className="text-xs text-white/65 max-w-xs mx-auto">
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
                <section className="panel-surface rounded-[2rem] p-8 lg:p-12">
                  <div className="flex items-center gap-2 mb-6">
                    <FileText size={16} className="text-muted" />
                    <h2 className="text-[10px] font-bold uppercase tracking-widest text-muted">Executive Summary</h2>
                  </div>
                  <div className="prose prose-slate max-w-none text-sm leading-relaxed text-ink/80">
                    <Markdown>{report.summary}</Markdown>
                  </div>
                </section>

                {/* Matrix */}
                <section className="panel-surface rounded-[2rem] p-8 lg:p-12">
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
                    <section key={idx} className="panel-surface rounded-[1.75rem] p-6">
                      <div className="flex justify-between items-start mb-6">
                        <h3 className="text-base font-bold">{comp.name}</h3>
                        <div className="flex flex-col items-end gap-2">
                          <span className="text-[9px] font-bold bg-gray-50 text-muted px-2 py-1 rounded-md uppercase tracking-wider border border-gray-100">
                            {comp.pricing || 'Standard'}
                          </span>
                          {typeof comp.confidence === 'number' && (
                            <span className="text-[9px] font-bold bg-emerald-50 text-emerald-700 px-2 py-1 rounded-md uppercase tracking-wider border border-emerald-100">
                              {comp.confidence}% confidence
                            </span>
                          )}
                        </div>
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
                  <section className="panel-surface rounded-[2rem] p-8">
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

                  <section className="panel-dark rounded-[2rem] p-8 text-white">
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

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                  <section className="panel-surface rounded-[2rem] p-8">
                    <div className="flex items-center gap-2 mb-6">
                      <BarChart3 size={16} className="text-muted" />
                      <h2 className="text-[10px] font-bold uppercase tracking-widest text-muted">Confidence Signals</h2>
                    </div>

                    <div className="space-y-4">
                      {report.confidence.length === 0 && (
                        <p className="text-xs text-muted">No section confidence scores were returned.</p>
                      )}

                      {report.confidence.map((item) => (
                        <div key={item.name} className="space-y-2">
                          <div className="flex items-center justify-between gap-3">
                            <h3 className="text-[10px] font-bold uppercase tracking-wider text-ink">{item.name}</h3>
                            <span className="text-[10px] font-bold text-muted">{item.score}%</span>
                          </div>
                          <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
                            <div
                              className="h-full bg-ink rounded-full transition-all"
                              style={{ width: `${Math.max(0, Math.min(item.score, 100))}%` }}
                            />
                          </div>
                          <p className="text-xs leading-relaxed text-ink/60">{item.rationale}</p>
                        </div>
                      ))}
                    </div>

                    <div className="mt-8 pt-6 border-t border-gray-100 space-y-3">
                      <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted">Open Coverage Gaps</h3>
                      {report.gaps.length === 0 && (
                        <p className="text-xs text-emerald-700">No unresolved gaps were carried into the report.</p>
                      )}
                      {report.gaps.map((gap) => (
                        <div key={`${gap.topic}-${gap.reason}`} className="rounded-2xl border border-amber-100 bg-amber-50/70 p-4 space-y-1">
                          <div className="flex items-center justify-between gap-3">
                            <p className="text-xs font-bold text-amber-900">{gap.topic}</p>
                            <span className="text-[9px] font-bold uppercase tracking-wider text-amber-700">{gap.severity}</span>
                          </div>
                          <p className="text-xs leading-relaxed text-amber-900/80">{gap.reason}</p>
                        </div>
                      ))}
                    </div>
                  </section>

                  <section className="panel-surface rounded-[2rem] p-8">
                    <div className="flex items-center gap-2 mb-6">
                      <BookOpen size={16} className="text-muted" />
                      <h2 className="text-[10px] font-bold uppercase tracking-widest text-muted">Evidence Ledger</h2>
                    </div>

                    <div className="space-y-4">
                      {report.evidence.length === 0 && (
                        <p className="text-xs text-muted">No grounded evidence passages were returned.</p>
                      )}

                      {report.evidence.map((item) => (
                        <article key={item.id} className="rounded-2xl border border-gray-100 p-4 space-y-3">
                          <div className="flex items-start justify-between gap-4">
                            <div className="space-y-1">
                              <p className="text-[10px] font-bold uppercase tracking-widest text-muted">{item.query || item.sourceType}</p>
                              <p className="text-xs leading-relaxed text-ink/70">{item.summary}</p>
                            </div>
                            {typeof item.retrievalScore === 'number' && (
                              <div className="shrink-0 flex flex-col items-end gap-1">
                                <span className="rounded-full bg-gray-50 px-2 py-1 text-[9px] font-bold text-muted border border-gray-100">
                                  score {item.retrievalScore.toFixed(2)}
                                </span>
                                {typeof item.lexicalScore === 'number' && typeof item.semanticScore === 'number' && (
                                  <span className="text-[9px] text-muted">
                                    lex {item.lexicalScore.toFixed(2)} / sem {item.semanticScore.toFixed(2)}
                                  </span>
                                )}
                              </div>
                            )}
                          </div>

                          {item.excerpt && (
                            <blockquote className="border-l-2 border-gray-200 pl-3 text-xs leading-relaxed text-ink/60">
                              {item.excerpt}
                            </blockquote>
                          )}

                          <div className="space-y-2">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-muted">Sources</p>
                            <div className="space-y-2">
                              {item.citations.map((citation) => (
                                <a
                                  key={citation.url}
                                  href={citation.url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="block rounded-xl border border-gray-100 px-3 py-2 hover:border-gray-200 transition-colors"
                                >
                                  <p className="text-xs font-medium text-ink/80">{citation.title}</p>
                                  <p className="text-[10px] text-muted break-all">{citation.url}</p>
                                </a>
                              ))}
                            </div>
                          </div>
                        </article>
                      ))}
                    </div>
                  </section>
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                  <section className="panel-surface rounded-[2rem] p-8">
                    <div className="flex items-center gap-2 mb-6">
                      <Activity size={16} className="text-muted" />
                      <h2 className="text-[10px] font-bold uppercase tracking-widest text-muted">Run Evaluation</h2>
                    </div>

                    {!evaluation && (
                      <p className="text-xs text-muted">No evaluation summary was returned for this run.</p>
                    )}

                    {evaluation && (
                      <div className="space-y-6">
                        <div className="grid grid-cols-2 gap-3">
                          {[
                            ['Groundedness', evaluation.groundedness],
                            ['Completeness', evaluation.completeness],
                            ['Citation Coverage', evaluation.citationCoverage],
                            ['Reflection Quality', evaluation.reflectionQuality],
                          ].map(([label, score]) => (
                            <div key={label} className="rounded-2xl border border-gray-100 bg-gray-50/70 p-4 space-y-2">
                              <p className="text-[10px] font-bold uppercase tracking-widest text-muted">{label}</p>
                              <p className="text-lg font-bold text-ink">{score}%</p>
                            </div>
                          ))}
                        </div>

                        <div className="space-y-2">
                          <p className="text-[10px] font-bold uppercase tracking-widest text-muted">Notes</p>
                          <ul className="space-y-2">
                            {evaluation.notes.map((note) => (
                              <li key={note} className="text-xs leading-relaxed text-ink/70 flex gap-2">
                                <ArrowRight size={12} className="mt-0.5 shrink-0 text-gray-400" />
                                <span>{note}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}
                  </section>

                  <section className="panel-surface rounded-[2rem] p-8">
                    <div className="flex items-center gap-2 mb-6">
                      <Activity size={16} className="text-muted" />
                      <h2 className="text-[10px] font-bold uppercase tracking-widest text-muted">Tool Trace</h2>
                    </div>

                    {toolTraces.length === 0 && (
                      <p className="text-xs text-muted">No tool traces were recorded for this run.</p>
                    )}

                    <div className="space-y-3">
                      {toolTraces.map((trace) => (
                        <article key={trace.id} className="rounded-2xl border border-gray-100 p-4 space-y-2">
                          <div className="flex items-center justify-between gap-3">
                            <div>
                              <p className="text-[10px] font-bold uppercase tracking-widest text-muted">{trace.toolName}</p>
                              <p className="text-xs font-medium text-ink/80">{trace.whyUsed}</p>
                            </div>
                            <span className={`rounded-full px-2 py-1 text-[9px] font-bold uppercase tracking-wider border ${trace.success ? 'border-emerald-100 bg-emerald-50 text-emerald-700' : 'border-amber-100 bg-amber-50 text-amber-700'}`}>
                              {trace.latencyMs} ms
                            </span>
                          </div>
                          <p className="text-[10px] text-muted break-words">{trace.inputSummary}</p>
                          <p className="text-xs leading-relaxed text-ink/65">{trace.outputSummary}</p>
                        </article>
                      ))}
                    </div>
                  </section>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        </section>
      </main>

      <footer className="relative border-t border-white/35 p-8 mt-12 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4 text-[9px] font-bold uppercase tracking-widest text-muted">
          <div className="flex items-center gap-2">
            <IntelAtlasLogo size={22} className="rounded-[0.7rem]" />
            <span>INTELATLAS ENGINE v1.2</span>
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

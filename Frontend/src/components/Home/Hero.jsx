const Hero = () => {
  return (
    <section className="relative min-h-screen bg-slate-950 overflow-hidden">

      {/* Background Glow */}
      <div className="absolute top-20 left-20 h-72 w-72 rounded-full bg-blue-500/20 blur-3xl"></div>
      <div className="absolute bottom-20 right-20 h-96 w-96 rounded-full bg-purple-600/20 blur-3xl"></div>

      <div className="relative max-w-7xl mx-auto px-8 py-24 flex flex-col lg:flex-row items-center justify-between">

        {/* Left Side */}
        <div className="max-w-2xl">

          <p className="text-blue-400 font-semibold mb-4 tracking-widest uppercase">
            AI Powered News Aggregation
          </p>

          <h1 className="text-5xl lg:text-7xl font-extrabold leading-tight">

            Stay Ahead with

            <span className="block bg-gradient-to-r from-blue-400 via-cyan-300 to-purple-500 bg-clip-text text-transparent">
              Intelligent News
            </span>

          </h1>

          <p className="mt-8 text-slate-300 text-lg leading-8">

            Aggregate articles from multiple trusted sources,
            generate AI-powered summaries using Ollama,
            compare viewpoints, and stay informed without information overload.

          </p>

          <div className="mt-10 flex flex-wrap gap-4">

            <button className="px-8 py-4 rounded-xl bg-blue-600 hover:bg-blue-700 transition font-semibold">
              Get Started
            </button>

            <button className="px-8 py-4 rounded-xl border border-slate-600 hover:border-blue-400 transition font-semibold">
              Learn More
            </button>

          </div>

        </div>

        {/* Right Side */}

        <div className="mt-20 lg:mt-0">

          <div className="w-[420px] rounded-3xl border border-slate-700 bg-slate-900/70 backdrop-blur-lg p-8 shadow-2xl">

            <h3 className="text-2xl font-bold mb-6">
              Live AI Summary
            </h3>

            <div className="space-y-5">

              <div className="rounded-xl bg-slate-800 p-4">

                <h4 className="font-semibold mb-2">
                  📰 Technology
                </h4>

                <p className="text-slate-400 text-sm">
                  AI summarizes breaking technology news
                  collected from multiple publishers into
                  concise, unbiased insights.
                </p>

              </div>

              <div className="rounded-xl bg-slate-800 p-4">

                <h4 className="font-semibold mb-2">
                  ⚡ FastAPI + Ollama
                </h4>

                <p className="text-slate-400 text-sm">
                  Lightning-fast backend powered by FastAPI
                  with local AI inference using Ollama.
                </p>

              </div>

            </div>

          </div>

        </div>

      </div>

    </section>
  );
};

export default Hero;
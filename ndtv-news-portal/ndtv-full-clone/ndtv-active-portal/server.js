const express = require('express');
const Parser = require('rss-parser');
const cron = require('node-cron');

const app = express();
const parser = new Parser();
const PORT = process.env.PORT || 3000;

// ক্যাটাগরি ভিত্তিক গ্লোবাল স্টোরেজ
let newsState = {
  all: [],
  india: [],
  world: [],
  business: [],
  tech: [],
  sports: [],
  entertainment: []
};

const stockTicker = [
  { name: "SENSEX", val: "81,420.15", change: "+420.30", up: true },
  { name: "NIFTY 50", val: "24,890.60", change: "+125.40", up: true },
  { name: "GOLD (10g)", val: "₹76,450", change: "-110.00", up: false },
  { name: "USD/INR", val: "83.92", change: "+0.04", up: true }
];

const fallbackThumbs = [
  "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=800&q=80"
];

function sanitizeItems(items, categoryName) {
  return items.map((item, idx) => {
    let cleanTitle = item.title || "Latest Headline Update";
    let source = "News Desk";
    if (cleanTitle.includes(" - ")) {
      const parts = cleanTitle.split(" - ");
      source = parts.pop();
      cleanTitle = parts.join(" - ");
    }
    return {
      id: `${categoryName.toLowerCase()}-${idx}`,
      title: cleanTitle,
      source: source,
      link: item.link || "#",
      category: categoryName.toUpperCase(),
      time: new Date(item.pubDate || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      image: fallbackThumbs[idx % fallbackThumbs.length],
      summary: item.contentSnippet ? item.contentSnippet.replace(/<[^>]*>?/gm, '').slice(0, 160) + "..." : "Follow live reporting for breaking developments on this story."
    };
  });
}

// স্বয়ংক্রিয়ভাবে সব ক্যাটাগরির RSS ফেচ করা
async function syncAllFeeds() {
  try {
    console.log('[Auto-Sync] লাইভ ফিড সংগ্রহ করা হচ্ছে...');
    const [topFeed, worldFeed, bizFeed, techFeed, sportsFeed, entFeed] = await Promise.all([
      parser.parseURL('https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en'),
      parser.parseURL('https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-IN&gl=IN&ceid=IN:en'),
      parser.parseURL('https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en'),
      parser.parseURL('https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en'),
      parser.parseURL('https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en'),
      parser.parseURL('https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-IN&gl=IN&ceid=IN:en')
    ]);

    newsState.india = sanitizeItems(topFeed.items.slice(0, 12), "India");
    newsState.world = sanitizeItems(worldFeed.items.slice(0, 12), "World");
    newsState.business = sanitizeItems(bizFeed.items.slice(0, 12), "Business");
    newsState.tech = sanitizeItems(techFeed.items.slice(0, 12), "Tech");
    newsState.sports = sanitizeItems(sportsFeed.items.slice(0, 12), "Sports");
    newsState.entertainment = sanitizeItems(entFeed.items.slice(0, 12), "Entertainment");
    newsState.all = [...newsState.india, ...newsState.business, ...newsState.tech, ...newsState.sports];

    console.log('[Auto-Sync Done] সমস্ত ক্যাটাগরি সক্রিয় ও আপডেটেড।');
  } catch (err) {
    console.error('[Sync Error]:', err.message);
  }
}

syncAllFeeds();
cron.schedule('*/15 * * * *', syncAllFeeds);

// লাইভ ডেটা API এন্ডপয়েন্ট
app.get('/api/news-state', (req, res) => {
  res.json(newsState);
});

// সম্পূর্ণ সক্রিয় ইন্টারেক্টিভ ফ্রন্টএন্ড UI
app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>24EarlyNews | Fully Active NDTV Suite</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: { extend: {} }
    }
  </script>
  <style>
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .animate-marquee { display: inline-block; white-space: nowrap; animation: marquee 35s linear infinite; }
    .animate-marquee:hover { animation-play-state: paused; }
  </style>
</head>
<body class="bg-[#f0f2f5] dark:bg-[#121212] text-[#1e2022] dark:text-gray-100 font-sans transition-colors duration-200">

  <!-- ১. মার্কেট ও ইউটিলিটি টপ স্ট্রিপ -->
  <div class="bg-[#1f2024] text-white text-[11px] py-1.5 px-4 border-b border-gray-700">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-6 overflow-x-auto whitespace-nowrap">
        <span class="font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1">
          <i class="fa-solid fa-chart-line text-yellow-400"></i> MARKETS:
        </span>
        ${stockTicker.map(s => `
          <span class="flex items-center gap-1">
            <span class="font-bold text-gray-200">${s.name}</span>
            <span>${s.val}</span>
            <span class="${s.up ? 'text-green-400' : 'text-red-400'} font-semibold">(${s.change})</span>
          </span>
        `).join('')}
      </div>
      <div class="hidden md:flex items-center space-x-4 text-gray-300">
        <span><i class="fa-solid fa-cloud-sun text-yellow-400 mr-1"></i> New Delhi 28°C</span>
        <span>•</span>
        <button onclick="toggleTheme()" class="hover:text-yellow-400 transition flex items-center gap-1 font-bold">
          <i id="themeIcon" class="fa-solid fa-moon"></i> THEME
        </button>
      </div>
    </div>
  </div>

  <!-- ২. নেটওয়ার্ক চ্যানেল ও ল্যাঙ্গুয়েজ বার -->
  <div class="bg-[#111317] text-gray-400 text-xs px-4 border-b border-gray-800">
    <div class="max-w-7xl mx-auto flex items-center justify-between py-1">
      <div class="flex space-x-5 font-semibold">
        <button onclick="filterCategory('all')" class="cat-btn text-white font-bold hover:text-white transition">24x7 DESK</button>
        <button onclick="filterCategory('india')" class="cat-btn hover:text-white transition">INDIA</button>
        <button onclick="filterCategory('business')" class="cat-btn hover:text-white transition">PROFIT</button>
        <button onclick="filterCategory('sports')" class="cat-btn hover:text-white transition">CRICKET</button>
        <button onclick="filterCategory('tech')" class="cat-btn hover:text-white transition">TECH</button>
        <button onclick="filterCategory('entertainment')" class="cat-btn hover:text-white transition">MOVIES</button>
      </div>
      <div class="flex items-center space-x-3 text-[11px]">
        <button onclick="switchLang('en')" id="langEn" class="text-white font-bold">EN</button>
        <span>|</span>
        <button onclick="switchLang('bn')" id="langBn" class="text-gray-400 hover:text-white">বাংলা</button>
      </div>
    </div>
  </div>

  <!-- ৩. প্রধান হেডার ও লাইভ সার্চ -->
  <header class="bg-white dark:bg-[#1a1a1a] sticky top-0 z-40 shadow-sm border-b border-gray-200 dark:border-gray-800 transition-colors">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
      <div class="flex items-center space-x-6">
        <a href="/" class="text-3xl font-black tracking-tighter text-red-600 flex items-center">
          24<span class="text-slate-900 dark:text-white">EARLYNEWS</span>
        </a>
      </div>

      <!-- অ্যাক্টিভ সার্চ ইনপুট -->
      <div class="flex-1 max-w-md relative hidden sm:block">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-gray-400 text-xs"></i>
        <input 
          type="text" 
          id="searchBox" 
          onkeyup="handleSearch(this.value)" 
          placeholder="Search live news, topics, companies..." 
          class="w-full pl-8 pr-4 py-1.5 text-xs rounded-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white focus:outline-none focus:border-red-600"
        />
      </div>

      <div class="flex items-center space-x-3">
        <button onclick="openLiveTv()" class="bg-red-600 hover:bg-red-700 text-white text-xs font-black px-3.5 py-1.5 rounded flex items-center gap-1.5 shadow-sm animate-pulse">
          <i class="fa-solid fa-play text-[10px]"></i> WATCH LIVE TV
        </button>
      </div>
    </div>

    <!-- ৪. ব্রেকিং নিউজ টিকার -->
    <div class="bg-[#d90429] text-white text-xs py-1.5 px-4 flex items-center">
      <div class="max-w-7xl mx-auto w-full flex items-center">
        <span class="bg-black text-white font-black px-2 py-0.5 rounded text-[10px] tracking-widest uppercase mr-3 shrink-0 flex items-center gap-1">
          <i class="fa-solid fa-bolt text-yellow-400"></i> BREAKING
        </span>
        <div class="overflow-hidden relative w-full whitespace-nowrap">
          <div id="tickerContent" class="animate-marquee font-semibold text-white">
            Syncing live satellite news feeds...
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- ৫. লাইভ স্কোরবোর্ড উইজেট -->
  <div class="max-w-7xl mx-auto px-4 mt-3">
    <div class="bg-white dark:bg-[#1e1e1e] border border-gray-200 dark:border-gray-800 rounded p-2.5 flex items-center justify-between text-xs shadow-sm">
      <div class="flex items-center space-x-3">
        <span class="bg-blue-600 text-white font-bold px-2 py-0.5 rounded text-[10px]">CRICKET LIVE</span>
        <span class="font-bold">India vs Australia - 2nd Test</span>
        <span class="text-gray-500 dark:text-gray-400">IND 284/6 (50) • AUS 142/3 (26.2)</span>
        <span class="text-red-600 font-bold animate-pulse">In Progress</span>
      </div>
      <button onclick="filterCategory('sports')" class="text-blue-600 dark:text-blue-400 hover:underline font-bold hidden sm:inline">
        Full Scorecard & Coverage &rarr;
      </button>
    </div>
  </div>

  <!-- ৬. কন্টেন্ট এরিয়া (ডায়নামিকালি রেন্ডার হবে) -->
  <main class="max-w-7xl mx-auto px-4 py-5">
    <div id="contentGrid" class="space-y-8">
      <!-- জাভাস্ক্রিপ্ট দ্বারা ফিল্টার ও আপডেট হবে -->
    </div>
  </main>

  <!-- ৭. লাইভ টিভি পপআপ মডাল -->
  <div id="tvModal" class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-black border border-gray-800 rounded-lg max-w-3xl w-full overflow-hidden shadow-2xl">
      <div class="flex justify-between items-center p-3 bg-gray-900 border-b border-gray-800 text-white">
        <span class="font-bold text-sm flex items-center gap-2">
          <span class="w-2.5 h-2.5 bg-red-600 rounded-full animate-ping"></span>
          24EarlyNews 24x7 Live Stream Desk
        </span>
        <button onclick="closeLiveTv()" class="text-gray-400 hover:text-white text-lg font-bold px-2">&times;</button>
      </div>
      <div class="aspect-video bg-black flex items-center justify-center relative">
        <iframe class="w-full h-full" src="https://www.youtube.com/embed/live_stream?channel=UC4R8DWoMoI7CAwX8_BQOrMg" title="Live Stream" frameborder="0" allowfullscreen></iframe>
      </div>
    </div>
  </div>

  <!-- ৮. ফুটার -->
  <footer class="bg-[#111317] text-gray-400 text-xs mt-12 border-t border-gray-800 pt-8 pb-12">
    <div class="max-w-7xl mx-auto px-4 text-center space-y-2">
      <p class="font-bold text-white text-sm">24EARLYNEWS &copy; 2026. All Features Activated.</p>
      <p class="text-[11px] text-gray-500">Automated Real-Time News Delivery Suite.</p>
    </div>
  </footer>

  <!-- ক্লায়েন্ট-সাইড অ্যাক্টিভেশন লজিক -->
  <script>
    let rawNews = {};
    let currentCategory = 'all';

    // সার্ভার থেকে ডেটা ফেচ
    async function loadLiveData() {
      try {
        const res = await fetch('/api/news-state');
        rawNews = await res.json();
        
        // টিকার আপডেট
        if (rawNews.all && rawNews.all.length) {
          document.getElementById('tickerContent').innerHTML = rawNews.all.slice(0, 10).map(n => n.title).join("  &nbsp;•&nbsp;  ");
        }
        renderNews();
      } catch (err) {
        console.error("ডেটা লোড এরর:", err);
      }
    }

    // ক্যাটাগরি ফিল্টার
    function filterCategory(cat) {
      currentCategory = cat;
      document.getElementById('searchBox').value = '';
      renderNews();
    }

    // লাইভ সার্চ ফিল্টার
    function handleSearch(query) {
      if (!rawNews.all) return;
      const filtered = rawNews.all.filter(item => 
        item.title.toLowerCase().includes(query.toLowerCase()) || 
        item.summary.toLowerCase().includes(query.toLowerCase())
      );
      renderCustomList(filtered, 'Search Results for: "' + query + '"');
    }

    // রেন্ডারিং লজিক (NDTV 3-কলাম আর্কিটেকচার)
    function renderNews() {
      const items = (currentCategory === 'all') ? rawNews.all : rawNews[currentCategory] || [];
      if (!items || items.length === 0) return;

      const lead = items[0];
      const center = items.slice(1, 5);
      const right = items.slice(5, 12);
      const more = items.slice(12);

      let html = \`
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
          <!-- বাম কলাম (Lead) -->
          <section class="lg:col-span-6 bg-white dark:bg-[#1a1a1a] p-4 rounded-lg border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col justify-between">
            <div>
              <a href="\${lead.link}" target="_blank" class="block group">
                <div class="relative overflow-hidden rounded bg-black aspect-video mb-3">
                  <img src="\${lead.image}" alt="\${lead.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500 opacity-95">
                  <span class="absolute top-3 left-3 bg-red-600 text-white text-[10px] font-black uppercase px-2 py-0.5 rounded">
                    \${lead.category}
                  </span>
                </div>
                <h1 class="text-2xl md:text-3xl font-black text-gray-900 dark:text-white group-hover:text-red-600 transition leading-tight">
                  \${lead.title}
                </h1>
                <p class="mt-2 text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                  \${lead.summary}
                </p>
              </a>
              <div class="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 space-y-2">
                <p class="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase">Key Developments:</p>
                <ul class="text-xs text-gray-600 dark:text-gray-400 space-y-1.5 list-disc pl-4">
                  <li>Direct continuous news monitoring through live verified feeds.</li>
                  <li>Real-time market responses tracking key policy metrics.</li>
                  <li>Follow live desk reporting for instant statements.</li>
                </ul>
              </div>
            </div>
            <div class="mt-4 flex items-center justify-between text-xs text-gray-400 pt-3 border-t border-gray-100 dark:border-gray-800">
              <span><i class="fa-regular fa-clock mr-1"></i> \${lead.time}</span>
              <span class="font-bold text-red-600">\${lead.source}</span>
            </div>
          </section>

          <!-- মাঝের কলাম (Top Highlights) -->
          <section class="lg:col-span-3 bg-white dark:bg-[#1a1a1a] p-4 rounded-lg border border-gray-200 dark:border-gray-800 shadow-sm divide-y divide-gray-100 dark:divide-gray-800 flex flex-col justify-between">
            <h2 class="text-xs font-black text-red-600 tracking-wider uppercase pb-2 border-b border-gray-200 dark:border-gray-700">
              TOP HIGHLIGHTS
            </h2>
            \${center.map(item => \`
              <div class="py-3 group first:pt-3">
                <a href="\${item.link}" target="_blank" class="block">
                  <div class="overflow-hidden rounded aspect-video mb-2 bg-gray-100 dark:bg-gray-800">
                    <img src="\${item.image}" alt="\${item.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
                  </div>
                  <h3 class="font-bold text-gray-900 dark:text-gray-200 text-xs md:text-sm group-hover:text-red-600 transition leading-snug">
                    \${item.title}
                  </h3>
                  <span class="mt-1 block text-[10px] text-gray-400"><i class="fa-regular fa-clock mr-1"></i>\${item.time}</span>
                </a>
              </div>
            \`).join('')}
          </section>

          <!-- ডান কলাম (Trending) -->
          <aside class="lg:col-span-3 bg-white dark:bg-[#1a1a1a] p-4 rounded-lg border border-gray-200 dark:border-gray-800 shadow-sm">
            <div class="flex items-center space-x-2 pb-2 border-b border-gray-200 dark:border-gray-700 text-xs font-black text-gray-900 dark:text-white uppercase">
              <i class="fa-solid fa-arrow-trend-up text-red-600"></i>
              <span>TRENDING NOW</span>
            </div>
            <div class="divide-y divide-gray-100 dark:divide-gray-800">
              \${right.map((item, idx) => \`
                <article class="py-2.5 group">
                  <a href="\${item.link}" target="_blank" class="flex items-start gap-2.5">
                    <span class="text-lg font-black text-gray-300 dark:text-gray-600 group-hover:text-red-600 leading-none">0\${idx+1}</span>
                    <div>
                      <h4 class="font-bold text-gray-800 dark:text-gray-200 text-xs group-hover:text-red-600 transition leading-snug">
                        \${item.title}
                      </h4>
                      <span class="text-[10px] text-gray-400 mt-1 block">\${item.time}</span>
                    </div>
                  </a>
                </article>
              \`).join('')}
            </div>
          </aside>
        </div>
      \`;

      if (more.length > 0) {
        html += \`
          <section class="pt-6">
            <h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wider mb-4 border-l-4 border-red-600 pl-3">
              MORE REPORTS IN THIS SECTION
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              \${more.map(item => \`
                <div class="bg-white dark:bg-[#1a1a1a] p-3 rounded-lg border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col justify-between group">
                  <a href="\${item.link}" target="_blank">
                    <img src="\${item.image}" class="w-full aspect-[16/10] object-cover rounded mb-2">
                    <h4 class="text-xs font-bold text-gray-800 dark:text-gray-200 group-hover:text-red-600 leading-snug">\${item.title}</h4>
                  </a>
                  <span class="text-[10px] text-gray-400 mt-2 block">\${item.time}</span>
                </div>
              \`).join('')}
            </div>
          </section>
        \`;
      }

      document.getElementById('contentGrid').innerHTML = html;
    }

    function renderCustomList(list, title) {
      if (list.length === 0) {
        document.getElementById('contentGrid').innerHTML = '<div class="p-8 text-center text-gray-400">No matching headlines found.</div>';
        return;
      }
      let html = \`
        <div class="bg-white dark:bg-[#1a1a1a] p-4 rounded-lg border border-gray-200 dark:border-gray-800">
          <h2 class="text-sm font-black text-red-600 uppercase mb-4">\${title}</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            \${list.map(item => \`
              <div class="p-3 border border-gray-100 dark:border-gray-800 rounded group">
                <a href="\${item.link}" target="_blank">
                  <h4 class="text-xs font-bold text-gray-800 dark:text-gray-200 group-hover:text-red-600 mb-1">\${item.title}</h4>
                  <p class="text-[11px] text-gray-500">\${item.summary}</p>
                </a>
              </div>
            \`).join('')}
          </div>
        </div>
      \`;
      document.getElementById('contentGrid').innerHTML = html;
    }

    // লাইভ টিভি উইন্ডো
    function openLiveTv() {
      document.getElementById('tvModal').classList.remove('hidden');
    }
    function closeLiveTv() {
      document.getElementById('tvModal').classList.add('hidden');
    }

    // থিম টগল (Dark/Light)
    function toggleTheme() {
      const html = document.documentElement;
      const icon = document.getElementById('themeIcon');
      if (html.classList.contains('dark')) {
        html.classList.remove('dark');
        icon.className = 'fa-solid fa-moon';
      } else {
        html.classList.add('dark');
        icon.className = 'fa-solid fa-sun text-yellow-400';
      }
    }

    // ভাষা পরিবর্তন
    function switchLang(lang) {
      if (lang === 'bn') {
        document.getElementById('langBn').className = 'text-white font-bold';
        document.getElementById('langEn').className = 'text-gray-400 hover:text-white';
      } else {
        document.getElementById('langEn').className = 'text-white font-bold';
        document.getElementById('langBn').className = 'text-gray-400 hover:text-white';
      }
    }

    loadLiveData();
    setInterval(loadLiveData, 60000); // প্রতি ১ মিনিটে ফ্রন্টএন্ড ডেটা চেক
  </script>
</body>
</html>
  `);
});

app.listen(PORT, () => {
  console.log(`\n========================================================`);
  console.log(`[NDTV Fully-Active Suite Online] http://localhost:${PORT}`);
  console.log(`========================================================\n`);
});

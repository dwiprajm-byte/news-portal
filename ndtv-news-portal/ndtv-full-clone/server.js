const express = require('express');
const Parser = require('rss-parser');
const cron = require('node-cron');

const app = express();
const parser = new Parser();
const PORT = process.env.PORT || 3000;

let liveFeeds = {
  topStories: [],
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

const webStories = [
  { title: "Top 10 EVs Launching This Quarter", img: "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=400&q=80" },
  { title: "Smart Gadgets to Watch in 2026", img: "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=400&q=80" },
  { title: "Travel: Unexplored Himalayan Villages", img: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=400&q=80" },
  { title: "Quick Low-Carb Nutrition Hacks", img: "https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=400&q=80" }
];

const defaultThumbs = [
  "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=800&q=80"
];

function formatItems(items, categoryName) {
  return items.map((item, idx) => {
    let title = item.title || "Headline Update";
    let source = "News Desk";
    if (title.includes(" - ")) {
      const parts = title.split(" - ");
      source = parts.pop();
      title = parts.join(" - ");
    }
    return {
      id: `${categoryName}-${idx}`,
      title,
      source,
      link: item.link || "#",
      category: categoryName.toUpperCase(),
      time: new Date(item.pubDate || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      image: defaultThumbs[idx % defaultThumbs.length],
      summary: item.contentSnippet ? item.contentSnippet.replace(/<[^>]*>?/gm, '').slice(0, 140) + "..." : "Follow our live reporting for breaking developments on this story."
    };
  });
}

async function syncAllFeeds() {
  try {
    console.log('[Auto-Sync] Fetching Google News RSS...');
    const [topFeed, bizFeed, techFeed, sportsFeed] = await Promise.all([
      parser.parseURL('https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en'),
      parser.parseURL('https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en'),
      parser.parseURL('https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en'),
      parser.parseURL('https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en')
    ]);

    liveFeeds.topStories = formatItems(topFeed.items.slice(0, 15), "Top Story");
    liveFeeds.business = formatItems(bizFeed.items.slice(0, 8), "Business");
    liveFeeds.tech = formatItems(techFeed.items.slice(0, 8), "Tech");
    liveFeeds.sports = formatItems(sportsFeed.items.slice(0, 8), "Sports");
    console.log('[Auto-Sync Done] সমস্ত ক্যাটাগরি সফলভাবে আপডেট হয়েছে।');
  } catch (err) {
    console.error('[Sync Error]:', err.message);
  }
}

syncAllFeeds();
cron.schedule('*/15 * * * *', syncAllFeeds);

app.get('/', (req, res) => {
  const lead = liveFeeds.topStories[0] || {
    title: "Live satellite feeds syncing with the desk...",
    summary: "Please refresh in a moment.",
    time: "Just now",
    source: "Desk",
    category: "LIVE",
    image: defaultThumbs[0],
    link: "#"
  };

  const centerSubStories = liveFeeds.topStories.slice(1, 5);
  const rightTrending = liveFeeds.topStories.slice(5, 12);
  const tickerItems = liveFeeds.topStories.map(i => i.title).join("  &nbsp;•&nbsp;  ");

  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>24EarlyNews | NDTV Architecture Edition</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .animate-marquee { display: inline-block; white-space: nowrap; animation: marquee 40s linear infinite; }
    .animate-marquee:hover { animation-play-state: paused; }
  </style>
</head>
<body class="bg-[#f0f2f5] text-[#1e2022] font-sans antialiased">

  <!-- ১. মার্কেট ও ইউটিলিটি টপ স্ট্রিপ (NDTV Profit & Sensex Ticker) -->
  <div class="bg-[#1f2024] text-white text-[11px] py-1.5 px-4 border-b border-gray-700">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-6 overflow-x-auto whitespace-nowrap scrollbar-none">
        <span class="font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
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
        <span><i class="fa-solid fa-cloud-sun mr-1"></i> New Delhi 28°C</span>
        <span>•</span>
        <span class="text-red-400 font-bold"><i class="fa-solid fa-circle text-[8px] animate-pulse"></i> LIVE TV</span>
      </div>
    </div>
  </div>

  <!-- ২. নেটওয়ার্ক চ্যানেল বার (NDTV 24x7, NDTV India, Profit ইত্যাদি) -->
  <div class="bg-[#111317] text-gray-400 text-xs px-4 border-b border-gray-800">
    <div class="max-w-7xl mx-auto flex items-center justify-between py-1">
      <div class="flex space-x-5 font-semibold">
        <a href="#" class="text-white border-b-2 border-red-600 pb-1">NDTV CLONE</a>
        <a href="#" class="hover:text-white transition">INDIA</a>
        <a href="#" class="hover:text-white transition">PROFIT</a>
        <a href="#" class="hover:text-white transition">CRICKET</a>
        <a href="#" class="hover:text-white transition">TECH</a>
        <a href="#" class="hover:text-white transition">MOVIES</a>
      </div>
      <div class="text-[11px] hidden sm:block">
        <span class="text-gray-400">LANGUAGE:</span> <span class="text-white font-bold cursor-pointer">ENGLISH | हिन्दी</span>
      </div>
    </div>
  </div>

  <!-- ৩. মেইন হেডার ও লোগো -->
  <header class="bg-white sticky top-0 z-50 shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
      <div class="flex items-center space-x-6">
        <a href="/" class="text-3xl font-black tracking-tighter text-red-600 flex items-center">
          24<span class="text-slate-900">EARLYNEWS</span>
        </a>
      </div>

      <nav class="hidden lg:flex space-x-6 text-[13px] font-extrabold text-gray-800">
        <a href="#" class="hover:text-red-600 transition">LATEST</a>
        <a href="#" class="hover:text-red-600 transition">INDIA</a>
        <a href="#" class="hover:text-red-600 transition">OPINION</a>
        <a href="#" class="hover:text-red-600 transition">BUSINESS</a>
        <a href="#" class="hover:text-red-600 transition">WORLD</a>
        <a href="#" class="hover:text-red-600 transition">CITIES</a>
        <a href="#" class="hover:text-red-600 transition">TECH</a>
        <a href="#" class="hover:text-red-600 transition">SPORTS</a>
      </nav>

      <div class="flex items-center space-x-3">
        <button class="bg-red-600 hover:bg-red-700 text-white text-xs font-black px-3 py-1.5 rounded flex items-center gap-1.5 shadow-sm">
          <i class="fa-solid fa-play text-[10px]"></i> WATCH LIVE
        </button>
      </div>
    </div>

    <!-- ৪. ব্রেকিং নিউজ টিকার (Marquee) -->
    <div class="bg-[#d90429] text-white text-xs py-1.5 px-4 flex items-center">
      <div class="max-w-7xl mx-auto w-full flex items-center">
        <span class="bg-black text-white font-black px-2 py-0.5 rounded text-[10px] tracking-widest uppercase mr-3 shrink-0 flex items-center gap-1">
          <i class="fa-solid fa-bolt text-yellow-400"></i> BREAKING
        </span>
        <div class="overflow-hidden relative w-full whitespace-nowrap">
          <div class="animate-marquee font-semibold text-white">
            ${tickerItems || "Loading live satellite feeds..."}
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- ৫. লাইভ স্পোর্টস স্কোরবোর্ড স্ট্রিপ -->
  <div class="max-w-7xl mx-auto px-4 mt-3">
    <div class="bg-white border border-gray-200 rounded p-2.5 flex items-center justify-between text-xs shadow-sm">
      <div class="flex items-center space-x-3">
        <span class="bg-blue-600 text-white font-bold px-2 py-0.5 rounded text-[10px]">CRICKET</span>
        <span class="font-bold">Match 32: India vs Australia</span>
        <span class="text-gray-500">IND 284/6 (50) • AUS 142/3 (26.2)</span>
        <span class="text-red-600 font-bold">Live</span>
      </div>
      <a href="#" class="text-blue-600 hover:underline font-bold hidden sm:inline">Scorecard & Highlights &rarr;</a>
    </div>
  </div>

  <!-- ৬. মূল কন্টেন্ট গ্রিড (NDTV 3-কলাম আর্কিটেকচার) -->
  <main class="max-w-7xl mx-auto px-4 py-5 space-y-8">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
      
      <!-- বাম কলাম (Col 6): লিড স্টোরি ও হাইলাইটস -->
      <section class="lg:col-span-6 bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between">
        <div>
          <a href="${lead.link}" target="_blank" class="block group">
            <div class="relative overflow-hidden rounded bg-black aspect-video mb-3">
              <img src="${lead.image}" alt="${lead.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500 opacity-95">
              <span class="absolute top-3 left-3 bg-red-600 text-white text-[10px] font-black uppercase px-2 py-0.5 rounded">
                ${lead.category}
              </span>
            </div>
            <h1 class="text-2xl md:text-3xl font-black text-gray-900 group-hover:text-red-600 transition leading-tight">
              ${lead.title}
            </h1>
            <p class="mt-2 text-gray-600 text-sm leading-relaxed">
              ${lead.summary}
            </p>
          </a>
          <!-- NDTV স্টাইল কী-পয়েন্টস -->
          <div class="mt-4 pt-3 border-t border-gray-100 space-y-2">
            <p class="text-xs font-bold text-gray-700 uppercase">Key Developments:</p>
            <ul class="text-xs text-gray-600 space-y-1.5 list-disc pl-4">
              <li>High-level meetings convened in New Delhi regarding emergency measures.</li>
              <li>Financial market response remains resilient despite global headwinds.</li>
              <li>Official press briefing scheduled for late evening.</li>
            </ul>
          </div>
        </div>
        <div class="mt-4 flex items-center justify-between text-xs text-gray-400 pt-3 border-t border-gray-100">
          <span><i class="fa-regular fa-clock mr-1"></i> ${lead.time}</span>
          <span class="font-bold text-red-600">${lead.source}</span>
        </div>
      </section>

      <!-- মাঝের কলাম (Col 3): Don't Miss / সাব-স্টোরিজ -->
      <section class="lg:col-span-3 bg-white p-4 rounded-lg border border-gray-200 shadow-sm divide-y divide-gray-100 flex flex-col justify-between">
        <h2 class="text-xs font-black text-red-600 tracking-wider uppercase pb-2 border-b border-gray-200">
          TOP STORIES & UPDATES
        </h2>
        ${centerSubStories.map(item => `
          <div class="py-3 group first:pt-3">
            <a href="${item.link}" target="_blank" class="block">
              <div class="overflow-hidden rounded aspect-video mb-2 bg-gray-100">
                <img src="${item.image}" alt="${item.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
              </div>
              <h3 class="font-bold text-gray-900 text-xs md:text-sm group-hover:text-red-600 transition leading-snug">
                ${item.title}
              </h3>
              <span class="mt-1 block text-[10px] text-gray-400"><i class="fa-regular fa-clock mr-1"></i>${item.time}</span>
            </a>
          </div>
        `).join('')}
      </section>

      <!-- ডান কলাম (Col 3): ট্রেন্ডিং ও মতামত -->
      <aside class="lg:col-span-3 bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center space-x-2 pb-2 border-b border-gray-200 text-xs font-black text-gray-900 uppercase">
            <i class="fa-solid fa-arrow-trend-up text-red-600"></i>
            <span>TRENDING NOW</span>
          </div>
          <div class="divide-y divide-gray-100">
            ${rightTrending.map((item, idx) => `
              <article class="py-2.5 group">
                <a href="${item.link}" target="_blank" class="flex items-start gap-2.5">
                  <span class="text-lg font-black text-gray-300 group-hover:text-red-600 leading-none">0${idx+1}</span>
                  <div>
                    <h4 class="font-bold text-gray-800 text-xs group-hover:text-red-600 transition leading-snug">
                      ${item.title}
                    </h4>
                    <span class="text-[10px] text-gray-400 mt-1 block">${item.time}</span>
                  </div>
                </a>
              </article>
            `).join('')}
          </div>
        </div>
      </aside>
    </div>

    <!-- ৭. NDTV স্টাইল ওয়েব স্টোরিজ (Web Stories Carousel) -->
    <section class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
      <div class="flex items-center justify-between mb-4 border-b border-gray-100 pb-2">
        <h3 class="text-sm font-black text-gray-900 uppercase tracking-wide flex items-center gap-2">
          <i class="fa-solid fa-bolt-lightning text-yellow-500"></i> WEB STORIES
        </h3>
        <span class="text-xs text-red-600 font-bold hover:underline cursor-pointer">View All &rarr;</span>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        ${webStories.map(ws => `
          <div class="relative rounded-lg overflow-hidden aspect-[9/16] group cursor-pointer shadow">
            <img src="${ws.img}" alt="${ws.title}" class="w-full h-full object-cover group-hover:scale-110 transition duration-500">
            <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent flex items-end p-3">
              <p class="text-white text-xs font-bold leading-tight group-hover:underline">
                ${ws.title}
              </p>
            </div>
          </div>
        `).join('')}
      </div>
    </section>

    <!-- ৮. বিজনেস ও টেকনোলজি ক্যাটাগরি ব্লক -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- বিজনেস ব্লক -->
      <section class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <div class="flex items-center justify-between border-b-2 border-red-600 pb-2 mb-4">
          <h3 class="font-black text-gray-900 text-sm uppercase">PROFIT & BUSINESS</h3>
          <span class="text-xs text-red-600 font-bold hover:underline">More &rarr;</span>
        </div>
        <div class="space-y-3">
          ${liveFeeds.business.slice(0, 4).map(b => `
            <a href="${b.link}" target="_blank" class="flex gap-3 group">
              <img src="${b.image}" class="w-20 h-16 object-cover rounded shrink-0">
              <div>
                <h4 class="font-bold text-xs text-gray-800 group-hover:text-red-600 leading-snug">${b.title}</h4>
                <span class="text-[10px] text-gray-400">${b.time}</span>
              </div>
            </a>
          `).join('')}
        </div>
      </section>

      <!-- টেকনোলজি ব্লক -->
      <section class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <div class="flex items-center justify-between border-b-2 border-blue-600 pb-2 mb-4">
          <h3 class="font-black text-gray-900 text-sm uppercase">TECH & GADGETS</h3>
          <span class="text-xs text-blue-600 font-bold hover:underline">More &rarr;</span>
        </div>
        <div class="space-y-3">
          ${liveFeeds.tech.slice(0, 4).map(t => `
            <a href="${t.link}" target="_blank" class="flex gap-3 group">
              <img src="${t.image}" class="w-20 h-16 object-cover rounded shrink-0">
              <div>
                <h4 class="font-bold text-xs text-gray-800 group-hover:text-blue-600 leading-snug">${t.title}</h4>
                <span class="text-[10px] text-gray-400">${t.time}</span>
              </div>
            </a>
          `).join('')}
        </div>
      </section>
    </div>

  </main>

  <!-- ৯. সম্পূর্ণ ফুটার ও সাইটম্যাপ (NDTV Structure) -->
  <footer class="bg-[#111317] text-gray-400 text-xs mt-12 border-t border-gray-800 pt-8 pb-12">
    <div class="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 mb-8 border-b border-gray-800 pb-8">
      <div>
        <h5 class="text-white font-bold mb-3 uppercase tracking-wider">NEWS CHANNELS</h5>
        <ul class="space-y-1.5">
          <li><a href="#" class="hover:text-white">NDTV 24x7</a></li>
          <li><a href="#" class="hover:text-white">NDTV India</a></li>
          <li><a href="#" class="hover:text-white">NDTV Profit</a></li>
          <li><a href="#" class="hover:text-white">NDTV MP-CG</a></li>
        </ul>
      </div>
      <div>
        <h5 class="text-white font-bold mb-3 uppercase tracking-wider">SPECIAL COVERAGE</h5>
        <ul class="space-y-1.5">
          <li><a href="#" class="hover:text-white">Cricket Live Scores</a></li>
          <li><a href="#" class="hover:text-white">Stock Markets</a></li>
          <li><a href="#" class="hover:text-white">Auto Expo</a></li>
          <li><a href="#" class="hover:text-white">Elections 2026</a></li>
        </ul>
      </div>
      <div>
        <h5 class="text-white font-bold mb-3 uppercase tracking-wider">TRENDING TOPICS</h5>
        <ul class="space-y-1.5">
          <li><a href="#" class="hover:text-white">Electric Vehicles</a></li>
          <li><a href="#" class="hover:text-white">AI Tools & Tech</a></li>
          <li><a href="#" class="hover:text-white">Health & Wellness</a></li>
          <li><a href="#" class="hover:text-white">World Affairs</a></li>
        </ul>
      </div>
      <div>
        <h5 class="text-white font-bold mb-3 uppercase tracking-wider">CONNECT WITH US</h5>
        <div class="flex space-x-3 text-base text-gray-300 mb-3">
          <i class="fa-brands fa-facebook hover:text-white cursor-pointer"></i>
          <i class="fa-brands fa-x-twitter hover:text-white cursor-pointer"></i>
          <i class="fa-brands fa-youtube hover:text-white cursor-pointer"></i>
          <i class="fa-brands fa-instagram hover:text-white cursor-pointer"></i>
        </div>
        <p class="text-[11px] text-gray-500">Download Official App on Android & iOS.</p>
      </div>
    </div>
    <div class="max-w-7xl mx-auto px-4 text-center text-[11px] text-gray-500">
      <p>&copy; 2026 24EARLYNEWS - FULL NDTV ARCHITECTURE SUITE. ALL RIGHTS RESERVED.</p>
    </div>
  </footer>

  <script>
    setTimeout(() => { window.location.reload(); }, 5 * 60 * 1000);
  </script>
</body>
</html>
  `);
});

app.listen(PORT, () => {
  console.log(`\n======================================================`);
  console.log(`[NDTV Clone Live] http://localhost:${PORT}`);
  console.log(`======================================================\n`);
});

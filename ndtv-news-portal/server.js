const express = require('express');
const Parser = require('rss-parser');
const cron = require('node-cron');

const app = express();
const parser = new Parser();
const PORT = process.env.PORT || 3000;

let newsDatabase = [];

const fallbackImages = [
  "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=800&q=80"
];

async function fetchAutomatedNews() {
  try {
    console.log('[অটোমেশন] নতুন খবর ফেচ করা হচ্ছে...');
    const feed = await parser.parseURL('https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en');
    
    if (feed && feed.items) {
      newsDatabase = feed.items.slice(0, 20).map((item, index) => {
        let cleanTitle = item.title || "Latest Headline Update";
        let source = "News Desk";
        if (cleanTitle.includes(" - ")) {
          const parts = cleanTitle.split(" - ");
          source = parts.pop();
          cleanTitle = parts.join(" - ");
        }

        return {
          id: index + 1,
          title: cleanTitle,
          summary: item.contentSnippet ? item.contentSnippet.replace(/<[^>]*>?/gm, '').slice(0, 150) + "..." : "Click to read full details regarding this developing news story.",
          link: item.link,
          source: source,
          category: index === 0 ? "TOP STORY" : (index % 2 === 0 ? "NATIONAL" : "BUSINESS"),
          time: new Date(item.pubDate || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          image: fallbackImages[index % fallbackImages.length]
        };
      });
      console.log(`[অটোমেশন সম্পন্ন] মোট ${newsDatabase.length} টি তাজা খবর আপডেট হয়েছে।`);
    }
  } catch (error) {
    console.error('[অটোমেশন এরর]:', error.message);
  }
}

fetchAutomatedNews();

cron.schedule('*/15 * * * *', () => {
  fetchAutomatedNews();
});

app.get('/api/news', (req, res) => {
  res.json(newsDatabase);
});

app.get('/', (req, res) => {
  const lead = newsDatabase[0] || {
    title: "Connecting to live news feeds...",
    summary: "Please refresh in a moment.",
    time: "Just now",
    category: "BREAKING",
    image: fallbackImages[0],
    link: "#"
  };

  const trending = newsDatabase.slice(1, 6);
  const gridNews = newsDatabase.slice(6, 18);
  const tickerItems = newsDatabase.slice(0, 8).map(n => n.title).join("  &nbsp;•&nbsp;  ");

  res.send(`
<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Live Breaking News Portal</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .animate-marquee { display: inline-block; white-space: nowrap; animation: marquee 35s linear infinite; }
    .animate-marquee:hover { animation-play-state: paused; }
  </style>
</head>
<body class="bg-[#f4f5f7] text-[#222] font-sans antialiased">

  <header class="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
      <div class="flex items-center space-x-6">
        <a href="/" class="text-3xl font-black tracking-tighter text-red-600 flex items-center gap-1">
          DAILY<span class="text-slate-900">BULLETIN</span>
        </a>
        <nav class="hidden md:flex space-x-6 text-sm font-bold text-gray-700">
          <a href="#" class="hover:text-red-600 transition">HOME</a>
          <a href="#" class="hover:text-red-600 transition">INDIA</a>
          <a href="#" class="hover:text-red-600 transition">WORLD</a>
          <a href="#" class="hover:text-red-600 transition">BUSINESS</a>
          <a href="#" class="hover:text-red-600 transition">TECH</a>
          <a href="#" class="hover:text-red-600 transition">SPORTS</a>
        </nav>
      </div>

      <div class="flex items-center space-x-3 text-xs font-semibold">
        <span class="flex items-center text-green-600 bg-green-50 px-2 py-1 rounded border border-green-200">
          <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse mr-1.5"></span> LIVE AUTO-FEED
        </span>
      </div>
    </div>

    <div class="bg-[#111] text-white text-xs py-2 px-4 flex items-center overflow-hidden border-t border-red-700">
      <div class="max-w-7xl mx-auto w-full flex items-center">
        <span class="bg-red-600 text-white font-extrabold px-2.5 py-0.5 rounded text-[10px] tracking-wider shrink-0 flex items-center gap-1 uppercase mr-3">
          <i class="fa-solid fa-bolt"></i> BREAKING
        </span>
        <div class="overflow-hidden relative w-full whitespace-nowrap">
          <div class="animate-marquee text-gray-200 font-medium">
            ${tickerItems || "Fetching latest live automated feeds..."}
          </div>
        </div>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 py-6">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 pb-8 border-b border-gray-300">
      
      <section class="lg:col-span-8 group">
        <a href="${lead.link}" target="_blank" class="block">
          <div class="relative overflow-hidden rounded-lg bg-black aspect-video mb-3 shadow">
            <img src="${lead.image}" alt="${lead.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500 opacity-95">
            <span class="absolute top-3 left-3 bg-red-600 text-white text-[11px] font-black uppercase px-2.5 py-1 rounded tracking-wider shadow">
              ${lead.category}
            </span>
          </div>
          <h1 class="text-2xl md:text-4xl font-extrabold text-gray-900 group-hover:text-red-600 transition leading-tight mt-2">
            ${lead.title}
          </h1>
          <p class="mt-2 text-gray-600 text-sm md:text-base leading-relaxed">
            ${lead.summary}
          </p>
          <div class="mt-3 flex items-center text-xs text-gray-400 space-x-3">
            <span><i class="fa-regular fa-clock mr-1"></i> ${lead.time}</span>
            <span>•</span>
            <span class="text-red-600 font-bold">${lead.source}</span>
          </div>
        </a>
      </section>

      <aside class="lg:col-span-4 flex flex-col justify-between divide-y divide-gray-200 bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div class="flex items-center space-x-2 pb-3 font-extrabold text-gray-900 border-b border-gray-200 uppercase tracking-wider text-sm">
          <i class="fa-solid fa-arrow-trend-up text-red-600"></i>
          <span>TRENDING HEADLINES</span>
        </div>

        ${trending.map(item => `
          <article class="py-3 group">
            <a href="${item.link}" target="_blank" class="block">
              <span class="text-[10px] font-extrabold text-red-600 tracking-wider uppercase">${item.source}</span>
              <h3 class="mt-1 font-bold text-gray-900 text-sm md:text-base group-hover:text-red-600 transition leading-snug">
                ${item.title}
              </h3>
              <span class="mt-1 block text-[11px] text-gray-400"><i class="fa-regular fa-clock mr-1"></i>${item.time}</span>
            </a>
          </article>
        `).join('')}
      </aside>
    </div>

    <section class="pt-8">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-black text-gray-900 border-l-4 border-red-600 pl-3 uppercase tracking-wide">
          Latest Reports & Updates
        </h2>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        ${gridNews.map(item => `
          <div class="bg-white p-3 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between group hover:shadow-md transition">
            <a href="${item.link}" target="_blank" class="block">
              <div class="overflow-hidden rounded aspect-[16/10] mb-2 bg-gray-100">
                <img src="${item.image}" alt="${item.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
              </div>
              <span class="text-[10px] font-bold text-red-600 uppercase tracking-wider block">${item.source}</span>
              <h4 class="mt-1 font-bold text-gray-900 text-sm group-hover:text-red-600 transition leading-snug">
                ${item.title}
              </h4>
            </a>
            <div class="mt-3 pt-2 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-400">
              <span><i class="fa-regular fa-clock mr-1"></i>${item.time}</span>
              <a href="${item.link}" target="_blank" class="text-red-600 hover:underline font-bold">Read &rarr;</a>
            </div>
          </div>
        `).join('')}
      </div>
    </section>
  </main>

  <footer class="bg-[#111] text-gray-400 text-xs py-8 mt-12 border-t border-gray-800">
    <div class="max-w-7xl mx-auto px-4 text-center space-y-2">
      <p class="font-bold text-white text-sm">DAILYBULLETIN &copy; 2026. All Rights Reserved.</p>
      <p>Automated Real-Time News Delivery Engine.</p>
    </div>
  </footer>
</body>
</html>
  `);
});

app.listen(PORT, () => {
  console.log(`\n==================================================`);
  console.log(`[ওয়েবসাইট রানিং] http://localhost:${PORT}`);
  console.log(`==================================================\n`);
});

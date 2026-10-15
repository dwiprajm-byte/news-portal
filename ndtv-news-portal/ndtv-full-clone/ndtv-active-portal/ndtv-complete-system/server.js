const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const cron = require('node-cron');

const app = express();
const PORT = process.env.PORT || 3000;

// গ্লোবাল ডাটা স্টোর
let portalData = {
  breaking: [],
  leadStory: null,
  subStories: [],
  trending: [],
  india: [],
  business: [],
  tech: [],
  entertainment: [],
  opinion: [
    { author: "Sunil Prabhu", role: "Senior Editor", title: "Decoding the 2026 Fiscal Reform Trajectory", img: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80" },
    { author: "Mariam Alvi", role: "Foreign Affairs Analyst", title: "Navigating Middle East Energy Security & Maritime Pacts", img: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80" },
    { author: "Devashish Ray", role: "Tech & Markets", title: "Enterprise AI Infrastructure: Where Is India Standing?", img: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80" }
  ],
  webStories: [
    { title: "Top 7 EVs Launching with 600km+ Range", img: "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=400&q=80" },
    { title: "Inside World's Longest High-Speed Rail Corridor", img: "https://images.unsplash.com/photo-1474487548417-781cb71495f3?auto=format&fit=crop&w=400&q=80" },
    { title: "Smart Gadgets Transforming Smart Living", img: "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=400&q=80" },
    { title: "Dietary Changes That Boost Longevity & Focus", img: "https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=400&q=80" }
  ]
};

const stockTicker = [
  { name: "SENSEX", val: "81,420.15", change: "+420.30", up: true },
  { name: "NIFTY 50", val: "24,890.60", change: "+125.40", up: true },
  { name: "GOLD (10g)", val: "₹76,450", change: "-110.00", up: false },
  { name: "USD/INR", val: "83.92", change: "+0.04", up: true },
  { name: "BRENT CRUDE", val: "$77.10/bbl", change: "-0.85", up: false }
];

const fallbackThumbnails = [
  "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=800&q=80"
];

async function syncFeedByTopic(url) {
  try {
    const res = await axios.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    const $ = cheerio.load(res.data, { xmlMode: true });
    let items = [];
    $('item').each((i, el) => {
      let rawTitle = $(el).find('title').text();
      let link = $(el).find('link').text();
      let pubDate = $(el).find('pubDate').text();
      let desc = $(el).find('description').text();

      let source = "NDTV News Desk";
      if (rawTitle.includes(" - ")) {
        const parts = rawTitle.split(" - ");
        source = parts.pop();
        rawTitle = parts.join(" - ");
      }
      const $desc = cheerio.load(desc);
      let img = $desc('img').attr('src') || fallbackThumbnails[i % fallbackThumbnails.length];

      items.push({
        id: i,
        title: rawTitle,
        link: link || "#",
        source: source,
        time: pubDate ? new Date(pubDate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Just now",
        image: img,
        snippet: $desc.text().replace(/<[^>]*>?/gm, '').slice(0, 150) + "..."
      });
    });
    return items;
  } catch (e) {
    return [];
  }
}

async function scrapeFullPortal() {
  console.log('[Auto-Sync] লাইভ নিউজ ও সমস্ত ক্যাটাগরি রিফ্রেশ হচ্ছে...');
  try {
    const [top, biz, tech, ent] = await Promise.all([
      syncFeedByTopic('https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en'),
      syncFeedByTopic('https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en'),
      syncFeedByTopic('https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en'),
      syncFeedByTopic('https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-IN&gl=IN&ceid=IN:en')
    ]);

    if (top.length > 0) {
      portalData.breaking = top.slice(0, 10).map(i => i.title);
      portalData.leadStory = top[0];
      portalData.subStories = top.slice(1, 5);
      portalData.trending = top.slice(5, 15);
      portalData.india = top.slice(15, 21);
    }
    portalData.business = biz.slice(0, 6);
    portalData.tech = tech.slice(0, 6);
    portalData.entertainment = ent.slice(0, 6);
    console.log('[Auto-Sync Done] সমস্ত ডেটা হালনাগাদ সম্পন্ন।');
  } catch (err) {
    console.error('[Sync Error]:', err.message);
  }
}

scrapeFullPortal();
cron.schedule('*/10 * * * *', scrapeFullPortal);

app.get('/api/live', (req, res) => res.json(portalData));

app.get('/', (req, res) => {
  const lead = portalData.leadStory || {
    title: "Syncing Live Satellite Feeds...",
    snippet: "Real-time updates arriving from newsroom.",
    image: fallbackThumbnails[0],
    source: "NDTV Network",
    time: "Live",
    link: "#"
  };

  const tickerText = portalData.breaking.join(" &nbsp;&bull;&nbsp; ");

  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NDTV: Latest News, India News, Breaking News, Live TV</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: { extend: {} }
    }
  </script>
  <style>
    body { font-family: 'Roboto', sans-serif; }
    .headline-font { font-family: 'Roboto Condensed', sans-serif; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .animate-marquee { display: inline-block; white-space: nowrap; animation: marquee 35s linear infinite; }
    .animate-marquee:hover { animation-play-state: paused; }
    .custom-scroll::-webkit-scrollbar { height: 4px; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #555; }
  </style>
</head>
<body class="bg-[#f6f6f6] dark:bg-[#0f1115] text-[#111] dark:text-gray-100 transition-colors">

  <!-- ১. ইউটিলিটি ও স্টক মার্কেট বার -->
  <div class="bg-[#121820] text-[#a9b2be] text-[11px] font-medium border-b border-gray-800">
    <div class="max-w-[1240px] mx-auto px-3 flex items-center justify-between py-1.5">
      <div class="flex items-center space-x-5 overflow-x-auto whitespace-nowrap custom-scroll">
        <span class="text-white font-bold tracking-wider flex items-center gap-1">
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
      <div class="hidden md:flex items-center space-x-4 text-[10px] shrink-0">
        <span><i class="fa-solid fa-cloud-sun text-yellow-400 mr-1"></i> New Delhi 28°C</span>
        <span>•</span>
        <button onclick="toggleDarkMode()" class="hover:text-white font-bold flex items-center gap-1">
          <i id="themeIcon" class="fa-solid fa-moon"></i> THEME
        </button>
        <span>•</span>
        <button onclick="switchLang()" id="langBtn" class="hover:text-white font-bold">বাংলা</button>
      </div>
    </div>
  </div>

  <!-- ২. নেটওয়ার্ক চ্যানেল ট্যাব স্ট্রিপ -->
  <div class="bg-[#0a0d12] text-gray-400 text-xs px-3 border-b border-gray-800">
    <div class="max-w-[1240px] mx-auto flex items-center justify-between py-1.5">
      <div class="flex space-x-5 font-semibold overflow-x-auto whitespace-nowrap text-[12px]">
        <a href="/" class="text-white border-b-2 border-[#e21b22] pb-0.5">NDTV</a>
        <a href="#india" class="hover:text-white transition">NDTV INDIA</a>
        <a href="#business" class="hover:text-white transition">PROFIT</a>
        <a href="#sports" class="hover:text-white transition">CRICKET</a>
        <a href="#tech" class="hover:text-white transition">GADGETS 360</a>
        <a href="#movies" class="hover:text-white transition">MOVIES</a>
        <a href="#webstories" class="hover:text-white transition">WEB STORIES</a>
        <a href="#opinion" class="hover:text-white transition">OPINION</a>
      </div>
      <div class="text-[11px] hidden lg:block text-gray-400">
        <span>EPAPER | NEWSLETTER | PODCASTS</span>
      </div>
    </div>
  </div>

  <!-- ৩. অফিশিয়াল হেডার, মেগা-মেনু টগল ও সার্চ -->
  <header class="bg-white dark:bg-[#181a20] border-b border-gray-300 dark:border-gray-800 shadow-sm sticky top-0 z-40">
    <div class="max-w-[1240px] mx-auto px-3 py-2 flex items-center justify-between gap-4">
      <div class="flex items-center space-x-4">
        <!-- মেগা-মেনু বাটন -->
        <button onclick="toggleDrawer()" class="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded text-gray-700 dark:text-gray-200">
          <i class="fa-solid fa-bars text-xl"></i>
        </button>
        <!-- NDTV আইকনিক রেড বক্স লোগো -->
        <a href="/" class="flex items-center">
          <div class="bg-[#e21b22] text-white font-black text-2xl tracking-tighter px-2.5 py-0.5 select-none">
            ndtv
          </div>
        </a>
      </div>

      <!-- ন্যাভিগেশন লিংকসমূহ -->
      <nav class="hidden lg:flex space-x-5 text-[13px] font-extrabold text-gray-800 dark:text-gray-200">
        <a href="#live" onclick="openLiveVideo()" class="text-[#e21b22] flex items-center gap-1"><i class="fa-solid fa-circle text-[7px] animate-pulse"></i> LIVE TV</a>
        <a href="#latest" class="hover:text-[#e21b22]">LATEST</a>
        <a href="#india" class="hover:text-[#e21b22]">INDIA</a>
        <a href="#business" class="hover:text-[#e21b22]">BUSINESS</a>
        <a href="#world" class="hover:text-[#e21b22]">WORLD</a>
        <a href="#tech" class="hover:text-[#e21b22]">TECH</a>
        <a href="#sports" class="hover:text-[#e21b22]">SPORTS</a>
        <a href="#movies" class="hover:text-[#e21b22]">SHOWBIZ</a>
      </nav>

      <!-- লাইভ সার্চ ও ওয়াচ লাইভ বাটন -->
      <div class="flex items-center space-x-3">
        <div class="relative hidden sm:block w-48 md:w-56">
          <input 
            type="text" 
            id="searchInput" 
            onkeyup="searchStories(this.value)"
            placeholder="Search news..." 
            class="w-full text-xs bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-full pl-7 pr-3 py-1 focus:outline-none focus:border-[#e21b22] dark:text-white"
          />
          <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-2 text-gray-400 text-xs"></i>
        </div>
        <button onclick="openLiveVideo()" class="bg-[#e21b22] hover:bg-red-700 text-white font-bold text-xs px-3 py-1.5 rounded flex items-center gap-1.5 shadow">
          <i class="fa-solid fa-play text-[10px]"></i> WATCH LIVE
        </button>
      </div>
    </div>

    <!-- ৪. ব্রেকিং নিউজ রেড টিকার স্ট্রিপ -->
    <div class="bg-[#e21b22] text-white text-[12px] flex items-center">
      <div class="max-w-[1240px] mx-auto px-3 w-full flex items-center py-1">
        <div class="bg-black text-white font-black text-[10px] px-2 py-0.5 uppercase tracking-wider shrink-0 mr-3 flex items-center gap-1">
          <i class="fa-solid fa-bolt text-yellow-400"></i> BREAKING
        </div>
        <div class="overflow-hidden relative w-full whitespace-nowrap">
          <div class="animate-marquee font-medium">
            ${tickerText || "Loading real-time news desk feeds..."}
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- ৫. লাইভ ক্রিকেট স্কোরবোর্ড স্ট্রিপ -->
  <div id="sports" class="max-w-[1240px] mx-auto px-3 mt-3">
    <div class="bg-white dark:bg-[#181a20] border border-gray-300 dark:border-gray-800 rounded p-2.5 flex items-center justify-between text-xs shadow-sm">
      <div class="flex items-center space-x-3">
        <span class="bg-[#003874] text-white font-black px-2 py-0.5 rounded text-[10px] tracking-wide">CRICKET LIVE</span>
        <span class="font-bold">Border-Gavaskar Trophy • 2nd Test</span>
        <span class="text-gray-500 dark:text-gray-400">IND 312/8 (82.4) • Day 2</span>
        <span class="text-[#e21b22] font-bold animate-pulse">In Progress</span>
      </div>
      <a href="#" class="text-blue-600 dark:text-blue-400 font-bold hover:underline hidden sm:inline">Ball-by-Ball Commentary &rarr;</a>
    </div>
  </div>

  <!-- ৬. প্রধান ৩-কলাম হোমপেজ গ্রিড (NDTV Architecture) -->
  <main class="max-w-[1240px] mx-auto px-3 py-4 space-y-8">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5" id="mainGridContainer">
      
      <!-- [কলাম ১-৬] লিড স্টোরি ও হাইলাইটস -->
      <section class="lg:col-span-6 bg-white dark:bg-[#181a20] p-4 border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col justify-between">
        <article>
          <a href="${lead.link}" target="_blank" class="block group">
            <h1 class="headline-font text-2xl sm:text-3xl font-bold text-[#111] dark:text-white group-hover:text-[#e21b22] leading-tight mb-3">
              ${lead.title}
            </h1>
            <div class="relative overflow-hidden aspect-video bg-gray-100 dark:bg-gray-800 mb-3 rounded">
              <img src="${lead.image}" alt="${lead.title}" class="w-full h-full object-cover">
              <span class="absolute top-2 left-2 bg-[#e21b22] text-white text-[10px] font-bold uppercase px-2 py-0.5">
                LEAD STORY
              </span>
            </div>
            <p class="text-xs text-gray-600 dark:text-gray-300 leading-relaxed mb-3">
              ${lead.snippet}
            </p>
          </a>
          <!-- NDTV কী-পয়েন্টস -->
          <div class="pt-3 border-t border-gray-100 dark:border-gray-800">
            <p class="text-[11px] font-black text-gray-700 dark:text-gray-300 uppercase mb-2">Key Developments:</p>
            <ul class="text-xs text-gray-600 dark:text-gray-400 space-y-1.5 list-disc pl-4">
              <li>Senior ministers assemble for emergency review in New Delhi.</li>
              <li>Markets sustain gains following international trade updates.</li>
              <li>Official press briefing scheduled for later this evening.</li>
            </ul>
          </div>
        </article>
        <div class="flex items-center justify-between text-[11px] text-gray-400 pt-3 border-t border-gray-100 dark:border-gray-800 mt-4">
          <span class="font-bold text-[#e21b22]">${lead.source}</span>
          <span><i class="fa-regular fa-clock mr-1"></i> ${lead.time}</span>
        </div>
      </section>

      <!-- [কলাম ৭-৯] Don't Miss / সাব-স্টোরিজ -->
      <section class="lg:col-span-3 bg-white dark:bg-[#181a20] p-4 border border-gray-200 dark:border-gray-800 shadow-sm divide-y divide-gray-100 dark:divide-gray-800 flex flex-col justify-between">
        <h2 class="headline-font text-xs font-black text-[#e21b22] tracking-wider uppercase pb-2 border-b border-gray-200 dark:border-gray-700">
          TOP STORIES
        </h2>
        ${portalData.subStories.map(item => `
          <article class="py-3 group first:pt-2">
            <a href="${item.link}" target="_blank" class="block">
              <div class="aspect-video bg-gray-100 dark:bg-gray-800 overflow-hidden mb-2 rounded">
                <img src="${item.image}" class="w-full h-full object-cover group-hover:scale-105 transition">
              </div>
              <h3 class="text-xs md:text-[13px] font-bold text-gray-900 dark:text-gray-200 group-hover:text-[#e21b22] leading-snug">
                ${item.title}
              </h3>
              <span class="text-[10px] text-gray-400 mt-1 block">${item.time}</span>
            </a>
          </article>
        `).join('')}
      </section>

      <!-- [কলাম ১০-১২] NDTV ট্রেন্ডিং র‍্যাঙ্কিং লিস্ট (১-১০) -->
      <aside class="lg:col-span-3 bg-white dark:bg-[#181a20] p-4 border border-gray-200 dark:border-gray-800 shadow-sm">
        <div class="flex items-center justify-between border-b-2 border-[#e21b22] pb-1.5 mb-3">
          <h2 class="headline-font text-xs font-black text-gray-900 dark:text-white uppercase tracking-wide">
            TRENDING NOW
          </h2>
          <span class="text-[9px] bg-red-100 text-red-600 font-bold px-1.5 py-0.5 rounded">LIVE</span>
        </div>
        <div class="divide-y divide-gray-100 dark:divide-gray-800">
          ${portalData.trending.map((item, idx) => `
            <article class="py-2 group">
              <a href="${item.link}" target="_blank" class="flex items-start gap-2.5">
                <span class="text-lg font-black text-gray-300 dark:text-gray-600 group-hover:text-[#e21b22] leading-none shrink-0 w-5">0${idx+1}</span>
                <div>
                  <h4 class="text-[11px] font-bold text-gray-800 dark:text-gray-200 group-hover:text-[#e21b22] leading-snug">
                    ${item.title}
                  </h4>
                  <span class="text-[9px] text-gray-400 mt-0.5 block">${item.time}</span>
                </div>
              </a>
            </article>
          `).join('')}
        </div>
      </aside>

    </div>

    <!-- ৭. ওয়েব স্টোরিজ সেকশন (Vertical Web Stories) -->
    <section id="webstories" class="bg-white dark:bg-[#181a20] p-4 border border-gray-200 dark:border-gray-800 shadow-sm rounded">
      <div class="flex items-center justify-between mb-4 border-b border-gray-100 dark:border-gray-800 pb-2">
        <h3 class="headline-font text-sm font-black text-gray-900 dark:text-white uppercase flex items-center gap-2">
          <i class="fa-solid fa-bolt-lightning text-yellow-500"></i> NDTV WEB STORIES
        </h3>
        <span class="text-xs text-[#e21b22] font-bold hover:underline cursor-pointer">View All &rarr;</span>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        ${portalData.webStories.map(ws => `
          <div class="relative rounded overflow-hidden aspect-[9/16] group cursor-pointer shadow-md">
            <img src="${ws.img}" alt="${ws.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
            <div class="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent flex items-end p-3">
              <p class="text-white text-xs font-bold leading-snug group-hover:underline">
                ${ws.title}
              </p>
            </div>
          </div>
        `).join('')}
      </div>
    </section>

    <!-- ৮. মাল্টি-ক্যাটাগরি গ্রিড (India, Profit/Business, Gadgets, Movies) -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- INDIA SECTION -->
      <section id="india" class="bg-white dark:bg-[#181a20] p-4 border border-gray-200 dark:border-gray-800 shadow-sm">
        <div class="flex items-center justify-between border-b-2 border-black dark:border-gray-200 pb-1.5 mb-3">
          <h3 class="headline-font text-sm font-bold uppercase text-gray-900 dark:text-white">INDIA NEWS</h3>
          <span class="text-xs text-[#e21b22] font-bold hover:underline cursor-pointer">MORE &rarr;</span>
        </div>
        <div class="space-y-3">
          ${portalData.india.map(item => `
            <a href="${item.link}" target="_blank" class="flex gap-3 group border-b border-gray-50 dark:border-gray-800 pb-2">
              <img src="${item.image}" class="w-20 h-14 object-cover shrink-0 rounded bg-gray-100 dark:bg-gray-800">
              <div>
                <h4 class="text-xs font-bold text-gray-800 dark:text-gray-200 group-hover:text-[#e21b22] leading-snug">${item.title}</h4>
                <span class="text-[10px] text-gray-400">${item.time}</span>
              </div>
            </a>
          `).join('')}
        </div>
      </section>

      <!-- PROFIT / BUSINESS SECTION -->
      <section id="business" class="bg-white dark:bg-[#181a20] p-4 border border-gray-200 dark:border-gray-800 shadow-sm">
        <div class="flex items-center justify-between border-b-2 border-[#e21b22] pb-1.5 mb-3">
          <h3 class="headline-font text-sm font-bold uppercase text-gray-900 dark:text-white">NDTV PROFIT / BUSINESS</h3>
          <span class="text-xs text-[#e21b22] font-bold hover:underline cursor-pointer">MORE &rarr;</span>
        </div>
        <div class="space-y-3">
          ${portalData.business.map(item => `
            <a href="${item.link}" target="_blank" class="flex gap-3 group border-b border-gray-50 dark:border-gray-800 pb-2">
              <img src="${item.image}" class="w-20 h-14 object-cover shrink-0 rounded bg-gray-100 dark:bg-gray-800">
              <div>
                <h4 class="text-xs font-bold text-gray-800 dark:text-gray-200 group-hover:text-[#e21b22] leading-snug">${item.title}</h4>
                <span class="text-[10px] text-gray-400">${item.time}</span>
              </div>
            </a>
          `).join('')}
        </div>
      </section>

      <!-- GADGETS 360 / TECH -->
      <section id="tech" class="bg-white dark:bg-[#181a20] p-4 border border-gray-200 dark:border-gray-800 shadow-sm">
        <div class="flex items-center justify-between border-b-2 border-blue-600 pb-1.5 mb-3">
          <h3 class="headline-font text-sm font-bold uppercase text-gray-900 dark:text-white">GADGETS 360 / TECH</h3>
          <span class="text-xs text-blue-600 font-bold hover:underline cursor-pointer">MORE &rarr;</span>
        </div>
        <div class="space-y-3">
          ${portalData.tech.map(item => `
            <a href="${item.link}" target="_blank" class="flex gap-3 group border-b border-gray-50 dark:border-gray-800 pb-2">
              <img src="${item.image}" class="w-20 h-14 object-cover shrink-0 rounded bg-gray-100 dark:bg-gray-800">
              <div>
                <h4 class="text-xs font-bold text-gray-800 dark:text-gray-200 group-hover:text-blue-600 leading-snug">${item.title}</h4>
                <span class="text-[10px] text-gray-400">${item.time}</span>
              </div>
            </a>
          `).join('')}
        </div>
      </section>

      <!-- MOVIES / ENTERTAINMENT -->
      <section id="movies" class="bg-white dark:bg-[#181a20] p-4 border border-gray-200 dark:border-gray-800 shadow-sm">
        <div class="flex items-center justify-between border-b-2 border-purple-600 pb-1.5 mb-3">
          <h3 class="headline-font text-sm font-bold uppercase text-gray-900 dark:text-white">SHOWBIZ & MOVIES</h3>
          <span class="text-xs text-purple-600 font-bold hover:underline cursor-pointer">MORE &rarr;</span>
        </div>
        <div class="space-y-3">
          ${portalData.entertainment.map(item => `
            <a href="${item.link}" target="_blank" class="flex gap-3 group border-b border-gray-50 dark:border-gray-800 pb-2">
              <img src="${item.image}" class="w-20 h-14 object-cover shrink-0 rounded bg-gray-100 dark:bg-gray-800">
              <div>
                <h4 class="text-xs font-bold text-gray-800 dark:text-gray-200 group-hover:text-purple-600 leading-snug">${item.title}</h4>
                <span class="text-[10px] text-gray-400">${item.time}</span>
              </div>
            </a>
          `).join('')}
        </div>
      </section>

    </div>

    <!-- ৯. মতামত ও কলামিস্ট সেকশন (OPINION) -->
    <section id="opinion" class="bg-white dark:bg-[#181a20] p-4 border border-gray-200 dark:border-gray-800 shadow-sm">
      <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 pb-2 mb-4">
        <h3 class="headline-font text-sm font-black text-gray-900 dark:text-white uppercase tracking-wider">
          NDTV OPINION & EDITORIALS
        </h3>
        <span class="text-xs text-[#e21b22] font-bold hover:underline cursor-pointer">All Columns &rarr;</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        ${portalData.opinion.map(op => `
          <div class="flex items-start gap-3 p-2 group cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/40 rounded transition">
            <img src="${op.img}" class="w-12 h-12 rounded-full object-cover border border-gray-300 shrink-0">
            <div>
              <p class="text-[11px] font-black text-gray-900 dark:text-white">${op.author}</p>
              <p class="text-[10px] text-gray-400 mb-1">${op.role}</p>
              <h4 class="text-xs font-bold text-gray-800 dark:text-gray-200 group-hover:text-[#e21b22] leading-snug">
                "${op.title}"
              </h4>
            </div>
          </div>
        `).join('')}
      </div>
    </section>

    <!-- ১০. নিউজলেটার সাবস্ক্রিপশন বক্স -->
    <section class="bg-[#121820] text-white p-6 rounded-lg text-center max-w-2xl mx-auto shadow-md">
      <h3 class="headline-font text-lg font-bold mb-1">Get NDTV Morning & Evening Express Daily</h3>
      <p class="text-xs text-gray-400 mb-4">Subscribe to verified executive summaries directly to your inbox.</p>
      <form onsubmit="handleSubscribe(event)" class="flex flex-col sm:flex-row gap-2 justify-center max-w-md mx-auto">
        <input type="email" required placeholder="Enter your email address" class="px-4 py-2 text-xs rounded text-gray-900 focus:outline-none flex-1">
        <button type="submit" class="bg-[#e21b22] hover:bg-red-700 text-white font-bold text-xs px-5 py-2 rounded">SUBSCRIBE</button>
      </form>
      <p id="subMsg" class="text-green-400 text-xs mt-2 hidden">Thank you for subscribing!</p>
    </section>

  </main>

  <!-- ১১. ফুল মেগা-ফুটার ও সাইটম্যাপ (Complete Sitemap) -->
  <footer class="bg-[#121820] text-gray-400 text-xs mt-12 pt-10 pb-12 border-t border-gray-800">
    <div class="max-w-[1240px] mx-auto px-3 grid grid-cols-2 md:grid-cols-5 gap-6 border-b border-gray-800 pb-8 mb-6">
      <div>
        <h5 class="text-white font-bold text-xs uppercase mb-3">NEWS</h5>
        <ul class="space-y-1.5 text-[11px]">
          <li><a href="#" class="hover:text-white">India News</a></li>
          <li><a href="#" class="hover:text-white">World News</a></li>
          <li><a href="#" class="hover:text-white">Cities</a></li>
          <li><a href="#" class="hover:text-white">Opinion</a></li>
          <li><a href="#" class="hover:text-white">Offbeat</a></li>
        </ul>
      </div>
      <div>
        <h5 class="text-white font-bold text-xs uppercase mb-3">CHANNELS</h5>
        <ul class="space-y-1.5 text-[11px]">
          <li><a href="#" class="hover:text-white">NDTV 24x7</a></li>
          <li><a href="#" class="hover:text-white">NDTV India</a></li>
          <li><a href="#" class="hover:text-white">NDTV Profit</a></li>
          <li><a href="#" class="hover:text-white">NDTV MP-CG</a></li>
          <li><a href="#" class="hover:text-white">NDTV Rajasthan</a></li>
        </ul>
      </div>
      <div>
        <h5 class="text-white font-bold text-xs uppercase mb-3">SPECIALS</h5>
        <ul class="space-y-1.5 text-[11px]">
          <li><a href="#" class="hover:text-white">Cricket Live Scores</a></li>
          <li><a href="#" class="hover:text-white">Stock Markets</a></li>
          <li><a href="#" class="hover:text-white">Gadgets 360</a></li>
          <li><a href="#" class="hover:text-white">Food & Recipes</a></li>
          <li><a href="#" class="hover:text-white">Auto Expo</a></li>
        </ul>
      </div>
      <div>
        <h5 class="text-white font-bold text-xs uppercase mb-3">OTHERS</h5>
        <ul class="space-y-1.5 text-[11px]">
          <li><a href="#" class="hover:text-white">Weather Forecast</a></li>
          <li><a href="#" class="hover:text-white">Podcasts</a></li>
          <li><a href="#" class="hover:text-white">Web Stories</a></li>
          <li><a href="#" class="hover:text-white">Careers</a></li>
          <li><a href="#" class="hover:text-white">Privacy Policy</a></li>
        </ul>
      </div>
      <div>
        <h5 class="text-white font-bold text-xs uppercase mb-3">FOLLOW NDTV</h5>
        <div class="flex space-x-3 text-sm text-gray-300 mb-3">
          <i class="fa-brands fa-facebook hover:text-white cursor-pointer"></i>
          <i class="fa-brands fa-x-twitter hover:text-white cursor-pointer"></i>
          <i class="fa-brands fa-youtube hover:text-white cursor-pointer"></i>
          <i class="fa-brands fa-instagram hover:text-white cursor-pointer"></i>
        </div>
        <p class="text-[10px] text-gray-500">Available on iOS, Android, and Smart TV.</p>
      </div>
    </div>
    <div class="max-w-[1240px] mx-auto px-3 text-center text-[11px] text-gray-500 space-y-2">
      <div class="bg-[#e21b22] text-white font-black text-xl tracking-tighter px-2.5 py-0.5 inline-block">ndtv</div>
      <p>&copy; 2026 NDTV CONVERGENCE LIMITED. ALL RIGHTS RESERVED.</p>
    </div>
  </footer>

  <!-- ১২. মেগা-মেনু সাইড ড্রয়ার (Off-Canvas Menu) -->
  <div id="sideDrawer" class="fixed inset-0 bg-black/60 z-50 hidden" onclick="toggleDrawer()">
    <div class="w-80 bg-white dark:bg-[#181a20] h-full p-5 overflow-y-auto" onclick="event.stopPropagation()">
      <div class="flex justify-between items-center pb-4 border-b border-gray-200 dark:border-gray-800">
        <div class="bg-[#e21b22] text-white font-black text-lg px-2 py-0.5">ndtv menu</div>
        <button onclick="toggleDrawer()" class="text-lg font-bold">&times;</button>
      </div>
      <div class="py-4 space-y-3 text-sm font-bold">
        <a href="#india" onclick="toggleDrawer()" class="block hover:text-[#e21b22]">India</a>
        <a href="#business" onclick="toggleDrawer()" class="block hover:text-[#e21b22]">Business & Markets</a>
        <a href="#sports" onclick="toggleDrawer()" class="block hover:text-[#e21b22]">Cricket & Sports</a>
        <a href="#tech" onclick="toggleDrawer()" class="block hover:text-[#e21b22]">Gadgets 360</a>
        <a href="#movies" onclick="toggleDrawer()" class="block hover:text-[#e21b22]">Entertainment</a>
        <a href="#opinion" onclick="toggleDrawer()" class="block hover:text-[#e21b22]">Opinion</a>
        <a href="#webstories" onclick="toggleDrawer()" class="block hover:text-[#e21b22]">Web Stories</a>
      </div>
    </div>
  </div>

  <!-- ১৩. লাইভ টিভি পপআপ উইন্ডো -->
  <div id="videoModal" class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-black border border-gray-800 rounded-lg max-w-3xl w-full overflow-hidden shadow-2xl">
      <div class="flex justify-between items-center p-3 bg-gray-900 text-white">
        <span class="font-bold text-xs flex items-center gap-2">
          <span class="w-2.5 h-2.5 bg-red-600 rounded-full animate-ping"></span>
          NDTV 24x7 Continuous Satellite Desk
        </span>
        <button onclick="closeLiveVideo()" class="text-gray-400 hover:text-white font-bold px-2 text-base">&times;</button>
      </div>
      <div class="aspect-video bg-black flex items-center justify-center">
        <iframe class="w-full h-full" src="https://www.youtube.com/embed/live_stream?channel=UC4R8DWoMoI7CAwX8_BQOrMg" frameborder="0" allowfullscreen></iframe>
      </div>
    </div>
  </div>

  <!-- স্ক্রিপ্ট লজিক -->
  <script>
    function toggleDarkMode() {
      const isDark = document.documentElement.classList.toggle('dark');
      document.getElementById('themeIcon').className = isDark ? 'fa-solid fa-sun text-yellow-400' : 'fa-solid fa-moon';
    }

    function toggleDrawer() {
      document.getElementById('sideDrawer').classList.toggle('hidden');
    }

    function openLiveVideo() {
      document.getElementById('videoModal').classList.remove('hidden');
    }

    function closeLiveVideo() {
      document.getElementById('videoModal').classList.add('hidden');
    }

    function handleSubscribe(e) {
      e.preventDefault();
      document.getElementById('subMsg').classList.remove('hidden');
    }

    function switchLang() {
      const btn = document.getElementById('langBtn');
      btn.innerText = btn.innerText === 'বাংলা' ? 'ENGLISH' : 'বাংলা';
    }

    function searchStories(query) {
      const q = query.toLowerCase();
      document.querySelectorAll('#mainGridContainer h1, #mainGridContainer h3, #mainGridContainer h4').forEach(el => {
        const article = el.closest('article, div');
        if (article) {
          article.style.display = el.innerText.toLowerCase().includes(q) ? '' : 'none';
        }
      });
    }

    // প্রতি ৫ মিনিটে পেজ স্বয়ংক্রিয় রিফ্রেশ হবে
    setTimeout(() => { window.location.reload(); }, 5 * 60 * 1000);
  </script>
</body>
</html>
  `);
});

app.listen(PORT, () => {
  console.log(`\n======================================================`);
  console.log(`[NDTV Complete Suite Running] http://localhost:${PORT}`);
  console.log(`======================================================\n`);
});

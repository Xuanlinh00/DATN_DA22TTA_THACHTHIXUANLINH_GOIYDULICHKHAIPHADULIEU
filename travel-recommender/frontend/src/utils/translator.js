// -*- coding: utf-8 -*-
/**
 * Translator Utility - Translates English strings to Vietnamese and vice versa.
 */

const COUNTRY_MAP = {
  'japan': 'Nhật Bản',
  'south korea': 'Hàn Quốc',
  'thailand': 'Thái Lan',
  'vietnam': 'Việt Nam',
  'france': 'Pháp',
  'italy': 'Ý',
  'germany': 'Đức',
  'united kingdom': 'Vương quốc Anh',
  'uk': 'Vương quốc Anh',
  'united states': 'Mỹ',
  'usa': 'Mỹ',
  'singapore': 'Singapore',
  'indonesia': 'Indonesia',
  'malaysia': 'Malaysia',
  'china': 'Trung Quốc',
  'switzerland': 'Thụy Sĩ',
  'australia': 'Úc',
  'spain': 'Tây Ban Nha',
  'canada': 'Canada',
  'egypt': 'Ai Cập',
  'greece': 'Hy Lạp',
  'turkey': 'Thổ Nhĩ Kỳ',
  'brazil': 'Brazil',
  'south africa': 'Nam Phi',
  'new zealand': 'New Zealand',
  'india': 'Ấn Độ',
  'nepal': 'Nepal',
  'philippines': 'Philippines',
  'cambodia': 'Campuchia',
  'laos': 'Lào',
  'myanmar': 'Myanmar',
  'maldives': 'Maldives',
  'sri lanka': 'Sri Lanka',
  'netherlands': 'Hà Lan',
  'belgium': 'Bỉ',
  'austria': 'Áo',
  'portugals': 'Bồ Đào Nha',
  'portugal': 'Bồ Đào Nha',
  'russia': 'Nga',
  'sweden': 'Thụy Điển',
  'norway': 'Na Uy',
  'finland': 'Phần Lan',
  'denmark': 'Đan Mạch',
  'uae': 'UAE (Các Tiểu vương quốc Ả Rập Thống nhất)',
  'united arab emirates': 'UAE',
  'saudi arabia': 'Ả Rập Xê Út',
  'morocco': 'Ma-rốc',
  'peru': 'Peru',
  'mexico': 'Mexico',
  'argentina': 'Argentina',
  'chile': 'Chile',
  'colombia': 'Colombia',
  'hungary': 'Hungary',
  'iceland': 'Iceland',
  'ireland': 'Ireland',
  'croatia': 'Croatia',
  'czech republic': 'Cộng hòa Séc',
  'poland': 'Ba Lan',
  'romania': 'Romania',
  'ukraine': 'Ukraine',
  'israel': 'Israel',
  'jordan': 'Jordan',
  'kenya': 'Kenya',
  'tanzania': 'Tanzania',
  'ghana': 'Ghana',
  'ethiopia': 'Ethiopia',
  'nigeria': 'Nigeria',
  'cuba': 'Cuba',
  'ecuador': 'Ecuador',
  'bolivia': 'Bolivia',
  'venezuela': 'Venezuela',
  'panama': 'Panama',
  'costa rica': 'Costa Rica',
  'jamaica': 'Jamaica',
};

const CATEGORY_MAP = {
  // Khớp chính xác với các giá trị Type trong dataset
  'beach':        'Biển & Đảo',
  'coastal':      'Biển & Đảo',
  'island':       'Biển & Đảo',
  'mountain':     'Núi & Rừng',
  'highland':     'Núi & Rừng',
  'trekking':     'Núi & Rừng',
  'cultural':     'Văn hoá & Lịch sử',
  'historical':   'Lịch sử',
  'heritage':     'Di sản',
  'nature':       'Thiên nhiên',
  'eco':          'Sinh thái',
  'wildlife':     'Thiên nhiên hoang dã',
  'adventure':    'Phiêu lưu & Mạo hiểm',
  'sport':        'Thể thao & Mạo hiểm',
  'urban':        'Thành phố',
  'city':         'Thành phố',
  'metropolis':   'Đô thị',
  'shopping':     'Mua sắm & Giải trí',
  'wellness':     'Nghỉ dưỡng & Spa',
  'spa':          'Nghỉ dưỡng & Spa',
  'resort':       'Khu nghỉ dưỡng',
  'theme park':   'Vui chơi giải trí',
  'amusement':    'Vui chơi giải trí',
  'entertainment':'Giải trí',
  'religious':    'Tâm linh & Tín ngưỡng',
  'temple':       'Đền chùa',
  'museum':       'Bảo tàng',
  'desert':       'Sa mạc',
  'lake':         'Hồ & Sông',
  'river':        'Sông & Hồ',
  'waterfall':    'Thác nước',
  'volcano':      'Núi lửa',
  'glacier':      'Băng hà',
  'safari':       'Safari & Động vật hoang dã',
  'cruise':       'Du thuyền',
  'food':         'Ẩm thực',
  'culinary':     'Ẩm thực',
  'art':          'Nghệ thuật & Văn hoá',
  'festival':     'Lễ hội',
  'romantic':     'Lãng mạn',
  'family':       'Gia đình',
  'backpacking':  'Phượt',
};

const SEASON_MAP = {
  'spring': 'Xuân (T1–T3)',
  'summer': 'Hạ (T4–T6)',
  'autumn': 'Thu (T7–T9)',
  'fall':   'Thu (T7–T9)',
  'winter': 'Đông (T10–T12)',
  'all year': 'Quanh năm',
  'all seasons': 'Quanh năm',
  'year round': 'Quanh năm',
};

const BUDGET_MAP = {
  'budget':   'Tiết kiệm',
  'moderate': 'Tầm trung',
  'expensive':'Cao cấp',
  'luxury':   'Sang trọng',
  'free':     'Miễn phí',
};

// ── Reverse mapping: Vietnamese → English (for search) ──────────────────────
// Maps a Vietnamese keyword to one or more English search terms
const VI_TO_EN_SEARCH = {
  // Quốc gia
  'nhật bản': 'japan',     'nhật': 'japan',
  'hàn quốc': 'south korea', 'hàn': 'south korea',
  'thái lan': 'thailand',  'thái': 'thailand',
  'việt nam': 'vietnam',   'việt': 'vietnam',
  'pháp': 'france',
  'ý': 'italy',
  'đức': 'germany',
  'anh': 'united kingdom',
  'mỹ': 'united states',   'hoa kỳ': 'united states',
  'trung quốc': 'china',   'trung': 'china',
  'thụy sĩ': 'switzerland',
  'úc': 'australia',
  'tây ban nha': 'spain',
  'ai cập': 'egypt',
  'hy lạp': 'greece',
  'thổ nhĩ kỳ': 'turkey',
  'nam phi': 'south africa',
  'ấn độ': 'india',
  'campuchia': 'cambodia',
  'lào': 'laos',
  'hà lan': 'netherlands',
  'bỉ': 'belgium',
  'áo': 'austria',
  'bồ đào nha': 'portugal',
  'nga': 'russia',
  'thụy điển': 'sweden',
  'na uy': 'norway',
  'phần lan': 'finland',
  'đan mạch': 'denmark',
  'ả rập': 'saudi arabia',
  'ma rốc': 'morocco',     'marốc': 'morocco',
  'ba lan': 'poland',
  'ai len': 'ireland',     'ireland': 'ireland',
  'israel': 'israel',
  'kenya': 'kenya',
  'cuba': 'cuba',
  'panama': 'panama',
  // Loại hình du lịch
  'biển': 'beach',         'đảo': 'beach',       'bãi biển': 'beach',
  'núi': 'mountain',       'rừng': 'mountain',   'leo núi': 'mountain',
  'văn hóa': 'cultural',   'văn hoá': 'cultural','lịch sử': 'cultural',
  'di sản': 'cultural',    'cổ đại': 'cultural', 'di tích': 'cultural',
  'thiên nhiên': 'nature', 'sinh thái': 'nature','hoang dã': 'nature',
  'phiêu lưu': 'adventure','mạo hiểm': 'adventure',
  'thành phố': 'city',     'đô thị': 'city',     'phố': 'city',
  'nghỉ dưỡng': 'wellness','spa': 'wellness',    'resort': 'wellness',
  'vui chơi': 'theme park','giải trí': 'theme park',
  'mua sắm': 'shopping',
  // Châu lục / Khu vực
  'châu á': 'asia',        'á châu': 'asia',
  'châu âu': 'europe',     'âu châu': 'europe',
  'châu mỹ': 'america',
  'mỹ la tinh': 'latin america',
  'châu phi': 'africa',
  'châu đại dương': 'oceania',
  'đông nam á': 'southeast asia',
  'đông á': 'east asia',
  'trung đông': 'middle east',
  'nam á': 'south asia',
  // Mùa
  'mùa xuân': 'spring',    'xuân': 'spring',
  'mùa hạ': 'summer',      'hạ': 'summer',
  'mùa hè': 'summer',      'hè': 'summer',
  'mùa thu': 'autumn',     'thu': 'autumn',
  'mùa đông': 'winter',    'đông': 'winter',
  // Ngân sách
  'tiết kiệm': 'budget',   'rẻ': 'budget',       'giá rẻ': 'budget',
  'bình dân': 'moderate',  'tầm trung': 'moderate',
  'cao cấp': 'expensive',
  'sang trọng': 'luxury',  'xa xỉ': 'luxury',    'hạng sang': 'luxury',
  // Địa điểm / Từ khóa du lịch
  'đền': 'temple',         'chùa': 'temple',     'đền thờ': 'temple',
  'bảo tàng': 'museum',
  'cung điện': 'palace',
  'công viên': 'park',
  'quần đảo': 'islands',
  'hồ': 'lake',
  'sa mạc': 'desert',
  'tuyết': 'snow',
  'suối nước nóng': 'hot spring',  'nước nóng': 'hot spring',
  'lặn biển': 'diving',    'lặn': 'diving',
  'leo': 'hiking',         'đi bộ': 'hiking',
  'cắm trại': 'camping',
  'ẩm thực': 'food',       'đồ ăn': 'food',      'nhà hàng': 'restaurant',
  'lễ hội': 'festival',
  'kiến trúc': 'architecture',
  'nghệ thuật': 'art',
  'chợ': 'market',
  'phố cổ': 'old town',
  'vịnh': 'bay',
  'hang động': 'cave',     'hang': 'cave',
  'núi lửa': 'volcano',
  'thác nước': 'waterfall','thác': 'waterfall',
  'rạn san hô': 'reef',    'san hô': 'reef',
  'hoàng hôn': 'sunset',
  'bình minh': 'sunrise',
  'cầu': 'bridge',
  'tháp': 'tower',
  'trung tâm': 'center',
  'khu phố': 'district',
  'vườn quốc gia': 'national park',
  'khu bảo tồn': 'reserve',
  'safari': 'safari',
  'du thuyền': 'cruise',
  'đi thuyền': 'sailing',
  'leo thác': 'waterfall',
  'leo băng': 'glacier',   'băng': 'glacier',
  'đỉnh': 'peak',          'đỉnh núi': 'peak',
  'vũng tàu': 'vung tau',
  'hạ long': 'ha long',
  'hội an': 'hoi an',
  'huế': 'hue',
};

/**
 * Translates a Vietnamese search query to English keyword(s) for backend search.
 * - Nếu từ khóa là tiếng Việt và có bản dịch → trả về ONLY terms tiếng Anh
 * - Nếu không dịch được → giữ nguyên từ gốc (có thể là tiếng Anh)
 */
export const translateSearchQuery = (query) => {
  if (!query || !query.trim()) return [query];
  const q = query.trim().toLowerCase();
  const enTerms = new Set();

  // Exact match → chỉ lấy bản dịch tiếng Anh
  if (VI_TO_EN_SEARCH[q]) {
    enTerms.add(VI_TO_EN_SEARCH[q]);
    return [...enTerms];
  }

  // Partial match — tìm tất cả VI key xuất hiện trong query
  for (const [vi, en] of Object.entries(VI_TO_EN_SEARCH)) {
    if (q.includes(vi)) {
      enTerms.add(en);
    }
  }

  // Nếu không tìm được bản dịch nào → gửi nguyên từ gốc (tiếng Anh hoặc tên riêng)
  if (enTerms.size === 0) {
    return [q];
  }

  return [...enTerms];
};


// ── English → Vietnamese exports ────────────────────────────────────────────

/**
 * Strip country suffix in parentheses from destination name for display.
 * e.g., "Sacred Ruins (Vietnam)" → "Sacred Ruins"
 */
export const stripDisplayName = (name) => {
  if (!name) return 'N/A';
  return name.replace(/\s*\([^)]*\)\s*$/, '').trim() || name;
};

// Map English category keywords to Vietnamese (for fixing CSV descriptions)
const DESC_CATEGORY_FIX = {
  'beach': 'biển', 'nature': 'thiên nhiên', 'adventure': 'phiêu lưu',
  'historical': 'lịch sử', 'religious': 'tâm linh', 'cultural': 'văn hoá',
  'city': 'thành phố', 'mountain': 'núi', 'waterfall': 'thác nước',
  'urban': 'đô thị', 'eco': 'sinh thái', 'wildlife': 'hoang dã',
  'safari': 'safari', 'resort': 'nghỉ dưỡng', 'heritage': 'di sản',
};

// Map English season words to Vietnamese (for fixing CSV descriptions)
const DESC_SEASON_FIX = {
  'spring': 'mùa xuân',
  'summer': 'mùa hè',
  'autumn': 'mùa thu',
  'fall': 'mùa thu',
  'winter': 'mùa đông',
};

/**
 * Fix CSV description: strip country from name, replace English category/season keywords with Vietnamese.
 */
export const fixDescription = (desc, fullName) => {
  if (!desc) return '';
  let d = String(desc);
  // Remove "(Country)" from destination name within description
  if (fullName) {
    const stripped = stripDisplayName(fullName);
    if (stripped !== fullName) {
      d = d.split(fullName).join(stripped);
    }
  }
  // Replace English category keywords with Vietnamese equivalents
  for (const [eng, vie] of Object.entries(DESC_CATEGORY_FIX)) {
    d = d.replace(new RegExp(`\\b${eng}\\b`, 'gi'), vie);
  }
  // Replace English season words with Vietnamese equivalents
  for (const [eng, vie] of Object.entries(DESC_SEASON_FIX)) {
    d = d.replace(new RegExp(`\\b${eng}\\b`, 'gi'), vie);
  }
  return d;
};

export const translateCountry = (country) => {
  if (!country) return '';
  const key = country.toLowerCase().trim();
  return COUNTRY_MAP[key] || country;
};

export const translateCategory = (category) => {
  if (!category) return '';
  const key = category.toLowerCase().trim();
  if (CATEGORY_MAP[key]) return CATEGORY_MAP[key];
  for (const [eng, vie] of Object.entries(CATEGORY_MAP)) {
    if (key.includes(eng)) return vie;
  }
  return category;
};

export const translateSeason = (season) => {
  if (!season) return '';
  const key = season.toLowerCase().trim();
  return SEASON_MAP[key] || season;
};

export const translateBudget = (budget) => {
  if (!budget) return '';
  const key = budget.toLowerCase().trim();
  return BUDGET_MAP[key] || budget;
};

export const translateUnesco = (val) => {
  if (!val) return 'Không';
  const key = String(val).toLowerCase().trim();
  if (key === 'yes' || key === 'true' || key === '1') return 'Có';
  return 'Không';
};

// ── Destination Name Translation Map ──────────────────────────────────────────
const DESTINATION_MAP = {
  'marina bay sands & gardens': 'Marina Bay Sands',
  'zermatt matterhorn peak': 'Zermatt',
  'maldives overwater villas': 'Maldives',
  'santorini island sunsets': 'Santorini',
  'taj mahal': 'Đền Taj Mahal',
  'leh ladakh': 'Leh Ladakh',
  'interlaken adventure': 'Interlaken',
  'cappadocia hot balloons': 'Cappadocia',
  'burj khalifa dubai': 'Tháp Burj Khalifa',
  'great wall of china': 'Vạn Lý Trường Thành',
  'jaipur city': 'Jaipur',
  'kerala backwaters': 'Kerala',
  'seoul tower & palace': 'Seoul',
  'london big ben & eye': 'London',
  'istanbul hagia sophia': 'Thánh đường Hagia Sophia',
  'ubud bali cultural tour': 'Ubud (Bali)',
  'goa beaches': 'Goa',
  'jeju island beaches': 'Đảo Jeju',
  'sentosa island resort': 'Đảo Sentosa',
  'maafushi budget beaches': 'Đảo Maafushi',
  'stockholm gamla stan': 'Phố cổ Gamla Stan',
  'oslo fjords & museum peninsula': 'Vịnh hẹp Oslo',
  'troms northern lights hunting': 'Tromsø',
  'geirangerfjord cruising': 'Vịnh hẹp Geirangerfjord',
  'bergen bryggen wharf': 'Bến tàu cổ Bryggen',
  'lofoten islands scenic tour': 'Quần đảo Lofoten',
  'amsterdam historic canal cruise': 'Amsterdam',
  'keukenhof tulip festival': 'Vườn hoa Keukenhof',
  'zaanse schans windmill village': 'Làng cối xay gió Zaanse Schans',
  'rotterdam futuristic architecture': 'Rotterdam',
  'giethoorn village without roads': 'Làng cổ Giethoorn',
  'brussels grand place': 'Quảng trường Lớn (Brussels)',
  'bruges medieval canal tour': 'Bruges',
  'ghent castle of the counts': 'Lâu đài Gravensteen',
  'antwerp diamond district': 'Antwerp',
  'vienna schonbrunn palace': 'Cung điện Schönbrunn',
  'hallstatt alpine village': 'Làng cổ Hallstatt',
  'salzburg mozart heritage': 'Salzburg',
  'innsbruck alpine skiing': 'Innsbruck',
  'lisbon alfama & tram 28': 'Lisbon',
  'porto douro vineyard valley': 'Porto',
  'algarve cliffs & caves': 'Algarve',
  'sintra pena palace': 'Cung điện Pena (Sintra)',
  'cliffs of moher coastal walk': 'Vách đá Moher',
  'dublin guinness & trinity college': 'Dublin',
  'killarney ring of kerry tour': 'Vòng quanh Kerry',
  'copenhagen nyhavn harbour': 'Cảng Nyhavn (Copenhagen)',
  'tivoli gardens theme park': 'Công viên Tivoli',
  'kronborg castle elsinore': 'Lâu đài Kronborg',
  'rovaniemi santa claus village': 'Làng Ông già Noel Rovaniemi',
  'helsinki cathedral & market': 'Helsinki',
  'finnish lakeland & sauna tour': 'Vùng hồ Phần Lan',
  'reykjavik blue lagoon spa': 'Blue Lagoon (Reykjavik)',
  'gullfoss golden waterfall': 'Thác nước Gullfoss',
  'reynisfjara black sand beach': 'Bãi biển cát đen Reynisfjara',
  'jokulsarlon glacier lagoon': 'Đầm sông băng Jökulsárlón',
  'krakow wawel castle & square': 'Krakow',
  'warsaw old town restoration': 'Phố cổ Warsaw',
  'tatra mountains zakopane': 'Zakopane',
  'prague charles bridge & castle': 'Prague',
  'cesky krumlov castle town': 'Cesky Krumlov',
  'karlovy vary spa town': 'Karlovy Vary',
  'budapest parliament on danube': 'Budapest',
  'szechenyi thermal bath pools': 'Nhà tắm hơi Szechenyi',
  'lake balaton resort beaches': 'Hồ Balaton',
  'dubrovnik game of thrones walls': 'Dubrovnik',
  'plitvice lakes waterfall trail': 'Hồ Plitvice',
  'split diocletian palace': 'Split',
  'hvar island sun & yacht port': 'Đảo Hvar',
  'kuala lumpur petronas towers': 'Kuala Lumpur',
  'penang georgetown heritage art': 'Georgetown (Penang)',
  'langkawi cable car & skybridge': 'Langkawi',
  'kota kinabalu nature trekking': 'Kota Kinabalu',
  'boracay island white beach': 'Boracay',
  'el nido bacuit bay islands': 'El Nido',
  'chocolate hills bohol adventure': 'Đồi sô-cô-la Bohol',
  'intramuros walled city manila': 'Manila',
  'angkor wat heritage park': 'Angkor Wat',
  'phnom penh palace & silver pagoda': 'Phnom Penh',
  'koh rong tropical beaches': 'Đảo Koh Rong',
  'luang prabang heritage town': 'Luang Prabang',
  'vang vieng karst nature tour': 'Vang Vieng',
  'kuang si turquoise waterfalls': 'Thác Kuang Si',
  'bagan hot air balloon valley': 'Bagan',
  'inle lake fisherman villages': 'Hồ Inle',
  'shwedagon pagoda yangon': 'Yangon',
  'sigiriya ancient lion rock': 'Núi đá sư tử Sigiriya',
  'ella train & nine arch bridge': 'Ella',
  'temple of the tooth kandy': 'Kandy',
  'kathmandu durbar square temples': 'Kathmandu',
  'everest base camp mountain trek': 'Everest Base Camp',
  'pokhara phewa lake resort': 'Pokhara',
  'taipei 101 observatory': 'Đài Bắc 101',
  'jiufen old street lanterns': 'Phố cổ Cửu Phần',
  'taroko marble gorge national park': 'Hẻm núi Taroko',
  'gobi desert singing dunes': 'Sa mạc Gobi',
  'terelj national park ger camp': 'Công viên quốc gia Terelj',
  'almaty charyn canyon': 'Hẻm núi Charyn',
  'astana bayterek tower': 'Tháp Bayterek',
  'cartagena spanish walled city': 'Cartagena',
  'coffee triangle plantation tour': 'Coffee Triangle',
  'easter island rapa nui moai': 'Đảo Phục Sinh',
  'torres del paine national park': 'Torres del Paine',
  'galapagos islands wildlife cruise': 'Quần đảo Galapagos',
  'arenal volcano hot springs': 'Núi lửa Arenal',
  'panama canal miraflores locks': 'Kênh đào Panama',
  'old havana classic cars': 'Havana',
  'varadero beach resorts': 'Varadero',
  'negril cliffs & seven mile beach': 'Negril',
  'yasawa islands coral reefs': 'Quần đảo Yasawa',
  'to sua ocean trench swim': 'Hố sụt To Sua',
  'serengeti national park safari': 'Serengeti',
  'mount kilimanjaro summit climb': 'Núi Kilimanjaro',
  'morondava avenue of baobabs': 'Đại lộ bao báp',
  'la digue anse source beach': "Đảo La Digue",
  'chamarel coloured earth dunes': 'Chamarel',
  'sapa terrace rice fields': 'Sa Pa',
  'phu quoc sunset beach': 'Phú Quốc',
  'trang an scenic landscape': 'Tràng An',
  'kyoto fushimi inari shrine': 'Đền Fushimi Inari',
  'osaka dotonbori street food': 'Dotonbori (Osaka)',
  'grand canyon south rim': 'Grand Canyon',
  'new york times square neon': 'Quảng trường Thời đại',
  'louvre art museum paris': 'Bảo tàng Louvre',
  'french riviera nice beaches': 'Nice (Pháp)',
  'zhangjiajie avatar mountains': 'Trương Gia Giới',
  'shanghai the bund skyline': 'Bến Thượng Hải',
  'chiang mai lantern festival': 'Chiang Mai',
  'phuket patong beach party': 'Phuket',
};

/**
 * Translates a destination name to Vietnamese.
 * Supports direct mappings and dynamic translation for synthetic ones.
 */
export const translateDestinationName = (name, countryName = '') => {
  if (!name) return 'N/A';
  const key = name.toLowerCase().trim();
  
  // 1. Check direct mapping first
  if (DESTINATION_MAP[key]) {
    return DESTINATION_MAP[key];
  }

  // 2. Check synthetic country-related patterns
  if (name.includes('Hidden Valley Trail')) {
    const rawCountry = name.replace('Hidden Valley Trail', '').trim();
    const cleanCountry = translateCountry(rawCountry || countryName);
    return `Đường mòn thung lũng ẩn giấu (${cleanCountry})`;
  }
  if (name.includes('Ancient Royal Palace')) {
    const rawCountry = name.replace('Ancient Royal Palace', '').trim();
    const cleanCountry = translateCountry(rawCountry || countryName);
    return `Cung điện hoàng gia cổ đại (${cleanCountry})`;
  }
  if (name.includes('Coastal Horizon Beach')) {
    const rawCountry = name.replace('Coastal Horizon Beach', '').trim();
    const cleanCountry = translateCountry(rawCountry || countryName);
    return `Bãi biển chân trời ven biển (${cleanCountry})`;
  }
  if (name.includes('Summit Peak Adventure')) {
    const rawCountry = name.replace('Summit Peak Adventure', '').trim();
    const cleanCountry = translateCountry(rawCountry || countryName);
    return `Hành trình chinh phục đỉnh cao (${cleanCountry})`;
  }

  // 3. Fallback to adjective-noun combination translation for other synthetic ones
  const adjMap = {
    'hidden': 'ẩn giấu',
    'golden': 'vàng',
    'serene': 'yên bình',
    'ancient': 'cổ kính',
    'grand': 'hùng vĩ',
    'mystic': 'huyền bí',
    'sacred': 'linh thiêng',
    'lush': 'xanh mát',
    'crystal': 'pha lê'
  };

  const nounMap = {
    'ruins': 'Di tích',
    'park': 'Công viên',
    'pagoda': 'Chùa',
    'beach': 'Bãi biển',
    'temple': 'Đền thờ',
    'plaza': 'Quảng trường',
    'falls': 'Thác nước',
    'forest': 'Khu rừng',
    'valley': 'Thung lũng',
    'canyon': 'Hẻm núi'
  };

  const words = key.split(/\s+/);
  if (words.length === 2) {
    const [adj, noun] = words;
    if (adjMap[adj] && nounMap[noun]) {
      return `${nounMap[noun]} ${adjMap[adj]}`;
    }
  }

  // If there's a parentheses country, translate inside it
  const match = name.match(/^(.+?)\s*\((.+?)\)$/);
  if (match) {
    const baseName = match[1];
    const cName = match[2];
    const transBase = translateDestinationName(baseName, cName);
    const transCountry = translateCountry(cName);
    return `${transBase} (${transCountry})`;
  }

  return name;
};

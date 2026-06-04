// -*- coding: utf-8 -*-
/**
 * Image Service - Maps destination types to high-quality Unsplash travel photos.
 * Uses consistent hashing to ensure a destination always gets the same image.
 */

const IMAGES_BY_TYPE = {
  beach: [
    'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1473116763269-255ea760754e?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1520116468888-95b2d18a79b2?w=800&auto=format&fit=crop&q=60'
  ],
  mountain: [
    'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1486873249359-2731bd6dafc7?w=800&auto=format&fit=crop&q=60'
  ],
  cultural: [
    'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1449034446853-66c86144b0ad?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=800&auto=format&fit=crop&q=60'
  ],
  nature: [
    'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1472214222541-d510753a4907?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1500627869374-13cd993b1115?w=800&auto=format&fit=crop&q=60'
  ],
  adventure: [
    'https://images.unsplash.com/photo-1501555088652-021faa106b9b?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1527853787696-f7bc74c2e357?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1533240332313-0db49b459ad6?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&auto=format&fit=crop&q=60'
  ],
  urban: [
    'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1496568818309-53d7c7753022?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&auto=format&fit=crop&q=60'
  ],
  default: [
    'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&auto=format&fit=crop&q=60'
  ]
};

// Simple hash function to consistently map a name to an index
const getStringHash = (str) => {
  let hash = 0;
  if (!str) return hash;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash |= 0; // Convert to 32bit integer
  }
  return Math.abs(hash);
};

export const getDestinationImage = (name, type) => {
  if (!name) return IMAGES_BY_TYPE.default[0];
  
  // Clean up category / type key to map to standard types
  let categoryKey = 'default';
  if (type) {
    const t = type.toLowerCase();
    if (t.includes('beach') || t.includes('biển') || t.includes('đảo')) categoryKey = 'beach';
    else if (t.includes('mountain') || t.includes('núi') || t.includes('phượt')) categoryKey = 'mountain';
    else if (t.includes('cultur') || t.includes('văn hóa') || t.includes('lịch sử') || t.includes('temple') || t.includes('religious') || t.includes('tôn giáo')) categoryKey = 'cultural';
    else if (t.includes('nature') || t.includes('thiên nhiên') || t.includes('rừng') || t.includes('khám phá')) categoryKey = 'nature';
    else if (t.includes('adventur') || t.includes('mạo hiểm')) categoryKey = 'adventure';
    else if (t.includes('urban') || t.includes('đô thị') || t.includes('thành phố') || t.includes('sầm uất')) categoryKey = 'urban';
  }
  
  const images = IMAGES_BY_TYPE[categoryKey] || IMAGES_BY_TYPE.default;
  const hash = getStringHash(name);
  const index = hash % images.length;
  
  // Return high-res if requested for detail banners
  return images[index];
};

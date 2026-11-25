export const EARTH_RADIUS_M = 6371008.8;
export function coordinates(lat, lon) {
  const a=Number(lat),o=Number(lon);
  if (String(lat).trim()===''||String(lon).trim()===''||!Number.isFinite(a)||!Number.isFinite(o)||Math.abs(a)>90||Math.abs(o)>180) throw new Error('Enter a latitude from −90 to 90 and longitude from −180 to 180.');
  return {lat:a,lon:o};
}
export function distance(a,b) {
  const r=Math.PI/180,dlat=(b.lat-a.lat)*r,dlon=(b.lon-a.lon)*r;
  const h=Math.sin(dlat/2)**2+Math.cos(a.lat*r)*Math.cos(b.lat*r)*Math.sin(dlon/2)**2;
  return 2*EARTH_RADIUS_M*Math.asin(Math.sqrt(Math.min(1,h)));
}
export function validateConfig(c) {
  if(!c||!/^[a-z]{2,3}$/.test(c.language)||!Array.isArray(c.presets)||!c.presets.length)throw new Error('Invalid place configuration.');
  return {...c,result_limit:Math.max(1,Math.min(50,Number(c.result_limit)||40)),default_radius_m:Math.max(100,Math.min(10000,Number(c.default_radius_m)||1500)),presets:c.presets.map(p=>({...p,...coordinates(p.lat,p.lon)}))};
}
export function normalizePages(payload,center,language='en') {
  if(payload.error)throw new Error(payload.error.info||'Wikipedia rejected the request.');
  return Object.values(payload.query?.pages||{}).filter(p=>p.pageid>0&&p.coordinates?.length).map(p=>{
    const c=coordinates(p.coordinates[0].lat,p.coordinates[0].lon);
    const image=p.thumbnail?.source;
    return {id:p.pageid,title:String(p.title),extract:String(p.extract||'Read the original article for the history of this place.').slice(0,1100),...c,distance:distance(center,c),url:`https://${language}.wikipedia.org/?curid=${p.pageid}`,revision:p.lastrevid||null,image:typeof image==='string'&&/^https:\/\/upload\.wikimedia\.org\//.test(image)?image:null};
  }).sort((a,b)=>a.distance-b.distance||a.title.localeCompare(b.title));
}
export function searchUrl(query,language='en') {
  const p=new URLSearchParams({action:'query',format:'json',origin:'*',generator:'search',gsrsearch:query,gsrlimit:'10',prop:'coordinates|info',inprop:'url'});
  return `https://${language}.wikipedia.org/w/api.php?${p}`;
}
export function nearbyUrl(center,radius,limit,language='en') {
  const c=coordinates(center.lat,center.lon);
  if(!Number.isFinite(radius)||radius<100||radius>10000)throw new Error('Choose a radius between 100 m and 10 km.');
  const p=new URLSearchParams({action:'query',format:'json',origin:'*',generator:'geosearch',ggscoord:`${c.lat}|${c.lon}`,ggsradius:String(radius),ggslimit:String(Math.min(50,Math.max(1,limit))),ggsnamespace:'0',prop:'coordinates|pageimages|extracts|info',inprop:'url',piprop:'thumbnail',pithumbsize:'360',exintro:'1',explaintext:'1',exchars:'700',exlimit:'max',colimit:'max'});
  return `https://${language}.wikipedia.org/w/api.php?${p}`;
}
export function readSaved(raw) {
  try {
    const a=JSON.parse(raw||'[]');if(!Array.isArray(a))return [];
    return a.slice(0,200).filter(p=>p&&Number.isInteger(p.id)&&p.id>0&&typeof p.title==='string'&&/^https:\/\/[a-z]{2,3}\.wikipedia\.org\/\?curid=\d+$/.test(p.url)&&Number.isFinite(p.lat)&&Number.isFinite(p.lon)&&Math.abs(p.lat)<=90&&Math.abs(p.lon)<=180).map(p=>({...p,image:typeof p.image==='string'&&/^https:\/\/upload\.wikimedia\.org\//.test(p.image)?p.image:null}));
  }catch{return [];}
}
export function distanceText(m){return m<1000?`${Math.round(m)} m`:`${(m/1000).toFixed(1)} km`;}

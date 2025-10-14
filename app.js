async function init(){
  // load devices.json
  const res = await fetch('devices.json');
  const devices = await res.json();
  window.devices = devices;
  populateBrands(devices);
  renderList(devices,1);
  setupEvents();
  // get user country for price
  try {
    const r = await fetch('https://ipapi.co/json/');
    const info = await r.json();
    window.userCountry = info.country || 'US';
  } catch(e) {
    window.userCountry = 'US';
  }
}

function populateBrands(devices){
  const brands = [...new Set(devices.map(d=>d.brand))].sort();
  const sel = document.getElementById('brandFilter');
  brands.forEach(b=>{ const opt=document.createElement('option'); opt.value=b; opt.textContent=b; sel.appendChild(opt); });
}

function renderList(devices,page=1){
  const perPage = 12;
  const start = (page-1)*perPage;
  const pageItems = devices.slice(start, start+perPage);
  const list = document.getElementById('list');
  if(pageItems.length===0){ list.innerHTML='<p style="padding:12px;color:#666">No devices</p>'; return; }
  list.innerHTML = pageItems.map(d=>`<div class="card" data-id="${escapeHtml(d.id)}">
    <div class="thumb">${(d.brand||'')[0]||'?'}</div>
    <div class="meta"><h3>${escapeHtml(d.brand)} ${escapeHtml(d.model)}</h3>
    <p>${escapeHtml((d.display && (d.display.size||d.display)) || '')} · ${escapeHtml(d.memory && (d.memory.ram || ''))} · ${escapeHtml(showPrice(d))}</p>
    <p class="muted">${escapeHtml(d.release_date||'')}</p></div>
  </div>`).join('');
  document.querySelectorAll('.card').forEach(c=>c.addEventListener('click', ()=>{ const id = c.getAttribute('data-id'); showDetails(id); }));
  renderPaging(devices, page, perPage);
}

function renderPaging(devices, page, perPage){
  const pages = Math.ceil(devices.length / perPage) || 1;
  const el = document.getElementById('paging');
  el.innerHTML = Array.from({length:pages}, (_,i)=>`<button class="page-btn" data-page="${i+1}" ${i+1===page? 'style="font-weight:700"' : ''}>${i+1}</button>`).join(' ');
  el.querySelectorAll('.page-btn').forEach(b=>b.addEventListener('click', ()=>{ renderList(devices, parseInt(b.dataset.page)); }));
}

function showDetails(id){
  const d = window.devices.find(x=> String(x.id) === String(id));
  if(!d) return;
  const modal = document.getElementById('detailModal');
  const body = document.getElementById('detailBody');
  body.innerHTML = `<h2>${escapeHtml(d.brand)} ${escapeHtml(d.model)}</h2>
    <div class="small">Released: ${escapeHtml(d.release_date)}</div>
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:10px">
      ${(d.images && d.images.gallery ? d.images.gallery.map((u,i)=>`<div style="width:120px;height:120px;border-radius:8px;background:#eef2ff;display:flex;align-items:center;justify-content:center">${i+1}</div>`).join('') : '<div style="width:120px;height:120px;border-radius:8px;background:#eef2ff;display:flex;align-items:center;justify-content:center">No Image</div>')}
    </div>
    <table class="specs-table">
      <tr><th>Display</th><td>${escapeHtml((d.display && (d.display.size || d.display))||'')}</td></tr>
      <tr><th>OS</th><td>${escapeHtml(d.platform && d.platform.os || '')}</td></tr>
      <tr><th>Chipset</th><td>${escapeHtml(d.platform && d.platform.chipset || '')}</td></tr>
      <tr><th>RAM</th><td>${escapeHtml(d.memory && d.memory.ram || '')}</td></tr>
      <tr><th>Storage</th><td>${escapeHtml(d.memory && d.memory.storage || '')}</td></tr>
      <tr><th>Battery</th><td>${escapeHtml(d.battery && (d.battery.capacity || '') )}</td></tr>
      <tr><th>Camera</th><td>${escapeHtml(JSON.stringify(d.camera) || '')}</td></tr>
      <tr><th>Price</th><td>${escapeHtml(showPrice(d))}</td></tr>
      <tr><th>Buy</th><td>${d.affiliate_links && d.affiliate_links.length ? `<a href="${escapeHtml(d.affiliate_links[0].url)}" target="_blank" rel="noopener">Buy Now</a>` : '—'}</td></tr>
    </table>`;
  modal.classList.add('show'); modal.setAttribute('aria-hidden','false');
}

function setupEvents(){
  document.getElementById('closeModal').addEventListener('click', closeModal);
  document.getElementById('detailModal').addEventListener('click', (e)=>{ if(e.target.id==='detailModal') closeModal(); });
  document.getElementById('brandFilter').addEventListener('change', (e)=>{ const v=e.target.value; const list = window.devices.filter(d=> v==='' || d.brand===v); renderList(list,1); });
  document.getElementById('search').addEventListener('input', (e)=>{ const q=e.target.value.toLowerCase(); const list = window.devices.filter(d=> (d.brand+' '+d.model+' '+(d.platform && d.platform.os || '')).toLowerCase().includes(q)); renderList(list,1); });
  document.getElementById('themeToggle').addEventListener('click', ()=>{ document.documentElement.classList.toggle('dark'); });
}

function closeModal(){ const modal=document.getElementById('detailModal'); modal.classList.remove('show'); modal.setAttribute('aria-hidden','true'); }

function escapeHtml(s){ return String(s||'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'); }

function showPrice(d){
  try{
    const country = window.userCountry || 'US';
    if(d.price_region && d.price_region[country]) return d.price_region[country];
    if(d.price) return d.price;
    // fallback: show usd if available
    if(d.currency && d.price) return `${d.currency} ${d.price}`;
    return '—';
  }catch(e){
    return d.price || '—';
  }
}

window.addEventListener('load', init);


async function loadData(){
  const res = await fetch('devices.json');
  const devices = await res.json();
  window.devices = devices;
  populateBrands(devices);
  renderList(devices);
}
function populateBrands(devices){
  const brands = [...new Set(devices.map(d=>d.brand))].sort();
  const sel = document.getElementById('brandFilter');
  brands.forEach(b=>{ const opt = document.createElement('option'); opt.value=b; opt.textContent=b; sel.appendChild(opt); });
}
function renderList(devices){
  const list = document.getElementById('list');
  list.innerHTML = devices.slice(0,48).map(d=>`<div class="card"><h3>${escapeHtml(d.brand)} ${escapeHtml(d.model)}</h3><p>${escapeHtml(d.display)} · ${escapeHtml(d.ram)} · ${escapeHtml(d.price || '')}</p></div>`).join('');
}
function escapeHtml(s){ return String(s||'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'); }
loadData();

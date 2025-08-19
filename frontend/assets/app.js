const API_BASE = "http://127.0.0.1:5000";

function setAuth(token, user){
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
}
function getToken(){ return localStorage.getItem("token"); }
function getUser(){ try { return JSON.parse(localStorage.getItem("user")); } catch(e){ return null; } }
function authHeader(){ return getToken() ? { "Authorization": `Bearer ${getToken()}` } : {}; }

async function api(path, { method = 'GET', body, headers = {}, formData } = {}){
  const opts = { method, headers: { ...headers, ...authHeader() } };
  if(formData){
    opts.body = formData;
  } else {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = body ? JSON.stringify(body) : undefined;
  }
  const res = await fetch(`${API_BASE}${path}`, opts);
  if(!res.ok){
    let err;
    try { err = await res.json(); } catch{ err = { error: res.statusText }; }
    throw new Error(err.error || 'Request failed');
  }
  // handle file download endpoints separately
  if(res.headers.get('content-type')?.includes('application/json')){
    return res.json();
  }
  return res;
}

function requireLogin(){
  if(!getToken()) window.location.href = 'login.html';
}

function renderStatusBadge(s){
  return `<span class="badge ${s}">${s.replace('_',' ')}</span>`;
}

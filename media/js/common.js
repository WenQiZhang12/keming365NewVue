// 公共工具函数
function $(id){return document.getElementById(id)}

// API 基础路径
const API_BASE = '/api/v1';

// 用户认证相关
function checkLogin(){
  var token = localStorage.getItem('token');
  return token ? true : false;
}

function logout(){
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  location.href='index.html';
}

function updateUserUI(){
  var el = $('headerUser');
  if(!el) return;
  
  var userStr = localStorage.getItem('user');
  if(userStr){
    try{
      var user = JSON.parse(userStr);
      var initial = (user.name || user.username || '用户').charAt(0).toUpperCase();
      el.innerHTML = '<div class="user-dropdown"><div class="avatar" onclick="toggleMenu()">'+initial+'</div><div class="dropdown-menu" id="userMenu"><div class="dropdown-item" onclick="location.href=\'profile.html\'">👤 个人中心</div><div class="dropdown-item" onclick="window.open(\'http://58.56.66.164:7777/manage/\',\'_blank\')">⚙️ 管理后台</div><div class="dropdown-divider"></div><div class="dropdown-item danger" onclick="logout()">🚪 退出登录</div></div></div>';
      var t = user.type;
      setTimeout(()=>{var items=document.querySelectorAll('.dropdown-item');if(items.length>1)items[1].style.display=(t===2)?'block':'none';},0);
    }catch(e){
      el.innerHTML='<a href="login.html" class="btn btn-login">登录</a><a href="register.html" class="btn btn-reg">注册</a>';
    }
  }else{
    el.innerHTML='<a href="login.html" class="btn btn-login">登录</a><a href="register.html" class="btn btn-reg">注册</a>';
  }
}

function toggleMenu(){
  var menu = $('userMenu');
  if(menu) menu.classList.toggle('show');
}

// 点击外部关闭下拉菜单
document.addEventListener('click', function(e){
  var menu = $('userMenu');
  if(menu && !menu.contains(e.target) && !e.target.classList.contains('avatar')){
    menu.classList.remove('show');
  }
});

// API 请求封装
function api(url, opts){
  opts = opts || {};
  var token = localStorage.getItem('token');
  if(token) opts.headers = opts.headers || {};
  if(token) opts.headers['Authorization'] = 'Bearer ' + token;
  
  return fetch(url, {
    method: opts.method || 'GET',
    headers: opts.headers || {'Content-Type':'application/json'},
    body: opts.body ? JSON.stringify(opts.body) : null
  }).then(res => res.json());
}

// 简化的API调用
async function apiCall(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  const token = localStorage.getItem('token');
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(API_BASE + '/' + path.replace(/^\//,''), opts);
  if (r.status === 204) return {};
  const data = await r.json();
  if (!r.ok) throw new Error(data.message || data.detail || '请求失败');
  return data;
}

// Toast提示
function toast(msg, type='info') {
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2500);
}

// 登录弹窗相关
let loginOverlay = null;

function showLogin() {
  if (!loginOverlay) {
    loginOverlay = document.createElement('div');
    loginOverlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:999;display:flex;align-items:center;justify-content:center';
    loginOverlay.innerHTML = `
      <div style="background:#fff;border-radius:12px;padding:32px;width:380px;position:relative">
        <span style="position:absolute;right:16px;top:12px;cursor:pointer;font-size:20px" onclick="closeLogin()">✕</span>
        <h2 style="margin-bottom:20px">🔐 登录</h2>
        <div style="margin-bottom:14px"><input id="loginUser" placeholder="用户名" style="width:100%;padding:10px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;outline:none"></div>
        <div style="margin-bottom:14px"><input id="loginPass" type="password" placeholder="密码" style="width:100%;padding:10px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;outline:none"></div>
        <button onclick="doLogin()" style="width:100%;padding:10px;background:#1a237e;color:#fff;border:none;border-radius:6px;font-size:15px;cursor:pointer">登录</button>
        <p id="loginErr" style="color:#e53935;font-size:13px;margin-top:8px;text-align:center"></p>
      </div>`;
    document.body.appendChild(loginOverlay);
    loginOverlay.addEventListener('click', e => { if(e.target===loginOverlay) closeLogin(); });
  }
  loginOverlay.style.display = 'flex';
  setTimeout(() => $('loginUser')?.focus(), 100);
}

function closeLogin() { 
  if (loginOverlay) loginOverlay.style.display = 'none'; 
}

async function doLogin() {
  const u = $('loginUser')?.value, p = $('loginPass')?.value;
  if (!u || !p) { $('loginErr').textContent = '请填写用户名和密码'; return; }
  try {
    const d = await apiCall('POST', 'accounts/auth/login/', { username:u, password:p });
    localStorage.setItem('token', d.access);
    localStorage.setItem('user', JSON.stringify(d.user));
    closeLogin(); 
    updateUserUI(); 
    toast('登录成功', 'success');
  } catch(e) { $('loginErr').textContent = e.message; }
}

// URL参数获取
function getUrlParam(name) {
  return new URLSearchParams(window.location.search).get(name) || '';
}

// HTML转义
function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/[&<>"']/g, m => {
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m];
  });
}

// 页面加载时更新用户状态
document.addEventListener('DOMContentLoaded', function(){
  updateUserUI();
});
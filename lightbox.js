(function(){var links=[].slice.call(document.querySelectorAll('.gallery a[data-idx]'));var lb=document.getElementById('lb');if(!lb||!links.length)return;
var img=document.getElementById('lb-img'),cap=document.getElementById('lb-cap'),i=0,last;
function show(n){i=(n+links.length)%links.length;var a=links[i];img.src=a.href;img.alt=a.querySelector('img').alt;cap.textContent=a.dataset.caption+'  ('+(i+1)+' / '+links.length+')';}
function open(n){last=document.activeElement;show(n);lb.hidden=false;document.body.style.overflow='hidden';lb.querySelector('.lb-close').focus();}
function close(){lb.hidden=true;document.body.style.overflow='';img.src='';if(last)last.focus();}
links.forEach(function(a,n){a.addEventListener('click',function(e){e.preventDefault();open(n);});});
lb.querySelector('.lb-close').onclick=close;lb.querySelector('.lb-prev').onclick=function(){show(i-1)};lb.querySelector('.lb-next').onclick=function(){show(i+1)};
lb.addEventListener('click',function(e){if(e.target===lb)close();});
document.addEventListener('keydown',function(e){if(lb.hidden)return;if(e.key==='Escape')close();if(e.key==='ArrowLeft')show(i-1);if(e.key==='ArrowRight')show(i+1);});
var x0=null;lb.addEventListener('touchstart',function(e){x0=e.touches[0].clientX},{passive:true});lb.addEventListener('touchend',function(e){if(x0===null)return;var dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40)show(i+(dx<0?1:-1));x0=null;});
})();

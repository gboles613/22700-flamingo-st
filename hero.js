(function(){
  var b=document.querySelector('.banner'),badge=document.getElementById('price-badge'),hero=document.querySelector('.hero'),img=document.querySelector('.hero-img');
  var GX=0.745,GY=0.62; /* garage door center in the photo */
  function place(){
    if(b)document.documentElement.style.setProperty('--bannerH',b.offsetHeight+'px');
    if(!badge||!hero||!img)return;
        var cw=img.clientWidth,ch=img.clientHeight,nw=img.naturalWidth||1920,nh=img.naturalHeight||1440;
    var sc=Math.max(cw/nw,ch/nh),iw=nw*sc,ih=nh*sc;
    var pos=getComputedStyle(img).objectPosition.split(' ');
    var px=parseFloat(pos[0])/100,py=parseFloat(pos[1]||'50%')/100;
    var ox=(cw-iw)*px+img.offsetLeft,oy=(ch-ih)*py+(img.getBoundingClientRect().top-hero.getBoundingClientRect().top);
    badge.style.left=(ox+GX*iw)+'px';badge.style.top=(oy+GY*ih)+'px';
  }
  window.addEventListener('resize',place);if(img&&!img.complete)img.addEventListener('load',place);place();
})();

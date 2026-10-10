/* Copos de nieve que se aceleran cuando el aire está encendido (canvas 2D, sin librerías).
   window.Frio(canvas, {static, count}) -> { set(on) } */
(function () {
  function Frio(canvas, opts) {
    opts = opts || {};
    var ctx = canvas.getContext('2d');
    var reduce = opts.static || window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var W = 0, H = 0, t = 0, power = 0, target = 0;
    var N = opts.count || (window.innerWidth < 600 ? 60 : 110);
    var flakes = [];

    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = canvas.clientWidth; H = canvas.clientHeight;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function spawn(f, anywhere) {
      f.x = Math.random() * W; f.y = anywhere ? Math.random() * H : -10;
      f.r = 1 + Math.pow(Math.random(), 2.2) * 6; f.d = Math.random() * 6.28;
      f.rot = Math.random() * 6.28; f.vr = (Math.random() - 0.5) * 0.6;
      return f;
    }
    function star(f, a) {
      ctx.save(); ctx.translate(f.x, f.y); ctx.rotate(f.rot);
      ctx.strokeStyle = 'rgba(40,130,230,' + a + ')'; ctx.lineWidth = Math.max(0.8, f.r / 5);
      ctx.beginPath();
      for (var i = 0; i < 3; i++) {
        var ang = i * Math.PI / 3, cx = Math.cos(ang) * f.r, cy = Math.sin(ang) * f.r;
        ctx.moveTo(-cx, -cy); ctx.lineTo(cx, cy);
      }
      ctx.stroke(); ctx.restore();
    }
    function step(dt) {
      t += dt; power += (target - power) * Math.min(1, dt * 2);
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < flakes.length; i++) {
        var f = flakes[i];
        f.y += (12 + f.r * 6) * (0.5 + power * 1.6) * dt;
        f.x += (Math.sin(t * 0.8 + f.d) * 10 + power * 14) * dt;
        f.rot += f.vr * dt * (1 + power * 2);
        if (f.y > H + 10 || f.x > W + 10) spawn(f, false);
        var a = (0.25 + f.r / 12) * (0.45 + power * 0.55);
        if (f.r > 3) star(f, a);
        else { ctx.fillStyle = 'rgba(60,150,240,' + a + ')'; ctx.beginPath(); ctx.arc(f.x, f.y, f.r * 0.7, 0, 6.28); ctx.fill(); }
      }
    }

    resize();
    for (var i = 0; i < N; i++) flakes.push(spawn({}, true));
    if (reduce) {
      target = power = opts.static ? 1 : 0.4; step(0);
    } else {
      var last = performance.now();
      window.addEventListener('resize', resize);
      (function loop(now) {
        var dt = Math.min((now - last) / 1000, 0.05); last = now;
        if (!document.hidden) step(dt);
        requestAnimationFrame(loop);
      })(last);
    }
    return { set: function (on) { target = on ? 1 : 0; if (reduce) { power = target; step(0); } } };
  }
  window.Frio = Frio;
})();

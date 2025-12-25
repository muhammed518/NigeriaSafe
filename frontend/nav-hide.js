(function () {
  let lastScroll = 0;
  const navbar = document.querySelector(".navbar");
  if (!navbar) return;
  let ticking = false;

  window.addEventListener(
    "scroll",
    function () {
      const scrollTop =
        window.pageYOffset || document.documentElement.scrollTop;
      if (!ticking) {
        window.requestAnimationFrame(() => {
          // only hide after some minimal scroll to avoid flicker at top
          if (scrollTop > lastScroll && scrollTop > 50) {
            navbar.classList.add("navbar-hidden");
          } else {
            navbar.classList.remove("navbar-hidden");
          }
          lastScroll = scrollTop <= 0 ? 0 : scrollTop;
          ticking = false;
        });
        ticking = true;
      }
    },
    { passive: true }
  );
})();

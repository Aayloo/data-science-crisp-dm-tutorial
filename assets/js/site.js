(() => {
  "use strict";

  const results = window.TUTORIAL_RESULTS || {};
  const progressBar = document.querySelector("#reading-progress-bar");
  const menuButton = document.querySelector("#menu-button");
  const scrim = document.querySelector("#mobile-scrim");
  const navLinks = Array.from(document.querySelectorAll(".nav-link"));
  const sections = Array.from(document.querySelectorAll("section[id]"));
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function readPath(object, path) {
    return path.split(".").reduce((value, key) => {
      if (value === undefined || value === null) return undefined;
      return value[key];
    }, object);
  }

  function formatValue(value, format) {
    if (value === undefined || value === null || Number.isNaN(Number(value))) {
      return "—";
    }
    if (format === "percent") {
      return `${(Number(value) * 100).toFixed(1)}%`;
    }
    if (format === "integer") {
      return new Intl.NumberFormat("en").format(Number(value));
    }
    if (format === "decimal") {
      return Number(value).toFixed(2);
    }
    return String(value);
  }

  document.querySelectorAll("[data-result]").forEach((element) => {
    const value = readPath(results, element.dataset.result);
    element.textContent = formatValue(value, element.dataset.format);
  });

  function updateProgress() {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
    progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
  }

  function closeMenu({ restoreFocus = false } = {}) {
    document.body.classList.remove("nav-open");
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.setAttribute("aria-label", "Open course navigation");
    scrim.hidden = true;
    if (restoreFocus) menuButton.focus();
  }

  function openMenu() {
    document.body.classList.add("nav-open");
    menuButton.setAttribute("aria-expanded", "true");
    menuButton.setAttribute("aria-label", "Close course navigation");
    scrim.hidden = false;
  }

  menuButton?.addEventListener("click", () => {
    const isOpen = document.body.classList.contains("nav-open");
    if (isOpen) closeMenu({ restoreFocus: true });
    else openMenu();
  });

  scrim?.addEventListener("click", () => closeMenu({ restoreFocus: true }));

  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (window.matchMedia("(max-width: 920px)").matches) {
        closeMenu();
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && document.body.classList.contains("nav-open")) {
      closeMenu({ restoreFocus: true });
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 920) closeMenu();
  });

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (!visible.length) return;
        const activeId = visible[0].target.id;
        navLinks.forEach((link) => {
          const isActive = link.getAttribute("href") === `#${activeId}`;
          link.classList.toggle("is-active", isActive);
          if (isActive) {
            link.setAttribute("aria-current", "location");
          } else {
            link.removeAttribute("aria-current");
          }
        });
      },
      {
        rootMargin: "-18% 0px -66% 0px",
        threshold: [0.01, 0.15, 0.35],
      }
    );
    sections.forEach((section) => observer.observe(section));
  }

  document.querySelectorAll(".code-block").forEach((block) => {
    const pre = block.querySelector("pre");
    if (!pre || !navigator.clipboard) return;

    const button = document.createElement("button");
    button.className = "copy-button";
    button.type = "button";
    button.textContent = "Copy";
    button.setAttribute("aria-label", "Copy this code example");
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(pre.innerText);
        button.textContent = "Copied";
        window.setTimeout(() => {
          button.textContent = "Copy";
        }, 1800);
      } catch {
        button.textContent = "Failed";
        window.setTimeout(() => {
          button.textContent = "Copy";
        }, 1800);
      }
    });
    block.append(button);
  });

  let ticking = false;
  window.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      window.requestAnimationFrame(() => {
        updateProgress();
        ticking = false;
      });
      ticking = true;
    },
    { passive: true }
  );

  updateProgress();

  if (!reduceMotion && "IntersectionObserver" in window) {
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08 }
    );
    document.querySelectorAll(".outcome-card, .case-study .figure-panel").forEach((element) => {
      element.classList.add("reveal");
      revealObserver.observe(element);
    });
  }
})();

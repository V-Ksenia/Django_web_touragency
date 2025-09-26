const preloader = document.getElementById("preloader");

function showPreloader() {
  preloader.classList.add("show");
}

function hidePreloader() {
  preloader.classList.remove("show");
}

document.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", (e) => {
    if (link.getAttribute("href").startsWith("#")) return;

    e.preventDefault();

    showPreloader();

    setTimeout(() => {
      window.location.href = link.href;
    }, Math.floor(Math.random() * (1000 - 300 + 1)) + 300); // Задержка
  });
});

window.addEventListener("load", () => {
  hidePreloader();
});

window.addEventListener("beforeunload", () => {
  showPreloader();
});

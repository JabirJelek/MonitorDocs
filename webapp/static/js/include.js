document.addEventListener("DOMContentLoaded", () => {
  const includes = document.querySelectorAll("[data-include]");
  includes.forEach(async (el) => {
    const url = "/static/" + el.getAttribute("data-include");
    try {
      const res = await fetch(url);
      if (res.ok) el.innerHTML = await res.text();
    } catch (e) {
      // silent fail
      el.innerHTML = "";
    }
  });
});

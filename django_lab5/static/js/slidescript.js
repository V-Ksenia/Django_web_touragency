let slideIndex = 1;
let autoSlideInterval;
let isHovered = false;

const loopCheckbox = document.getElementById("loop");
const autoCheckbox = document.getElementById("auto");
const stopHoverCheckbox = document.getElementById("stopHover");
const delayInput = document.getElementById("delay");

function plusSlides(n) {
  const loopEnabled = loopCheckbox.checked;
  const slides = document.getElementsByClassName("slide");

  if (!loopEnabled) {
    if (
      (slideIndex === slides.length && n > 0) ||
      (slideIndex === 1 && n < 0)
    ) {
      return;
    }
  }

  showSlides((slideIndex += n));
}

function currentSlide(n) {
  showSlides((slideIndex = n));
}

function showSlides(n) {
  const slides = document.getElementsByClassName("slide");
  const dots = document.getElementsByClassName("dot");

  if (n > slides.length) {
    slideIndex = 1;
  }
  if (n < 1) {
    slideIndex = slides.length;
  }

  for (let i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  for (let i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }

  slides[slideIndex - 1].style.display = "block";
  dots[slideIndex - 1].className += " active";
}

function startAutoSlide() {
  if (!loopCheckbox.checked) {
    loopCheckbox.checked = true;
  }
  const delay = parseInt(delayInput.value) || 5; //5с дефолт
  autoSlideInterval = setInterval(() => {
    if (!isHovered) {
      plusSlides(1);
    }
  }, delay * 1000);
}

function stopAutoSlide() {
  clearInterval(autoSlideInterval);
  loopCheckbox.checked = false;
  stopHoverCheckbox.checked = false;
}

autoCheckbox.addEventListener("change", () => {
  if (autoCheckbox.checked) {
    startAutoSlide();
  } else {
    stopAutoSlide();
  }
});

stopHoverCheckbox.addEventListener("change", () => {

  const slides = document.getElementsByClassName("slide");

  if (stopHoverCheckbox.checked) {
    for (let slide of slides) {
      slide.addEventListener("mouseenter", () => (isHovered = true));
      slide.addEventListener("mouseleave", () => (isHovered = false));
    }
  } else {
    for (let slide of slides) {
      slide.removeEventListener("mouseenter", () => (isHovered = true));
      slide.removeEventListener("mouseleave", () => (isHovered = false));
    }
    isHovered = false;
  }
});

delayInput.addEventListener("input", () => {
  if (autoCheckbox.checked) {
    stopAutoSlide();
    startAutoSlide();
  }
});

showSlides(slideIndex);

const views = document.getElementsByName("view");

const prev = document.querySelector(".prev");
const next = document.querySelector(".next");
const dots = document.querySelectorAll(".dot");

Array.from(views).forEach((radio) => {
  radio.addEventListener("change", (event) => {
    prev.style.display = next.style.display =
      event.target.checked && event.target.value == "navs" && event.target.value != "allviews" ? "none" : "block";
    dots.forEach((dot) => {
      dot.style.display =
        event.target.checked && event.target.value == "pags"
          ? "none"
          : "inline-block";
    });
  });
});

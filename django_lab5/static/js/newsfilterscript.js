
const styleToggle = document.getElementById("styleToggle");
const controlPanel = document.getElementById("controlPanel");
const fontSizeSlider = document.getElementById("fontSizeSlider");
const textColorPicker = document.getElementById("textColorPicker");
const backgroundColorPicker = document.getElementById("backgroundColorPicker");

const news = document.querySelector(".news-details");

styleToggle.addEventListener("change", () => {
    controlPanel.style.display = styleToggle.checked ? "block" : "none";
});


fontSizeSlider.addEventListener("input", () => {
    news.style.fontSize = fontSizeSlider.value + "px";
});


textColorPicker.addEventListener("input", () => {
    news.style.color = textColorPicker.value;
});


backgroundColorPicker.addEventListener("input", () => {
    news.style.backgroundColor = backgroundColorPicker.value;
});

const itemsPerPage = 4;
let currentPage = 1;

function displayItems(page) {
  const catalog = document.getElementById("tour-wrapper");
  catalog.innerHTML = "";

  const startIndex = (page - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;

  const itemsToDisplay = tours.slice(startIndex, endIndex);
  itemsToDisplay.forEach((tours) => {
    const tourDiv = document.createElement("a");
    tourDiv.classList.add("tour-container");
    tourDiv.href = `${baseUrl}${tours.id}`;
    tourDiv.style.backgroundImage = `url('${tours.photo}')`;
    tourDiv.innerHTML = `
            <span style="font-weight: bold; font-size: 30px;">${tours.name}</span>
            <hr>
            <p>Visit a ${tours.country}</p>
            <p>Stay in a ${tours.hotel} hotel with ${tours.hotel_stars}★</p>
            <p>Duration is ${tours.duration_weeks} weeks</p>
            <p style="position: relative; top: 150px; font-size: larger;">For <span style="font-weight: bold; font-size: 20px;">${tours.price}$</span> / person</p>
        </a>
            `;
    catalog.appendChild(tourDiv);
  });

  displayPagination(tours.length, page);
}

function displayPagination(totalItems, currentPage) {
  const pagination = document.getElementById("pagination");
  pagination.innerHTML = "";

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  for (let i = 1; i <= totalPages; i++) {
    const pageButton = document.createElement("button");
    pageButton.textContent = i;
    pageButton.classList.add("page-button");
    if (i === currentPage) {
      pageButton.classList.add("active");
    }
    pageButton.addEventListener("click", () => {
      displayItems(i);
    });
    pagination.appendChild(pageButton);
  }
}

displayItems(currentPage);

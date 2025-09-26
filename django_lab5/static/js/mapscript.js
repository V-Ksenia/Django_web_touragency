document.addEventListener("DOMContentLoaded", () => {
   
    const map = L.map('map')
    
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    async function getCoordinates(countryName) {
        const url = `https://nominatim.openstreetmap.org/search?country=${encodeURIComponent(countryName)}&format=json&limit=1`;
        try {
            const response = await fetch(url);
            const data = await response.json();
            if (data && data.length > 0) {
                const { lat, lon } = data[0];
                return { lat: parseFloat(lat), lon: parseFloat(lon) };
            } else {
                console.error(`Coordinates for "${countryName}" not found.`);
                return null;
            }
        } catch (error) {
            console.error(`Error fetching coordinates for "${countryName}":`, error);
            return null;
        }
    }


    tours.forEach(async (tour, index) => {
        const coordinates = await getCoordinates(tour.country);
        if (coordinates) {
            if (index === 0) {
                map.setView([coordinates.lat, coordinates.lon], 5);
            }

            const marker = L.marker([coordinates.lat, coordinates.lon]).addTo(map);
            marker.bindPopup(`
                <b>${tour.hotel}</b><br>
                ${tour.country}
            `);
        }
    });
});

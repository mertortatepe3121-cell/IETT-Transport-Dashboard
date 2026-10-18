document.addEventListener("DOMContentLoaded", function () {

    /* =========================
       TARİH VE SAAT
    ========================= */

    function updateDateTime() {

        const now = new Date();

        const day = String(now.getDate()).padStart(2, "0");
        const month = String(now.getMonth() + 1).padStart(2, "0");
        const year = now.getFullYear();

        const hours = String(now.getHours()).padStart(2, "0");
        const minutes = String(now.getMinutes()).padStart(2, "0");
        const seconds = String(now.getSeconds()).padStart(2, "0");

        const dateElement = document.getElementById("currentDate");
        const timeElement = document.getElementById("currentTime");

        if (dateElement) {
            dateElement.textContent =
                `${day}.${month}.${year}`;
        }

        if (timeElement) {
            timeElement.textContent = 
    `${hours}:${minutes}:${seconds}`;
        }
    }

    updateDateTime();

    setInterval(updateDateTime, 1000);


    /* =========================
       SIDEBAR AÇ / KAPAT
    ========================= */

    const sidebarToggle =
        document.getElementById("sidebarToggle");

    const sidebar =
        document.querySelector(".sidebar");

    if (sidebarToggle && sidebar) {

        sidebarToggle.addEventListener("click", function () {

            sidebar.classList.toggle("open");

        });
    }


    /* =========================
       MOBİLDE MENÜDEN SONRA KAPAT
    ========================= */

    const menuItems =
        document.querySelectorAll(".menu-item");

    menuItems.forEach(function (item) {

        item.addEventListener("click", function () {

            if (window.innerWidth <= 800) {
                sidebar.classList.remove("open");
            }

        });

    });

});
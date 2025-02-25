document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.querySelector(".navbar");
    const navbarToggler = document.querySelector(".navbar-toggler");
    const navbarCollapse = document.querySelector(".navbar-collapse");

    // Animasi navbar berubah warna saat scroll
    window.addEventListener("scroll", function () {
        if (window.scrollY > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    });

    // Menangani tampilan background saat tombol burger ditekan
    navbarToggler.addEventListener("click", function () {
        if (!navbarCollapse.classList.contains("show")) {
            navbar.classList.add("scrolled"); // Tambahkan background meskipun belum di-scroll
        } else {
            if (window.scrollY < 50) {
                navbar.classList.remove("scrolled"); // Hapus background jika belum di-scroll
            }
        }
    });

    // Mengatur tahun otomatis di footer
    document.getElementById("current-year").textContent = new Date().getFullYear();

    // Menghilangkan alert otomatis setelah 3 detik
    setTimeout(function() {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(function(alert) {
            alert.style.transition = "opacity 0.5s";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        });
    }, 3000);
});

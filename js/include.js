function includeHTML(id, file) {
    fetch(file)
        .then(res => res.text())
        .then(html => {
            document.getElementById(id).innerHTML = html;

            // Highlight current page
            if (id === "header") {
                let currentPage = window.location.pathname.split("/").pop();

                if (currentPage === "") {
                    currentPage = "index.html";
                }

                document.querySelectorAll("#header .nav-link").forEach(link => {
                    let linkPage = link.getAttribute("href");

                    if (linkPage === currentPage) {
                        link.classList.add("active");
                    }
                });
            }
        });
}

includeHTML("header", "header.html");
includeHTML("footer", "footer.html");
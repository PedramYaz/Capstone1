let li = document.querySelectorAll("li");
let info = document.querySelectorAll(".info");

for (let i = 0; i < li.length; i++) {
  li[i].addEventListener("click", function () {
    info[i].classList.toggle("info");
  });
}

// document.body.addEventListener("click", function (e) {
//   if (e.target.id === "submit-button") {
//     e.preventDefault();
//     console.log(e.target.classList[0]);
//   }
// });

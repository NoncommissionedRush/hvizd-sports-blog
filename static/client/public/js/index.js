const Confirm = {
  open(options) {
    options = Object.assign(
      {},
      {
        message: "",
        yesText: "Yes",
        noText: "No",
        onYes: function () {
          console.log("clicked yes");
          return true;
        },
        onNo: function () {
          console.log("clicked no");
          return false;
        },
      },
      options
***REMOVED***;

    html = `
            <div class="confirm">
                <div class="confirm-window">
                    <p class="my-1">${options.message}</p>
                    <button class="btn btn-small btn-white btn-yes">${options.yesText}</button>
                    <button class="btn btn-small btn-delete btn-no">${options.noText}</button>
                </div>
            </div>
        `;

    const template = document.createElement("template");
    template.innerHTML = html;

    const confirmElement = template.content.querySelector(".confirm");
    const btnYes = template.content.querySelector(".btn-yes");
    const btnNo = template.content.querySelector(".btn-no");

    confirmElement.addEventListener("click", (e) => {
      if (e.target === confirmElement) {
        options.onNo();
        this._close(confirmElement);
      }
    });

    btnYes.addEventListener("click", () => {
      options.onYes();
      this._close(confirmElement);
    });

    btnNo.addEventListener("click", () => {
      options.onNo();
      this._close(confirmElement);
    });

    document.body.appendChild(template.content);
  },

  _close(confirmElement) {
    confirmElement.classList.add("confirm-close");
    confirmElement.addEventListener("animationend", () => {
      document.body.removeChild(confirmElement);
    });
  },
};

btnDeletePost = document.querySelector("#btn-delete-post")
if (btnDeletePost){
    btnDeletePost.addEventListener("click", (e) => {
      e.preventDefault()
      Confirm.open({
          message: "Are you sure you want to delete the post?",
          onYes: () => {
              window.location.href = e.target.href;
          }
      })
    });    
}

btnDeleteProfile = document.querySelector("#btn-delete-profile")
if (btnDeleteProfile){
    btnDeleteProfile.addEventListener("click", (e) => {
      e.preventDefault();
      Confirm.open({
        message: "Are you sure you want to delete the profile?",
        onYes: () => {
          window.location.href = e.target.href;
        },
      });
    });
}

btnDeleteComment = document.querySelector("#btn-delete-comment")
if (btnDeleteComment){
    btnDeleteComment.addEventListener("click", (e) => {
      e.preventDefault();
      Confirm.open({
        message: "Are you sure you want to delete the comment?",
        onYes: () => {
          window.location.href = e.target.href;
        },
      });
    });
}

const Confirm = {

  types: {
    YESNO: "confirm",
    OK: "ok"
  },

  open(options) {
    options = Object.assign(
      {},
      {
        type: this.types.YESNO,
        message: "",
        yesText: "Áno",
        noText: "Nie",
        onYes: function () {},
        onNo: function () {},
      },
      options
***REMOVED***;

    if (options.type == this.types.YESNO){
      console.log('funguje')
      html = `
      <div class="confirm">
        <div class="confirm-window">
            <p class="my-1">${options.message}</p>
            <button class="btn btn-small btn-white btn-yes">${options.yesText}</button>
            <button class="btn btn-small btn-delete btn-no">${options.noText}</button>
        </div>
      </div>
    `;
    } else if (options.type == this.types.OK) {
      html = `
      <div class="confirm">
          <div class="confirm-window">
              <p class="my-1">${options.message}</p>
              <button class="btn btn-small btn-white btn-yes">${options.yesText}</button>
          </div>
      </div>
    `;
    }


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

    if(btnNo){
      btnNo.addEventListener("click", () => {
        options.onNo();
        this._close(confirmElement);
      });
    }
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
          type: Confirm.types.YESNO,
          message: "Určite chcete zmazať článok?",
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
        type: Confirm.types.YESNO,
        message: "Určite chcete zmazať svoj profil?",
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
        type: Confirm.types.YESNO,
        message: "Určite chcete zmazať komentár?",
        onYes: () => {
          window.location.href = e.target.href;
        },
      });
    });
}

btnForgotPassword = document.querySelector("#btn-forgot-password")
if (btnForgotPassword) {
  btnForgotPassword.addEventListener("click", (e) => {
    e.preventDefault()
    Confirm.open({
      type: Confirm.types.OK,
      message: "Link na zmenu hesla bol odoslaný na váš email",
      yesText: "Ok",
      onYes: () => {
        form = document.querySelector("#request-password-reset-form")
        form.submit()
        console.log(form)
        // window.location.href = e.target.getAttribute("data-href")
      }
    });
  })
}
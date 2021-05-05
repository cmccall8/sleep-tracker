var register_pg = document.querySelector(".registration");
var log_in_pg = document.querySelector(".log_in");
var home_pg = document.querySelector("#home_page");
var register_btn = document.querySelector("#register_btn");
var switch_to_login = document.querySelector("#switch_to_login");
var switch_to_reg = document.querySelector("#switch_to_reg");
var log_in_btn = document.querySelector("#log_in_btn");
var record_list_btn = document.querySelector("#sleep_record");
var record_btn = document.querySelector("#record_btn");
var change_btn = document.querySelector("#change_btn");
var submit = document.querySelector("#submit_record");
var slider = document.querySelector("#hours_slider");
var value_output = document.querySelector("#value_output");
var title_txt = document.querySelector(".title_txt");

//why null???
var sleeplogs = null;
var editId = null;

register_btn.onclick = function () {
  var login_error_msg = document.querySelector(".login_error_msg");
  login_error_msg.innerHTML = " ";

  var fname_field = document.querySelector("#fname_field");
  var fname = fname_field.value;
  console.log("fname: ", fname);

  var lname_field = document.querySelector("#lname_field");
  var lname = lname_field.value;
  console.log("lname: ", lname);

  var email_field = document.querySelector("#email_field");
  var email = email_field.value;
  console.log("email: ", email);

  var password_field = document.querySelector("#password_field");
  var password = password_field.value;
  console.log("password: ", password);

  var data = "fname=" + encodeURIComponent(fname)
  + "&" + "lname=" + encodeURIComponent(lname)
  + "&" + "email=" + encodeURIComponent(email)
  + "&" + "password=" + encodeURIComponent(password);

  fetch("http://localhost:8080/users", {
    method: "POST",
    body: data,
    credentials: "include",
    headers: {
      "Content-Type":"application/x-www-form-urlencoded"
    }
  }).then(function (response) {
    if (response.status == 201) {
      register_pg.style.display = "none";
      log_in_pg.style.display = "block";
      home_pg.style.display = "none";
      title_txt.innerHTML = "Log-In to Sleep Tracker"
    } else if (response.status == 422) {
      var reg_error_msg = document.querySelector(".reg_error_msg");
      reg_error_msg.innerHTML = "The email you entered is already<br> in use. Please try again.";
    }
  });
};

switch_to_login.onclick = function () {
  register_pg.style.display = "none";
  log_in_pg.style.display = "block";
  title_txt.innerHTML = "Log-In to Sleep Tracker"
};

log_in_btn.onclick = function () {
  var user_email_input = document.querySelector("#user_email");
  var email = user_email_input.value;
  var user_password_input = document.querySelector("#user_password");
  var password = user_password_input.value;

  var data = "email=" + encodeURIComponent(email)
  + "&" + "password=" + encodeURIComponent(password);

  fetch("http://localhost:8080/sessions", {
    method: "POST",
    body: data,
    credentials: "include",
    headers: {
      "Content-Type":"application/x-www-form-urlencoded"
    }
  }).then(function (response) {
    loadSleepLog();
  });
};

switch_to_reg.onclick = function () {
  log_in_pg.style.display = "none";
  register_pg.style.display = "block";
};

record_btn.onclick = function () {
  var section = document.querySelector("#record_section");
  var hidden_section = document.querySelector("#sleep_record_list");
  hidden_section.style.display = "none";
  section.style.display = "block";
  change_btn.style.display = "none";
  submit.style.display = "block";
};

record_list_btn.onclick = function () {
  var section = document.querySelector("#sleep_record_list");
  var hidden_section = document.querySelector("#record_section");
  hidden_section.style.display = "none";
  section.style.display = "block";
  loadSleepLog();
};

slider.oninput = function () {
  value_output.innerHTML = this.value;
};

submit.onclick = function () {
  var day_input = document.querySelector("#day_select");
  var day = day_input.value;
  console.log("You chose:", day);
  var hours_input = document.querySelector("#hours_slider");
  var hours = hours_input.value;
  console.log("You chose:", hours);
  phone = checkPhoneRadio();
  console.log("You chose:", phone);
  late = checkLateRadio();
  console.log("You chose:", late);
  mood = checkMoodRadio();
  console.log("you chose:", mood);

  var data = "day=" + encodeURIComponent(day)
  + "&" + "hours=" + encodeURIComponent(hours)
  + "&" + "phone=" + encodeURIComponent(phone)
  + "&" + "late=" + encodeURIComponent(late)
  + "&" + "mood=" + encodeURIComponent(mood);

  fetch("http://localhost:8080/sleeplogs", {
    method: "POST",
    credentials: "include",
    body: data,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  }).then(function (response) {
    loadSleepLog();
    var section = document.querySelector("#sleep_record_list");
    var hidden_section = document.querySelector("#record_section");
    hidden_section.style.display = "none";
    section.style.display = "block";
  });
};

function loadSleepLog () {
  fetch("http://localhost:8080/sleeplogs", {
    credentials: "include"
  }).then(function(response){
    if (response.status == 200) {
      register_pg.style.display = "none";
      log_in_pg.style.display = "none";
      home_pg.style.display = "block";
      title_txt.innerHTML = "Welcome to Sleep Tracker"
    } else if (response.status == 401) {
      home_pg.style.display == "none";
      register_pg.style.display == "none";
      log_in_pg.style.display == "block";
      title_txt.innerHTML = "Log-In to Sleep Tracker"
      var login_error_msg = document.querySelector(".login_error_msg");
      login_error_msg.innerHTML = "Login failed. Are you sure you <br> used the right email & password?";
      return
    }
    response.json().then(function (listFromServer) {
      var sleep_record_list = document.querySelector("#sleep_record_list");
      sleep_record_list.innerHTML = "";
      listFromServer.forEach(function (item) {
        console.log("one log:", item);
        var listItem = document.createElement("li");
        listItem.innerHTML = item.day + "</br> you slept: "
        + item.hours + " hours </br>"
        + " Phone use: " + item.phone
        + "</br> Late: " + item.late
        + "</br> Mood: " + item.mood + "</br>";

        var del_btn = document.createElement("button");
        del_btn.innerHTML = "Delete";
        del_btn.onclick = function () {
          console.log("You chose me: ", item)
          if (confirm ("Are you sure you want to delete " + item.day + " ?")) {
            deleteLogOnServer(item.id);
          };
        };

        var edit_btn = document.createElement("button");
        edit_btn.innerHTML = "Edit";
        edit_btn.onclick = function () {
          console.log("You chose me:", item)
          editId = item.id;
          // show the edit form
          var section = document.querySelector("#record_section");
          var hidden_section = document.querySelector("#sleep_record_list");
          hidden_section.style.display = "none";
          section.style.display = "block";
          // show the "save" button (hide the "record" button)
          submit.style.display = "none";
          change_btn.style.display = "block";
          // pre-fill the form with data from item
          var day_input = document.querySelector("#day_select");
           day_input.value = item.day;
           value_output.innerHTML = item.hours;
           slider.value = item.hours;

           var phone1 = document.querySelector("#phone_select1");
           var phone2 = document.querySelector("#phone_select2");

           if (item.phone == "yes") {
             phone1.checked = true;
          }
          else {
            phone2.checked = true;
          }

          var late1 = document.querySelector("#late_select1");
          var late2 = document.querySelector("#late_select2");
          if (item.late == "yes") {
            late1.checked = true;
         }
         else {
           late2.checked = true;
         };

         var mood1 = document.querySelector("#mood_select1");
         var mood2 = document.querySelector("#mood_select2");
         var mood3 = document.querySelector("#mood_select3");
         if (item.mood == "good") {
           mood1.checked = true;
         } else if (item.mood == "fair") {
           mood2.checked = true;
         } else if (item.mood == "bad") {
           mood3.checked = true;
         }
         };

        change_btn.onclick = function () {
          updateSleepLogOnServer(editId);
        };
        listItem.appendChild(edit_btn);
        listItem.appendChild(del_btn);
        sleep_record_list.appendChild(listItem);
      });
    });
  });
};

function deleteLogOnServer(log_id) {
  fetch("http://localhost:8080/sleeplogs/" + log_id, {
    method: "DELETE",
    credentials: "include"
  }).then(function (response) {
    loadSleepLog();
  });
};

function updateSleepLogOnServer(log_id) {
  var day_input = document.querySelector("#day_select");
  var day = day_input.value;
  console.log("You chose:", day);
  var hours_input = document.querySelector("#hours_slider");
  var hours = hours_input.value;
  console.log("You chose:", hours);
  phone = checkPhoneRadio();
  console.log("You chose:", phone);
  late = checkLateRadio();
  console.log("You chose:", late);
  mood = checkMoodRadio();
  console.log("you chose:", mood);

  var data = "day=" + encodeURIComponent(day)
  + "&" + "hours=" + encodeURIComponent(hours)
  + "&" + "phone=" + encodeURIComponent(phone)
  + "&" + "late=" + encodeURIComponent(late)
  + "&" + "mood=" + encodeURIComponent(mood);

  fetch("http://localhost:8080/sleeplogs/" + log_id, {
    method: "PUT",
    credentials: "include",
    body: data,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  }).then(function (response) {
    loadSleepLog();
    var section = document.querySelector("#sleep_record_list");
    var hidden_section = document.querySelector("#record_section");
    hidden_section.style.display = "none";
    section.style.display = "block";
  });
};

function checkPhoneRadio() {
  var phone1 = document.querySelector("#phone_select1");
  var phone2 = document.querySelector("#phone_select2");
  if (phone1.checked) {
    phone = phone1.value;
  }
  else {
    phone = phone2.value;
  }
  return phone
};

function checkLateRadio() {
  var late1 = document.querySelector("#late_select1");
  var late2 = document.querySelector("#late_select2");
  if (late1.checked) {
    late = late1.value;
  }
  else {
    late = late2.value;
  }
  return late
};

function checkMoodRadio() {
  var mood1 = document.querySelector("#mood_select1");
  var mood2 = document.querySelector("#mood_select2");
  var mood3 = document.querySelector("#mood_select3");
  if (mood1.checked) {
    mood = mood1.value;
  } else if (mood2.checked) {
    mood = mood2.value;
  }
  else {
    mood = mood3.value;
  }
  return mood
};
loadSleepLog();

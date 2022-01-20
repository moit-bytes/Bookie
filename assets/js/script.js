const toggleButton = document.getElementsByClassName('toggle-button')[0]
const navbarLinks = document.getElementsByClassName('navbar-links')[0]

toggleButton.addEventListener('click', () => {
  navbarLinks.classList.toggle('active')
})

//Text Autocomplete

consoleText(['Need to borrow a book?', 'Lend your books easily', 'Lookup for books'], 'text', ['#20F304 ', '#F8A604 ', '#F8068B ']);

function consoleText(words, id, colors) {
  if (colors === undefined) colors = ['#fff'];
  var visible = true;
  var con = document.getElementById('console');
  var letterCount = 1;
  var x = 1;
  var waiting = false;
  var target = document.getElementById(id)
  target.setAttribute('style', 'color:' + colors[0])
  window.setInterval(function () {

    if (letterCount === 0 && waiting === false) {
      waiting = true;
      target.innerHTML = words[0].substring(0, letterCount)
      window.setTimeout(function () {
        var usedColor = colors.shift();
        colors.push(usedColor);
        var usedWord = words.shift();
        words.push(usedWord);
        x = 1;
        target.setAttribute('style', 'color:' + colors[0])
        letterCount += x;
        waiting = false;
      }, 1000)
    } else if (letterCount === words[0].length + 1 && waiting === false) {
      waiting = true;
      window.setTimeout(function () {
        x = -1;
        letterCount += x;
        waiting = false;
      }, 1000)
    } else if (waiting === false) {
      target.innerHTML = words[0].substring(0, letterCount)
      letterCount += x;
    }
  }, 120)
  window.setInterval(function () {
    if (visible === true) {
      con.className = 'console-underscore hidden'
      visible = false;

    } else {
      con.className = 'console-underscore'

      visible = true;
    }
  }, 400)
}


// Search books using book API
const searchBookButton = document.getElementById('searchBooks');
const book_id = document.getElementById('book_name');
const author_id = document.getElementById('author_name');
const book_search_status = document.getElementById('book_search_status');
const modal_open = document.getElementById('open_modal_button');

searchBookButton.addEventListener('click', () => {
  var book_title = book_id.value;
  var author_name = author_id.value;
  //console.log("Hello " + book_title);
  if (book_name === "" && author_name === "") {
    alert("Please enter book name or author name");
  }
  else if (author_name == "") {
    callAPi(book_title);
  }
  else {
    callAPi(author_name);
  }

});



function callAPi(name) {
  let request = new XMLHttpRequest();
  request.open("GET", "https://www.googleapis.com/books/v1/volumes?q=" + name);
  request.send();
  request.onload = () => {
    console.log(request);
    if (request.status === 200) {
      // by default the response comes in the string format, we need to parse the data into JSON
      clearModal();
      var json_data = JSON.parse(request.response);
      var json_array = json_data.items;
      var n = json_data.totalItems;
      console.log("Value " + n);
      if (n == 0) {
        //Books not found
        book_search_status.innerText = "Ughhh :(  Your searched book is not found. We tried hard to find your book but we couldn't find it";

        modal_open.click();
      }
      else {
        book_search_status.innerText = "Hola :)  Your searched book is found. Go below and look out for the book.";

        modal_open.click();

        var array_size = json_array.length;
        // if (array_size > 3) {
        //   array_size = 3;
        // }
        for (var i = 0; i < array_size; i++) {
          var each_object = json_array[i];
          var volumeInfo = each_object.volumeInfo;
          var title = volumeInfo.title;
          var authors_array = volumeInfo.authors;
          var img = volumeInfo.imageLinks;
          var img_url = "";
          if (img == undefined) {
            img_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQMMwS7fqFrpMTwZOFzSS11bvIsUmFSu5TVI1WvHmuLb_Zr_DiRDabQPGOxLOY3vhEZBpk&usqp=CAU";
          }
          else {
            img_url = img.thumbnail;
          }
          console.log(title);
          console.log(authors_array);
          console.log(img_url);
          addToModal(title, authors_array, img_url);
        }
      }

    } else {
      console.log(`error ${request.status} ${request.statusText}`);
    }
  };


  function addToModal(title, authors_array, img_url) {
    let container = document.querySelector('.book_res');
    var authors = ""
    for (var j = 0; j < authors_array.length; j++) {
      authors = authors_array[j] + " | ";
    }

    let myDiv = document.createElement("div");

    myDiv.innerHTML = '<div class="card each_book_crd"> <h5>' + title + '</h5> <h6>By ' + authors + ' </h6> <img class="book-search-img" src=" ' + img_url + ' " alt=""> </div>';
    container.appendChild(myDiv);
  }

  function clearModal() {
    var e = document.querySelector(".book_res");

    var child = e.lastElementChild;
    while (child) {
      e.removeChild(child);
      child = e.lastElementChild;
    }
  }
}



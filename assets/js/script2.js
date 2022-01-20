const toggleButton = document.getElementsByClassName('toggle-button')[0]
const navbarLinks = document.getElementsByClassName('navbar-links')[0]

toggleButton.addEventListener('click', () => {
  navbarLinks.classList.toggle('active')
})

//POST Data to DynamoDB

var lendBookBtn = document.getElementById('lendBook');
var lenderName = document.getElementById('lenderName');
var lenderBookName = document.getElementById('lenderBookName');
var lenderAuthorName = document.getElementById('lenderAuthorName');
var lenderAddress = document.getElementById('lenderAddress');
var lenderPhone = document.getElementById('lenderPhone');


lendBookBtn.addEventListener('click', ()=>
{
  console.log("Hello")
  var createdAt = getIDAsDateTime();

  var lender_name = lenderName.value;
  var book_name = lenderBookName.value;
  var author_name = lenderAuthorName.value;
  var lender_add = lenderAddress.value;
  var lender_phone = lenderPhone.value;
  
  if(lender_name == "" || book_name == "" || author_name == "" || lender_add == ""
  || lender_phone == "")
  {
    window.alert("Please ensure that all your details are appropriate!")
  }
  else
  {
      postDataToDB(createdAt, book_name, author_name,
        lender_name, lender_add, lender_phone);

        lenderName.value = "";
        lenderBookName.value ="";
        lenderAuthorName.value = "";
        lenderAddress.value ="";
        lenderPhone.value = "";
  }

});

function getIDAsDateTime() {
  var today = new Date();
  var date = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate();
  var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
  var dateTime = date + ' ' + time;

  return dateTime;
}

function postDataToDB(createdAt, bookName, authorName, lenderName,
  lenderAddress, lenderPhone) 
{

  var myHeaders = new Headers();
  myHeaders.append("Content-Type", "text/plain");

  var raw = "{\n  \"createdAt\":\""+createdAt+"\",\n  \"bookName\":\""+bookName+"\",\n  \"bookAuthor\":\""+authorName+"\",\n  \"lenderName\":\""+lenderName+"\",\n  \"lenderAddress\":\""+lenderAddress+"\",\n  \"lenderPhone\":\""+lenderPhone+"\"\n}";

// var raw = "{\n  \"createdAt\":\""+createdAt+"\",\n  \"bookName\":\"Test Book\",\n  \"bookAuthor\":\"Test Author\",\n  \"lenderName\":\"Test Name\",\n  \"lenderAddress\":\"Test Address\",\n  \"lenderPhone\":\"Test Phone\"\n}";

  var requestOptions = {
    method: 'POST',
    headers: myHeaders,
    body: raw,
    redirect: 'follow'
  };

  fetch("https://cahts53sz7.execute-api.us-east-1.amazonaws.com/testProd/lendbook", requestOptions)
    .then(response => response.text())
    .then(result => alert("Hurray!! Your book is successfully kept for lending. If someone needs the book they will contact you."))
    .catch(error => console.log('error', error));
}

// {
//   "createdAt":"2020",
//   "bookName":"Test Book",
//   "bookAuthor":"Test Author",
//   "lenderName":"Test Name",
//   "lenderAddress":"Test Address",
//   "lenderPhone":"Test Phone"
// }


// [
//   {
//     "lenderAddress": {
//       "S": "Test Address"
//     },
//     "bookAuthor": {
//       "S": "Test Author"
//     },
//     "bookName": {
//       "S": "Test Book"
//     },
//     "createdAt": {
//       "S": "300"
//     },
//     "lenderPhone": {
//       "S": "Test Phone"
//     },
//     "lenderName": {
//       "S": "Test Name"
//     }
//   },
//   {
//     "lenderAddress": {
//       "S": "Test Address"
//     },
//     "bookAuthor": {
//       "S": "Test Author"
//     },
//     "bookName": {
//       "S": "Test Book"
//     },
//     "createdAt": {
//       "S": "2020"
//     },
//     "lenderPhone": {
//       "S": "Test Phone"
//     },
//     "lenderName": {
//       "S": "Test Name"
//     }
//   }
// ]


//Get Data From Bookie API


// var requestOptions = {
//   method: 'GET',
//   redirect: 'follow'
// };

// fetch("https://cahts53sz7.execute-api.us-east-1.amazonaws.com/testProd/getbooks", requestOptions)
//   .then(response => response.text())
//   .then(result => filterData(result))
//   .catch(error => console.log('error', error));

// function filterData(result) {
//   var josnArr = JSON.parse(result);
//   console.log(josnArr[0]["bookAuthor"]["S"])
// }
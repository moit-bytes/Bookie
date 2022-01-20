const toggleButton = document.getElementsByClassName('toggle-button')[0]
const navbarLinks = document.getElementsByClassName('navbar-links')[0]

toggleButton.addEventListener('click', () => {
    navbarLinks.classList.toggle('active')
})


//Get Data From Bookie API


var requestOptions = {
    method: 'GET',
    redirect: 'follow'
};

fetch("https://cahts53sz7.execute-api.us-east-1.amazonaws.com/testProd/getbooks", requestOptions)
    .then(response => response.text())
    .then(result => filterData(result))
    .catch(error => console.log('error', error));

function filterData(result) {
    var josnArr = JSON.parse(result);
    //console.log()
    for (var i = 0; i < josnArr.length; i++) {
        var book_name = josnArr[i]["bookName"]["S"];
        var author_name = josnArr[i]["bookAuthor"]["S"];
        var lender_name = josnArr[i]["lenderName"]["S"];
        var lender_phone = josnArr[i]["lenderPhone"]["S"];
        var lender_add = josnArr[i]["lenderAddress"]["S"];
        insRow(book_name, author_name, lender_name, lender_phone, lender_add);
    }

    //document.getElementById('bookTable').rows[1].style["display"] = "none";

    $(document).ready(function () {
        $('#bookTable').DataTable();
    });

}

function insRow(book_name, author_name, lender_name, lender_phone,
    lender_add) {
    var x = document.getElementById('bookTable');
    var y = document.getElementById('tableBody');
    // deep clone the targeted row
    //var new_row = x.rows[1].cloneNode(true);
    // get the total number of rows
    var len = x.rows.length;
    // new_row.cells[0].innerHTML = len+1;
    // new_row.cells[1].innerHTML = book_name;
    // new_row.cells[2].innerHTML = author_name;
    // new_row.cells[3].innerHTML = lender_name;
    // new_row.cells[4].innerHTML = lender_phone;
    // new_row.cells[5].innerHTML = lender_add;
    // var len = x.rows.length;

    var template = `<tr class="titem">
                        <td>${len}</td>
                        <td>${book_name}</td>
                        <td>${author_name}</td>
                        <td>${lender_name}</td>
                        <td>${lender_phone}</td>
                        <td>${lender_add}</td>
                    </tr>`;

    y.innerHTML += template;
}
const toggleButton = document.getElementsByClassName('toggle-button')[0]
const navbarLinks = document.getElementsByClassName('navbar-links')[0]

toggleButton.addEventListener('click', () => {
    navbarLinks.classList.toggle('active')
})

const sendContact = document.getElementById('sendContact');

sendContact.addEventListener('click', ()=>
{
    if(document.getElementById('your_name').value == "" || document.getElementById('your_email').value == "")
    {
        alert("Oops!! Please enter your details correctly");
    }
    else
    {
        alert("Thanks!! For connecting to us. Soon I will get back to you.");
        document.getElementById('your_name').value = null;
        document.getElementById('your_email').value = null;
    }
    
})
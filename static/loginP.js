function verifyIdentity(){

};
function createAccount() {
    const usrnm = document.getElementById("username").value;
    const passwrd = document.getElementById("password").value;
    const isTeacher = document.getElementById("is_teacher").checked;

    const data = { "username": usrnm, "password": passwrd, "is_teacher": isTeacher };

    fetch('http://127.0.0.1:5000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => console.log('Success:', data))
    .catch(error => console.error('Error:', error));
}

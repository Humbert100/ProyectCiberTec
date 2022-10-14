function process_login_info(){
    var continue_next = true;
    switch(true){
        case(!$("#user_email").val()):
            alert("Favor de ingresar su correo");
            continue_next = false;
        break;
        case(!$("#user_pwd").val()):
            alert("Favor de ingresar su contraseña");
            continue_next = false;
        break;
    }
    if(continue_next == false){
        console.log("not registered");
        return;
    }

    let user_login_data = {'email'  :   $("#user_email").val(),
                           'pwd'    :   $("#user_pwd").val()};
    console.log(user_login_data)

    $.ajax({
        type        :   "PUT",
        url         :   "/user/login",
        data        :   JSON.stringify(user_login_data),
        contentType :   'application/json',
        dataType    :   "json",

        success: function (data){
            if (data.authorized == true)    {
                location.replace("/homepage");
            }
            else if(data.authorized ==  "exist"){
                alert("EL usuario no existe, favor de registrarse");
            }
            else if(data.authorized == "available"){
                alert("EL usuario no verificado, favor de consultar su correo");
            }
            else if(data.authorized == "pwd"){
                alert("contraseña incorrecta, favor de volver a colocarla");
            }
        }
    })

}

function process_sign_in_info(){

    var emailregex = /^[a-zA-z0-9_.+-]+@[a-zA-z0-9-]+\.[a-zA-z0-9-.]+$/
    var pwdmin = /^.{8,}$/
    var regextest = emailregex.test($("#user_email").val());
    var regexpwd  = pwdmin.test($("user_pwd").val());
    var continue_next = true;
    switch(true){
        case(!$("#user_name").val()):
            alert("Favor de ingresar su nombre");
            continue_next = false;
        break;
        case(!$("#user_lastname").val()):
            alert("Favor de ingresar su o sus apellidos");
            continue_next = false;
        break;
        case(!$("#user_email").val()):
            alert("Favor de ingresar su correo");
            continue_next = false;
        break;
        case(regextest == false):
            alert("No es un correo valido, favor de colocar un correo que si lo sea")
            continue_next = false;
        break;
        case(!$("#user_pwd").val()):
            console.log(regextest)
            alert("Favor de ingresar su contraseña");
            continue_next = false;
        break;
        case(regexpwd == false):
            alert("La contraseña debe tener min. 8 caracteres")
        case(!$("#user_pwd_confirmation").val()):
            alert("Favor de ingresar su contraseña");
            continue_next = false;
        break;
        case($("#user_pwd_confirmation").val() != $("#user_pwd").val()):
            alert("Las contraseñas no coinciden, favor de verificar");
            continue_next = false;
        break;
        case(document.getElementById("checkbox").value == true):
            alert("Porfavor, acepta los terminos y condiciones")
            continue_next = false
        break;
    }
    if(continue_next == false){
        console.log("usuario invalido para registrar");
        return;
    }
    

    let name = $("#user_name").val()
    let lastname = $("#user_lastname").val()
    let fullname = name + " " +lastname
    let user_sign_up_data = {   'name'      :   fullname,
                                'email'     :   $("#user_email").val(),
                                'pwd'       :   $("#user_pwd").val()};
    console.log(user_sign_up_data)

    $.ajax({
        url         :   "/user/create",
        type        :   "POST",
        data        :   JSON.stringify(user_sign_up_data),
        contentType :   'application/json',
        dataType    :   "json",
    
        success: function (data)   {
            if (data.register == 1){
                alert("usuario registrado")
                console.log("Se logro")
                location.replace("/iniciosesion")
            }
            if (data.register == "exist"){
                alert("Correo ya registrado, favor de probar con otro")
            }
        }

    })
}